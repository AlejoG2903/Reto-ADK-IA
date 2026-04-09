# 🏥 Sistema de Gestión de Turnos con Agente AI (ADK)

## 📌 Descripción

Este proyecto implementa un agente inteligente para la gestión de turnos en una clínica, utilizando arquitectura basada en MCP servers y un modelo LLM.

El agente permite automatizar:

* Creación de turnos
* Asignación de pacientes
* Validación de capacidad
* Cierre de turnos

---

## 🚀 Ejecución rápida

```bash
git clone https://github.com/AlejoG2903/Reto-ADK-IA
cd Reto-ADK-IA
cp .env.example .env
docker-compose up -d --build
```

---

## 🧪 Ejecutar tests

```bash
pytest tests/test_completo.py -v
```

---

## 🤖 Uso del agente

Ejecutar un prompt dentro del contenedor:

```bash
docker-compose exec agente python main.py "Crear un turno con 10 pacientes"
```

Ejemplos:

```bash
docker-compose exec agente python main.py "Asignar paciente a turno"
docker-compose exec agente python main.py "Cerrar turno"
```

---

## 📂 Estructura del proyecto

```
.
├── agente/
├── mcp_database/
├── mcp_filesystem/
├── mcp_api/
├── mcp_analitica/
├── tests/
├── use_cases/
│   └── cierre_turno.md
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 🔧 Variables de entorno

Copiar el archivo:

```bash
cp .env.example .env
```

Variables principales:

* `POSTGRES_USER`
* `POSTGRES_PASSWORD`
* `POSTGRES_DB`
* `CAPACIDAD_TURNO`
* `LLM_MODEL`
* `GOOGLE_API_KEY`

---

## 📘 Caso de uso

El flujo de cierre de turno está documentado en:

```
/use_cases/cierre_turno.md
```

Incluye:

* Reglas de negocio
* Flujo completo
* Ejemplo práctico

---

## 🐳 Arquitectura

El sistema está compuesto por:

* Agente principal (ADK)
* MCP Database
* MCP Filesystem
* MCP API
* MCP Analítica
* PostgreSQL

---

## ✅ Estado del proyecto

* ✔️ Proyecto funcional
* ✔️ Tests automatizados (≥15)
* ✔️ Caso de uso documentado
* ✔️ Configuración con `.env.example`
* ✔️ Docker completamente operativo

---
