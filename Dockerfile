# Schlankes Python Image
FROM python:3.10-slim

# Arbeitsverzeichnis
WORKDIR /app

# Zuerst nur die requirements kopieren (effizienteres Caching)
COPY requirements.txt .

# Installiere Python-Pakete
RUN pip install --no-cache-dir -r requirements.txt

# Den restlichen Code kopieren
COPY . .

# Port freigeben
EXPOSE 8501

# Startbefehl (Prüfe hier unbedingt die Groß-/Kleinschreibung deiner Datei!)
ENTRYPOINT ["streamlit", "run", "Pflanzen_app.py", "--server.port=8501", "--server.address=0.0.0.0"]