# Basis-Image von Microsoft Playwright (enthält Python + Browser)
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den Bot-Code kopieren
COPY bot.py .

# Playwright Browser installieren (sicherheitshalber, falls im Base Image was fehlt)
RUN playwright install chromium

# Umgebungsvariable für unbuffered Output (damit Logs sofort in Docker erscheinen)
ENV PYTHONUNBUFFERED=1

# Start-Befehl
CMD ["python", "bot.py"]
