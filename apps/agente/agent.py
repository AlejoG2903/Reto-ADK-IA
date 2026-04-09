import os
from datetime import datetime
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams

MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

MCP_DATABASE_URL = os.getenv("MCP_DATABASE_URL", "http://mcp_database:8001") + "/sse"
MCP_FILESYSTEM_URL = os.getenv("MCP_FILESYSTEM_URL", "http://mcp_filesystem:8002") + "/sse"
MCP_API_URL = os.getenv("MCP_API_URL", "http://mcp_api:8003") + "/sse"
MCP_ANALITICA_URL = os.getenv("MCP_ANALITICA_URL", "http://mcp_analitica:8004") + "/sse"

now = datetime.now()
fecha_hoy = now.strftime("%Y-%m-%d")
turno = "manana" if now.hour < 14 else "tarde" if now.hour < 20 else "noche"

root_agent = LlmAgent(
    name="agente_clinica",
    model=MODEL,
    instruction=f"""
Eres un agente que genera cierres de turno clínico automáticamente.

CONTEXTO:
- Fecha: {fecha_hoy}
- Turno: {turno}
- Hora: {now.strftime("%H:%M")}

PASOS OBLIGATORIOS - Ejecuta en este orden exacto sin omitir ninguno:

PASO 1: Llama a obtener_resumen_epidemiologico()
PASO 2: Llama a obtener_consultas_por_fecha(fecha='{fecha_hoy}', turno='{turno}')
PASO 3: Llama a obtener_pacientes_por_fecha(fecha='{fecha_hoy}')
PASO 4: Llama a obtener_diagnosticos_por_consulta(fecha='{fecha_hoy}')
PASO 5: Llama a obtener_consumos_por_fecha(fecha='{fecha_hoy}')
PASO 6: Llama a obtener_stock_actual()
PASO 7: Llama a calcular_ocupacion(consultas=<lista del PASO 2>)
PASO 8: Llama a calcular_top_diagnosticos(diagnosticos=<lista del PASO 4>, limite=3)
PASO 9: Llama a proyectar_stock(consumos=<lista del PASO 5>, stock=<lista del PASO 6>, dias=7)
PASO 10: Llama a generar_reporte_markdown(
    fecha='{fecha_hoy}',
    turno='{turno}',
    pacientes=<cantidad de elementos en lista del PASO 3>,
    ocupacion_data=<dict del PASO 7>,
    top_diagnosticos=<lista del PASO 8>,
    proyeccion_stock=<lista del PASO 9>,
    alertas_epidemiologicas=<string del PASO 1>
)
PASO 11: Llama a write_file(path='cierre_{fecha_hoy}_{turno}.md', content=<string del PASO 10>)

REGLAS CRÍTICAS:
- NUNCA inventes, asumas ni hardcodees ningún dato.
- Usa ÚNICAMENTE los valores retornados por cada herramienta.
- Si un paso retorna lista vacía, pásala tal cual al siguiente paso.
- No termines hasta haber completado el PASO 11 exitosamente.
""",
    tools=[
        McpToolset(connection_params=SseConnectionParams(url=MCP_DATABASE_URL)),
        McpToolset(connection_params=SseConnectionParams(url=MCP_FILESYSTEM_URL)),
        McpToolset(connection_params=SseConnectionParams(url=MCP_API_URL)),
        McpToolset(connection_params=SseConnectionParams(url=MCP_ANALITICA_URL)),
    ]
)