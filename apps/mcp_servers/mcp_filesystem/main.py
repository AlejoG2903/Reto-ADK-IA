import os
import json
import logging
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("mcp-filesystem")
logger = logging.getLogger("mcp-filesystem")
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "/app/workspace")).resolve()

def validar_ruta(ruta: str) -> Path:
    ruta_completa = (WORKSPACE_DIR / ruta).resolve()
    if not str(ruta_completa).startswith(str(WORKSPACE_DIR)):
        raise ValueError("Acceso a ruta no permitido")
    return ruta_completa

@mcp.tool()
async def escribir_archivo(ruta: str, contenido: str) -> dict:
    try:
        path = validar_ruta(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contenido, encoding="utf-8")
        return {"success": True, "ruta": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def leer_archivo(ruta: str) -> dict:
    try:
        path = validar_ruta(ruta)
        if not path.exists():
            return {"success": False, "error": "Archivo no existe"}
        return {"success": True, "contenido": path.read_text(encoding="utf-8")}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def listar_archivos(directorio: str = "") -> dict:
    try:
        path = validar_ruta(directorio)
        if not path.exists() or not path.is_dir():
            return {"success": False, "error": "Directorio no existe"}
        return {"success": True, "archivos": [p.name for p in path.iterdir()]}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def eliminar_archivo(ruta: str) -> dict:
    try:
        path = validar_ruta(ruta)
        if not path.exists():
            return {"success": False, "error": "Archivo no existe"}
        path.unlink()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def existe_archivo(ruta: str) -> dict:
    try:
        path = validar_ruta(ruta)
        return {"success": True, "existe": path.exists()}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="sse")
