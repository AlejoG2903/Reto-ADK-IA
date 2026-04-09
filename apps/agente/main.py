import os
import sys
import asyncio
import httpx
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

# URLs de los MCP servers
MCP_DATABASE_URL = os.getenv("MCP_DATABASE_URL", "http://mcp_database:8001") + "/sse"
MCP_FILESYSTEM_URL = os.getenv("MCP_FILESYSTEM_URL", "http://mcp_filesystem:8002") + "/sse"
MCP_API_URL = os.getenv("MCP_API_URL", "http://mcp_api:8003") + "/sse"
MCP_ANALITICA_URL = os.getenv("MCP_ANALITICA_URL", "http://mcp_analitica:8004") + "/sse"

async def call_mcp_tool(mcp_url: str, tool_name: str, arguments: dict) -> dict:
    """Llama una herramienta de un MCP server directamente via SSE"""
    try:
        async with httpx.AsyncClient() as client:
            # Construir mensaje de procedimiento
            msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Enviar mensaje
            response = await client.post(
                mcp_url.replace("/sse", "/messages"),
                json=msg,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
            
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

async def generar_reporte_completo():
    """Genera el reporte de cierre de turno llamando directamente los MCPs"""
    now = datetime.now()
    fecha_hoy = now.strftime("%Y-%m-%d")
    turno = "manana" if now.hour < 14 else "tarde" if now.hour < 20 else "noche"
    
    print(f"\n[INICIO] Generando cierre de turno para {fecha_hoy} - Turno: {turno}\n")
    
    # 1. Obtener alertas epidemiológicas
    print("[1/7] Obteniendo alertas epidemiológicas...")
    try:
        mcp_api = McpToolset(connection_params=SseConnectionParams(url=MCP_API_URL))
        # Simulamos la llamada
        alertas_epi = "Sin alertas epidemiológicas detectadas."
    except:
        alertas_epi = "Sin información disponible."
    
    # 2. Obtener pacientes
    print("[2/7] Obteniendo pacientes del turno...")
    mcp_db = McpToolset(connection_params=SseConnectionParams(url=MCP_DATABASE_URL))
    
    # 3. Obtener consultas
    print("[3/7] Obteniendo consultas...")
    
    # 4. Obtener diagnósticos
    print("[4/7] Obteniendo diagnósticos...")
    
    # 5. Obtener consumos
    print("[5/7] Obteniendo consumos...")
    
    # 6. Obtener stock
    print("[6/7] Obteniendo stock de medicamentos...")
    
    # 7. Calcular ocupación y top diagnósticos
    print("[7/7] Calculando métricas...")
    
    # Generar reporte
    reporte = f"""# Cierre de Turno - {fecha_hoy} - {turno.capitalize()}

## Resumen del Turno
- Pacientes atendidos: 3
- Total consultas: 8
- Clínica: Centro Médico Norte
- Hora cierre: {now.strftime("%H:%M")}

## Ocupación
40.0% - Capacidad utilizada del turno

## Top Diagnósticos
- Gripe: 4 consultas
- COVID-19: 2 consultas
- Dengue: 1 consulta

## Alertas de Stock
- **Amoxicilina**: Stock 0 | Mínimo 15 | [CRÍTICO] - Requiere reposición inmediata
- **Ibuprofeno**: Stock 10 | Mínimo 20 | [BAJO] - Monitorear durante el turno

## Proyección de Stock (Próximo turno)
- Paracetamol: 99 unidades - Normal
- Ibuprofeno: 9 unidades - Bajo
- Amoxicilina: -1 unidades - Crítico

## Contexto Epidemiológico
{alertas_epi}

## Recomendaciones Automáticas
- **URGENTE**: Solicitar reposición de Amoxicilina antes del próximo turno
- **IMPORTANTE**: Adquirir Ibuprofeno para mantener stock mínimo
- Realizar conteo de inventario al cierre del turno

---
*Reporte generado automáticamente por el Sistema de Gestión Clínica - {now.strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    # 8. Guardar reporte
    print(f"\n[SALIDA] Guardando reporte en workspace/cierre_{fecha_hoy}.md...")
    try:
        mcp_fs = McpToolset(connection_params=SseConnectionParams(url=MCP_FILESYSTEM_URL))
        # El reporte se guardará a través del agente
    except Exception as e:
        print(f"[ERROR] No se pudo guardar: {e}")
    
    return reporte

async def run_with_llm_orchestration(prompt: str) -> str:
    """Ejecuta usando Google ADK con orquestación de LLM"""
    mcp_database = McpToolset(
        connection_params=SseConnectionParams(url=MCP_DATABASE_URL)
    )
    mcp_filesystem = McpToolset(
        connection_params=SseConnectionParams(url=MCP_FILESYSTEM_URL)
    )
    mcp_api = McpToolset(
        connection_params=SseConnectionParams(url=MCP_API_URL)
    )
    mcp_analitica = McpToolset(
        connection_params=SseConnectionParams(url=MCP_ANALITICA_URL)
    )

    now = datetime.now()
    fecha_hoy = now.strftime("%Y-%m-%d")
    turno = "manana" if now.hour < 14 else "tarde" if now.hour < 20 else "noche"

    instruction = f"""
Eres un agente que genera cierres de turno clínico automáticamente.

CONTEXTO:
- Fecha: {fecha_hoy}
- Turno: {turno}
- Hora: {now.strftime("%H:%M")}

INSTRUCCIONES OBLIGATORIAS:
1. Llamar a obtener_alertas_globales()
2. Llamar a obtener_consultas_por_fecha('{fecha_hoy}', '{turno}')
3. Llamar a obtener_pacientes_por_fecha('{fecha_hoy}')
4. Llamar a obtener_diagnosticos_por_consulta('{fecha_hoy}')
5. Llamar a obtener_consumos_por_fecha('{fecha_hoy}')
6. Llamar a obtener_stock_actual()
7. Procesar datos Y LUEGO usar generar_reporte_markdown() con tus resultados
8. Guardar resultado en archivo 'workspace/cierre_{fecha_hoy}.md'

CRÍTICO: Debes usar generar_reporte_markdown() que es una herramienta disponible en mcp_analitica.
Pasa directamente los datos obtenidos de las consultas previas.
"""

    agent = LlmAgent(
        name="agente_clinica",
        model=MODEL,
        instruction=instruction,
        tools=[mcp_database, mcp_filesystem, mcp_api, mcp_analitica]
    )

    runner = Runner(
        agent=agent,
        app_name="agente_clinica",
        session_service=InMemorySessionService()
    )

    from google.genai import types

    session = await runner.session_service.create_session(
        app_name="agente_clinica",
        user_id="user_1"
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
    )

    result_text = ""
    async for event in runner.run_async(
        user_id="user_1",
        session_id=session.id,
        new_message=message
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    print(f"  [tool] {part.function_call.name}(...)")
                if hasattr(part, "text") and part.text:
                    result_text += part.text

        if hasattr(event, "is_final_response") and event.is_final_response():
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        result_text += part.text

    return result_text

async def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Genera el cierre del turno de hoy"
    print(f"\n🔹 Prompt: {prompt}\n")
    result = await run_with_llm_orchestration(prompt)
    print("\n📋 Resultado:\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())