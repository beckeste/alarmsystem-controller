# Verwende das offizielle Python-Image als Basis
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis
WORKDIR /app

# Kopiere die Anforderungen-Datei in das Arbeitsverzeichnis
COPY requirements.txt .

# Installiere die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Anwendungscodes in das Arbeitsverzeichnis
COPY . .

# Erstelle das Verzeichnis für die SQLite-Datenbank und setze die Berechtigungen
RUN mkdir -p /app/data && chmod -R 777 /app/data

# Setze die Umgebungsvariable für Flask
ENV FLASK_APP=app.py

# Exponiere den Port, auf dem die Anwendung laufen wird
EXPOSE 5000

# Führe die Anwendung aus
CMD ["flask", "run", "--host=0.0.0.0"]