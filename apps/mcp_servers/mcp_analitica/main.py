import os
import json
import logging
from collections import Counter, defaultdict
from fastmcp import FastMCP

mcp = FastMCP("mcp-analitica")
logger = logging.getLogger("mcp-analitica")
CAPACIDAD_TURNO = int(os.getenv("CAPACIDAD_TURNO", 20))

@mcp.tool()
async def generar_reporte_completo(fecha: str, turno: str, consultas: list, diagnosticos: list, 
                                   consumos: list, stock: list, alertas_epidemiologicas: str) -> str:
    """Genera el reporte completo en una sola llamada con datos de BD"""
    try:
        # Contar pacientes únicos
        pacientes_unicos = len(set(c.get("paciente_id") for c in consultas))
        
        # Calcular ocupación
        total_consultas = len(consultas)
        ocupacion_pct = (total_consultas / CAPACIDAD_TURNO * 100) if CAPACIDAD_TURNO > 0 else 0
        
        # Top diagnósticos (máximo 3)
        conteo_diag = Counter(d.get("diagnostico_nombre") for d in diagnosticos)
        top_diag = sorted(conteo_diag.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Proyección de stock (7 días)
        consumo_map = defaultdict(int)
        for c in consumos:
            consumo_map[c.get("medicamento_id")] += c.get("cantidad", 0)
        
        proyeccion = []
        for m in stock:
            consumo_diario = consumo_map.get(m.get("id"), 0)
            stock_proy = m.get("stock_actual", 0) - (consumo_diario * 7)
            proyeccion.append({
                "medicamento": m.get("nombre"),
                "stock_actual": m.get("stock_actual"),
                "stock_proyectado": stock_proy,
                "stock_minimo": m.get("stock_minimo"),
                "alerta": stock_proy <= m.get("stock_minimo", 0)
            })
        
        # Alertas de stock críticas
        alertas_stock = []
        for med in proyeccion:
            if med.get("alerta"):
                estado = "CRÍTICO" if med.get("stock_actual", 0) <= 0 else "BAJO"
                alertas_stock.append(
                    f"- **{med.get('medicamento')}**: Stock {med.get('stock_actual')}, "
                    f"Mínimo {med.get('stock_minimo')}, Proyectado {med.get('stock_proyectado')} [{estado}]"
                )
        
        # Recomendaciones
        recomendaciones = []
        for med in proyeccion:
            if med.get("stock_proyectado", 0) <= med.get("stock_minimo", 0):
                recomendaciones.append(f"- **URGENTE**: Reponer {med.get('medicamento')}")
        if not recomendaciones:
            recomendaciones = ["- Mantener vigilancia de stock en siguiente turno"]
        
        # Generar Markdown
        top_diag_text = "\n".join([f"- {d[0]}: {d[1]} consulta(s)" for d in top_diag]) if top_diag else "- Sin diagnósticos"
        alertas_text = "\n".join(alertas_stock) if alertas_stock else "- Todos los medicamentos en niveles normales"
        recom_text = "\n".join(recomendaciones)
        proyeccion_text = "\n".join([f"- {m['medicamento']}: {m['stock_proyectado']} unidades" for m in proyeccion[:3]])
        
        reporte = f"""# Cierre de Turno - {fecha} - {turno.capitalize()}

## Resumen
- Pacientes atendidos: {pacientes_unicos}
- Consultas registradas: {total_consultas}
- Ocupación: {round(ocupacion_pct, 2)}%

## Top Diagnósticos
{top_diag_text}

## Alertas de Stock
{alertas_text}

## Proyección de Stock (7 días)
{proyeccion_text if proyeccion_text else "- Sin cambios esperados"}

## Contexto Epidemiológico
{alertas_epidemiologicas if alertas_epidemiologicas else "Sin alertas"}

## Recomendaciones
{recom_text}

---
*Reporte generado automáticamente*"""
        
        return reporte
    except Exception as e:
        logger.error(json.dumps({"tool": "generar_reporte_completo", "error": str(e)}))
        return f"Error generando reporte: {str(e)}"

@mcp.tool()
async def calcular_top_diagnosticos(diagnosticos: list, limite: int = 3) -> list:
    try:
        conteo = Counter(d["diagnostico_nombre"] for d in diagnosticos)
        ordenados = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        resultado = []
        threshold = None
        for i, (nombre, total) in enumerate(ordenados):
            if i < limite:
                resultado.append({"diagnostico_nombre": nombre, "total": total})
                threshold = total
            elif total == threshold:
                resultado.append({"diagnostico_nombre": nombre, "total": total})
            else:
                break
        return resultado
    except Exception as e:
        logger.error(json.dumps({"tool": "calcular_top_diagnosticos", "error": str(e)}))
        return []

@mcp.tool()
async def calcular_ocupacion(consultas: list) -> dict:
    try:
        total = len(consultas)
        ocupacion = (total / CAPACIDAD_TURNO) * 100 if CAPACIDAD_TURNO > 0 else 0
        return {
            "total_consultas": total,
            "capacidad_turno": CAPACIDAD_TURNO,
            "ocupacion_porcentaje": round(ocupacion, 2)
        }
    except Exception as e:
        logger.error(json.dumps({"tool": "calcular_ocupacion", "error": str(e)}))
        return {}

@mcp.tool()
async def proyectar_stock(consumos: list, stock: list, dias: int = 7) -> list:
    try:
        consumo_map = defaultdict(int)
        for c in consumos:
            consumo_map[c["medicamento_id"]] += c["cantidad"]
        resultado = []
        for m in stock:
            consumo_diario = consumo_map.get(m["id"], 0)
            stock_proyectado = m["stock_actual"] - (consumo_diario * dias)
            resultado.append({
                "medicamento": m["nombre"],
                "stock_actual": m["stock_actual"],
                "consumo_diario": consumo_diario,
                "stock_proyectado": stock_proyectado,
                "stock_minimo": m["stock_minimo"],
                "alerta": stock_proyectado <= m["stock_minimo"]
            })
        return resultado
    except Exception as e:
        logger.error(json.dumps({"tool": "proyectar_stock", "error": str(e)}))
        return []

@mcp.tool()
async def calcular_consumo_promedio(consumos: list, medicamento_id: int) -> dict:
    try:
        cantidades = [c["cantidad"] for c in consumos if c["medicamento_id"] == medicamento_id]
        if not cantidades:
            return {"medicamento_id": medicamento_id, "promedio": 0}
        return {"medicamento_id": medicamento_id, "promedio": round(sum(cantidades)/len(cantidades), 2)}
    except Exception as e:
        return {}

@mcp.tool()
async def generar_resumen_diario(datos: dict) -> dict:
    try:
        top = await calcular_top_diagnosticos(datos.get("diagnosticos", []), 3)
        ocupacion = await calcular_ocupacion(datos.get("consultas", []))
        proyeccion = await proyectar_stock(datos.get("consumos", []), datos.get("stock", []), 7)
        return {"top_diagnosticos": top, "ocupacion": ocupacion, "proyeccion_stock": proyeccion}
    except Exception as e:
        logger.error(json.dumps({"tool": "generar_resumen_diario", "error": str(e)}))
        return {}

@mcp.tool()
async def generar_reporte_markdown(fecha: str, turno: str, pacientes: int, ocupacion_data: dict, 
                                   top_diagnosticos: list, proyeccion_stock: list, 
                                   alertas_epidemiologicas: str) -> str:
    """Genera el reporte completo en markdown estructurado"""
    try:
        ocupacion_pct = ocupacion_data.get("ocupacion_porcentaje", 0)
        total_consultas = ocupacion_data.get("total_consultas", 0)
        
        # Generar alertas de stock
        alertas_stock = []
        for med in proyeccion_stock:
            if med.get("alerta"):
                estado = "CRÍTICO" if med.get("stock_actual", 0) <= 0 else "BAJO"
                alertas_stock.append(
                    f"- **{med.get('medicamento')}**: Stock: {med.get('stock_actual')}, "
                    f"Mínimo: {med.get('stock_minimo')}, Proyectado: {med.get('stock_proyectado')}. "
                    f"[{estado}]"
                )
        
        alertas_text = "\n".join(alertas_stock) if alertas_stock else "- Todos los medicamentos dentro de niveles normales."
        
        # Generar top diagnósticos
        top_diag_text = ""
        if top_diagnosticos:
            for diag in top_diagnosticos:
                top_diag_text += f"- {diag.get('diagnostico_nombre')}: {diag.get('total')} consulta(s)\n"
        else:
            top_diag_text = "- Sin diagnósticos registrados.\n"
        
        # Generar proyección
        proyeccion_text = ""
        for med in proyeccion_stock[:3]:
            proyeccion_text += f"- {med.get('medicamento')}: {med.get('stock_proyectado')} unidades\n"
        
        #Generar recomendaciones
        recomendaciones = []
        for med in proyeccion_stock:
            if med.get("stock_proyectado", 0) <= med.get("stock_minimo", 0):
                recomendaciones.append(f"- **URGENTE**: Reponer {med.get('medicamento')} - proyectado: {med.get('stock_proyectado')}")
        
        if not recomendaciones:
            recomendaciones = ["- Mantener vigilancia de stock durante el siguiente turno."]
        
        recomendaciones_text = "\n".join(recomendaciones)
        
        reporte = f"""# Cierre de Turno - {fecha} - {turno.capitalize()}

## Resumen del Turno
- Pacientes atendidos: {pacientes}
- Total consultas: {total_consultas}
- Clínica: Centro Médico Norte

## Ocupación
**{ocupacion_pct}%** - Capacidad utilizada del turno

## Top Diagnósticos
{top_diag_text}

## Alertas de Stock
{alertas_text}

## Proyección de Stock (Próximo turno)
{proyeccion_text if proyeccion_text else "- Sin cambios significativos esperados."}

## Contexto Epidemiológico
{alertas_epidemiologicas}

## Recomendaciones Automáticas
{recomendaciones_text}

---
*Reporte generado automáticamente por el Sistema de Gestión Clínica*
"""
        return reporte
    except Exception as e:
        logger.error(json.dumps({"tool": "generar_reporte_markdown", "error": str(e)}))
        return f"Error generando reporte: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
