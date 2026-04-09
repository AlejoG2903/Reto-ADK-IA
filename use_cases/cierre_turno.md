# Caso de Uso: Cierre de Turno Automatizado

## 🎯 Problema

El cierre de turno clínico se realiza manualmente, tomando ~30 minutos y con riesgo de errores.

---

## 🚀 Solución

El agente IA automatiza el proceso generando un reporte completo en ~5 segundos.

---

## ⚙️ Ejecución

```bash
docker-compose exec agente python main.py \
  "Genera el cierre del turno de hoy"
```

---

## 🔄 Flujo

1. Obtiene pacientes del día
2. Analiza diagnósticos
3. Calcula consumo de medicamentos
4. Verifica stock
5. Genera reporte automático

---

## 📊 Resultado

* ⏱️ 30 min → 5 segundos
* 📉 Menos errores humanos
* 🚨 Detección automática de alertas

---

## 📁 Output

Se genera un archivo:

```
/app/workspace/cierre_<fecha>.md
```

---

## 🧠 Valor

Demuestra:

* Orquestación con Google ADK
* Integración de múltiples MCP servers
* Lógica de negocio clínica
* Generación automática de reportes

---
