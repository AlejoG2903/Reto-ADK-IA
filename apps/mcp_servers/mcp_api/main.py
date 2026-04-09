import os
import json
import logging
import httpx
from fastmcp import FastMCP

mcp = FastMCP("mcp-api")
logger = logging.getLogger("mcp-api")
BASE_URL = os.getenv("DISEASE_API_URL", "https://disease.sh/v3/covid-19")

async def fetch(url: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
    except Exception as e:
        logger.error(json.dumps({"tool": "fetch", "error": str(e)}))
        return {"success": False, "error": str(e), "data": None}

@mcp.tool()
async def obtener_alertas_globales() -> dict:
    return await fetch(f"{BASE_URL}/all")

@mcp.tool()
async def obtener_alertas_pais(pais: str) -> dict:
    return await fetch(f"{BASE_URL}/countries/{pais}")

@mcp.tool()
async def obtener_historico_global() -> dict:
    return await fetch(f"{BASE_URL}/historical/all?lastdays=7")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8003)
