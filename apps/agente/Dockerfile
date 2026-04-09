FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos dentro de una subcarpeta con el nombre del agente
COPY agent.py ./agente_clinica/agent.py
COPY __init__.py ./agente_clinica/__init__.py
COPY .agent.md ./agente_clinica/.agent.md
COPY .instructions.md ./agente_clinica/.instructions.md

CMD ["adk", "web", "--port", "8000", "--host", "0.0.0.0"]