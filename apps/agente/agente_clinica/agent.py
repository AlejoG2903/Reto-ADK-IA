import logging
import os
from datetime import datetime
import pytz

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, SseConnectionParams
from google.genai.types import GenerateContentConfig

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BOGOTA_TZ = pytz.timezone("America/Bogota")

def get_context():
    now = datetime.now(BOGOTA_TZ)
    fecha = now.strftime("%Y-%m-%d")
    hour = now.hour
    turno = "Manana" if hour < 14 else "Tarde" if hour < 20 else "Noche"
    return fecha, turno

FECHA_HOY, TURNO_ACTUAL = get_context()

SYSTEM_PROMPT = f"""
Eres el Agente de Cierre de Centro Médico Norte.
Fecha: {FECHA_HOY} | Turno: {TURNO_ACTUAL}

Solo cuando el usuario solicite el cierre de turno, ejecuta este plan:

1. RECOPILA datos usando estas herramientas:
   - obtener_consultas_por_fecha(fecha="{FECHA_HOY}", turno="{TURNO_ACTUAL}")
   - obtener_diagnosticos_por_consulta(fecha="{FECHA_HOY}")
   - obtener_consumos_por_fecha(fecha="{FECHA_HOY}")
   - obtener_stock_actual()
   - alertas_bogota()

2. ANALIZA y GENERA el reporte con:
   - generar_reporte_markdown (pasa todos los datos obtenidos arriba)

3. GUARDA el resultado con:
   - escribir_archivo(ruta="/workspace/cierre_{FECHA_HOY}.md", contenido="CONTENIDO_DEL_REPORTE")

RESPUESTA FINAL:
Muestra el Markdown del reporte y nada más.
"""

def build_toolsets():
    """
    Construye los toolsets leyendo las URLs desde el entorno de Docker.
    Si las variables no existen, usa los nombres de servicio por defecto.
    """
    # Mapeo de variables de entorno definidas en tu docker-compose
    mcp_configs = [
        os.getenv("MCP_DATABASE_URL", "http://mcp_database:8001"),
        os.getenv("MCP_FILESYSTEM_URL", "http://mcp_filesystem:8002"),
        os.getenv("MCP_API_URL", "http://mcp_api:8003"),
        os.getenv("MCP_ANALITICA_URL", "http://mcp_analitica:8004")
    ]
    
    toolsets = []
    for base_url in mcp_configs:
        # Limpieza de URL y concatenación de /sse
        full_url = f"{base_url.rstrip('/')}/sse"
        logger.info(f"Conectando a MCP Toolset en: {full_url}")
        
        try:
            toolsets.append(
                McpToolset(
                    connection_params=SseConnectionParams(url=full_url)
                )
            )
        except Exception as e:
            logger.error(f"Error al inicializar toolset para {full_url}: {e}")
            
    return toolsets

# Inicialización del Agente
root_agent = LlmAgent(
    name="agente_clinica",
    model="gemini-2.5-flash-lite", 
    instruction=SYSTEM_PROMPT,
    generate_content_config=GenerateContentConfig(
        temperature=0.1,
        top_p=0.95
    ),
    tools=build_toolsets(),
)

if __name__ == "__main__":
    logger.info("Agente iniciado y listo para recibir peticiones.")