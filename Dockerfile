# Basis-Image mit Python
FROM python:3.10-slim

# Arbeitsverzeichnis im Container erstellen
WORKDIR /app

# System-Tools installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den gesamten Code kopieren
COPY . .

# Port für Streamlit öffnen
EXPOSE 8501

# Startbefehl
CMD ["streamlit", "run", "Pflanzen_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
