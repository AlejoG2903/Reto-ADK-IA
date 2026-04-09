import os
import json
import logging
import asyncpg
from fastmcp import FastMCP

mcp = FastMCP("mcp-database")
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("mcp-database")
pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=10
        )
    return pool

@mcp.tool()
async def obtener_consultas_por_fecha(fecha: str, turno: str = None) -> list:
    query = """
        SELECT c.id, c.fecha_consulta, c.turno, c.notas,
               p.id as paciente_id, p.nombre as paciente_nombre, p.documento
        FROM consultas c JOIN pacientes p ON p.id = c.paciente_id
        WHERE DATE(c.fecha_consulta) = $1 AND ($2 IS NULL OR c.turno = $2)
        ORDER BY c.fecha_consulta ASC;
    """
    try:
        p = await get_pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query, fecha, turno)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(json.dumps({"tool": "obtener_consultas_por_fecha", "error": str(e)}))
        return []

@mcp.tool()
async def obtener_diagnosticos_por_consulta(fecha: str) -> list:
    query = """
        SELECT c.id AS consulta_id, c.fecha_consulta, c.turno,
               d.id AS diagnostico_id, d.nombre AS diagnostico_nombre,
               d.codigo AS diagnostico_codigo, cd.principal
        FROM consultas c
        JOIN consulta_diagnosticos cd ON cd.consulta_id = c.id
        JOIN diagnosticos d ON d.id = cd.diagnostico_id
        WHERE DATE(c.fecha_consulta) = $1
        ORDER BY c.fecha_consulta ASC;
    """
    try:
        p = await get_pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query, fecha)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(json.dumps({"tool": "obtener_diagnosticos_por_consulta", "error": str(e)}))
        return []

@mcp.tool()
async def obtener_consumos_por_fecha(fecha: str) -> list:
    query = """
        SELECT c.id AS consulta_id, c.fecha_consulta,
               m.id AS medicamento_id, m.nombre AS medicamento_nombre, co.cantidad
        FROM consumos co
        JOIN consultas c ON c.id = co.consulta_id
        JOIN medicamentos m ON m.id = co.medicamento_id
        WHERE DATE(c.fecha_consulta) = $1
        ORDER BY c.fecha_consulta ASC;
    """
    try:
        p = await get_pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query, fecha)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(json.dumps({"tool": "obtener_consumos_por_fecha", "error": str(e)}))
        return []

@mcp.tool()
async def obtener_stock_actual() -> list:
    query = "SELECT id, nombre, stock_actual, stock_minimo FROM medicamentos ORDER BY nombre ASC;"
    try:
        p = await get_pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(json.dumps({"tool": "obtener_stock_actual", "error": str(e)}))
        return []

@mcp.tool()
async def obtener_pacientes_por_fecha(fecha: str) -> list:
    query = """
        SELECT DISTINCT p.id, p.nombre, p.documento
        FROM consultas c JOIN pacientes p ON p.id = c.paciente_id
        WHERE DATE(c.fecha_consulta) = $1 ORDER BY p.nombre ASC;
    """
    try:
        p = await get_pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query, fecha)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(json.dumps({"tool": "obtener_pacientes_por_fecha", "error": str(e)}))
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8001)
