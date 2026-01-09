# DataAnnotation Monitor Bot 🤖

Ein automatisierter Bot, der die DataAnnotation Projekt-Seite überwacht und dich sofort via WhatsApp (Green API) oder andere Kanäle benachrichtigt, sobald neue Projekte oder Qualifikationen verfügbar sind.

## Features

*   🔄 Überprüft die Seite automatisch alle 60 Sekunden (konfigurierbar).
*   🚀 **Playwright** Basiert: Login und Navigation erfolgen über einen echten Browser (im Headless Mode).
*   📱 **WhatsApp Benachrichtigungen**: Integriert mit Green API für sofortige Alerts aufs Handy.
*   🐳 **Docker Ready**: Einfaches Deployment mit Docker Compose (perfekt für Portainer / Home Server).
*   🛡️ **Robust**: Startet sich bei Fehlern oder Browser-Crashes automatisch neu.

## Installation & Nutzung

### 1. Repository klonen
```bash
git clone https://github.com/DEIN_USER/DA-Notifications.git
cd DA-Notifications
```

### 2. Konfiguration (.env)
Erstelle eine Datei namens `.env` im Hauptverzeichnis und trage deine Daten ein.
Eine Vorlage findest du unten, kopiere einfach diesen Inhalt:

`.env` Datei:
```env
# Deine DataAnnotation Zugangsdaten
BOT_USERNAME=deine-email@beispiel.com
BOT_PASSWORD=dein-passwort

# Prüf-Intervall in Sekunden
CHECK_INTERVAL=60

# WhatsApp Benachrichtigung (Green API)
# Hole dir einen Account unter https://green-api.com/
GREEN_API_INSTANCE_ID=1234567890
GREEN_API_TOKEN=dein_langer_token_hier
# Empfänger Nummer (Format: Ländervorwahl ohne + oder 00, z.B. 49 für DE)
WHATSAPP_RECIPIENT=4915112345678@c.us
```

### 3. Starten mit Docker (Empfohlen)

Einfach Docker Compose verwenden:

```bash
docker-compose up -d --build
```

Oder in **Portainer**:
1.  Neuen Stack erstellen.
2.  Repository URL angeben (oder `docker-compose.yml` Inhalt kopieren).
3.  Wichtig: Die Environment Variablen in Portainer setzen oder die `.env` Datei bereitstellen.

### Manuelle Installation (Python)

Voraussetzungen: Python 3.8+

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Playwright Browser laden
playwright install chromium

# Starten
python bot.py
```

## Haftungsausschluss

Dieses Tool dient nur zu Bildungszwecken. Die Nutzung erfolgt auf eigene Gefahr. Beachte die Nutzungsbedingungen (Terms of Service) von DataAnnotation.
