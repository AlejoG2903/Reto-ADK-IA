import os
import json
import logging
import httpx
from fastmcp import FastMCP

# Usamos un nombre simple sin guiones para evitar problemas de resolución
mcp = FastMCP("epidemiologia")
logger = logging.getLogger("mcp-epidemiologia")

BASE_URL = "https://www.datos.gov.co/resource/gt2j-8ykr.json"

async def fetch(params: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            # Creamos un resumen para que el LLM lo procese fácil
            resumen = f"Se encontraron {len(data)} registros epidemiológicos activos." if data else "No hay alertas activas."
            return {"success": True, "resumen": resumen, "data": data}
    except Exception as e:
        logger.error(f"Error en fetch: {str(e)}")
        return {"success": False, "error": str(e), "resumen": "Error al consultar alertas."}

@mcp.tool()
async def alertas_bogota() -> dict:
    """Obtiene datos epidemiológicos filtrados para Bogotá"""
    params = {"ciudad_municipio_nom": "BOGOTA", "$limit": 10}
    return await fetch(params)

@mcp.tool()
async def alertas_colombia() -> dict:
    """Datos generales de Colombia"""
    params = {"$limit": 10}
    return await fetch(params)

if __name__ == "__main__":
    mcp.run(transport="sse")