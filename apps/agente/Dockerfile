FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agente_clinica/ ./agente_clinica/
COPY main.py .
CMD ["adk", "web", "--port", "8000", "--host", "0.0.0.0"]