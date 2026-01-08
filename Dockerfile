# Basis-Image
FROM python:3.10-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Dateien kopieren (Punkt bedeutet: alles aus lokalem Ordner nach /app)
COPY . .

# Python-Bibliotheken installieren
RUN pip3 install -r requirements.txt

# Port für Streamlit
EXPOSE 8501

# Startbefehl (Wichtig: Der Pfad muss stimmen!)
ENTRYPOINT ["streamlit", "run", "Pflanzen_app.py", "--server.port=8501", "--server.address=0.0.0.0"]