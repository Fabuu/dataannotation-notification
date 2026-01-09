import time
import os
import requests
from playwright.sync_api import sync_playwright

# Konfiguration
LOGIN_URL = "https://app.dataannotation.tech/users/sign_in"
TARGET_URL = "https://app.dataannotation.tech/workers/projects"

# Sensible Daten aus Environment Variables laden (für Docker/Sicherheit)
USERNAME = os.environ.get("BOT_USERNAME")
PASSWORD = os.environ.get("BOT_PASSWORD")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 60))

# Green API (WhatsApp) Konfiguration
GREEN_API_INSTANCE_ID = os.environ.get("GREEN_API_INSTANCE_ID")
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN")
WHATSAPP_RECIPIENT = os.environ.get("WHATSAPP_RECIPIENT") # Format: 491701234567@c.us

# CSS Selektoren anpassen!
USERNAME_SELECTOR = "#user_email"
PASSWORD_SELECTOR = "#user_password"
SUBMIT_SELECTOR = "input[type='submit']"
# Der Div, den du überwachen willst (enthält Projekte und Qualifikationen)
MONITOR_SELECTOR = '[id="workers/WorkerProjectsTable-hybrid-root"]' 

def run_bot():
    last_content = None

    while True:
        try:
            with sync_playwright() as p:
                # headless=True bedeutet, der Browser läuft im Hintergrund ohne Fenster.
                browser = p.chromium.launch(headless=True) 
                context = browser.new_context()
                page = context.new_page()

                try:
                    # Erster Login Versuch
                    print("Starte Bot...")
                    perform_login(page)

                    while True:
                        try:
                            print(f"Prüfe Seite: {TARGET_URL}")
                            page.goto(TARGET_URL)
                            
                            # Prüfen ob wir vielleicht ausgeloggt wurden (z.B. Redirect zur Login Seite)
                            if "login" in page.url:
                                print("Session abgelaufen, logge neu ein...")
                                perform_login(page)
                                page.goto(TARGET_URL)

                            # Warte bis das Element geladen ist
                            page.wait_for_selector(MONITOR_SELECTOR, timeout=5000)
                            
                            # Inhalt des überwachten Elements holen
                            element = page.query_selector(MONITOR_SELECTOR)
                            current_content = element.inner_text() if element else ""

                            if last_content is None:
                                last_content = current_content
                                print("Initialer Status gespeichert.")
                            elif current_content != last_content:
                                print("⚠️ ÄNDERUNG ERKANNT! ⚠️")
                                print(f"Neu: {current_content}")
                                
                                # WhatsApp Nachricht via Green API
                                if GREEN_API_INSTANCE_ID and GREEN_API_TOKEN and WHATSAPP_RECIPIENT:
                                    send_whatsapp_message(f"🚨 DataAnnotation Änderung! 🚨\n\nNeuer Status:\n{current_content[:500]}")
                                
                                last_content = current_content
                            else:
                                print("Keine Änderung.")

                        except Exception as e:
                            print(f"Fehler beim Prüfen: {e}")
                            # Bei Fehlern innerhalb der Loop nicht sofort abbrechen, sondern retryen
                            # Außer es ist ein Browser-Crash, den fängt die äußere Loop

                        time.sleep(CHECK_INTERVAL)

                except KeyboardInterrupt:
                    print("Bot beendet.")
                    raise # Raus aus dem Wrapper
                finally:
                    browser.close()
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"KRITISCHER FEHLER (Browser Crash?): {e}")
            print("Starte Bot neu in 10 Sekunden...")
            time.sleep(10)

def perform_login(page):
    print("Führe Login durch...")
    page.goto(LOGIN_URL)
    
    # Warte auf Login Felder
    page.wait_for_selector(USERNAME_SELECTOR)
    
    # Daten eingeben
    page.fill(USERNAME_SELECTOR, USERNAME)
    page.fill(PASSWORD_SELECTOR, PASSWORD)
    page.click(SUBMIT_SELECTOR)
    
    # Warte kurz, um sicherzugehen, dass der Request raus ist
    page.wait_for_timeout(2000)
    
    # Warte explizit darauf, dass wir auf der Projektseite landen oder der Monitor-Selektor sichtbar wird
    try:
        print("Warte auf Weiterleitung zur Projektseite...")
        # Entweder URL ändert sich
        page.wait_for_url("**/workers/projects", timeout=15000)
    except:
        print("URL Check Time-out - Prüfe ob Element trotzdem da ist...")

    print("Login Schritt abgeschlossen.")

def send_whatsapp_message(message):
    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE_ID}/SendMessage/{GREEN_API_TOKEN}"
        payload = {
            "chatId": WHATSAPP_RECIPIENT,
            "message": message
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("✅ WhatsApp Nachricht gesendet.")
        else:
            print(f"❌ Fehler beim Senden an WhatsApp: {response.text}")
    except Exception as e:
        print(f"❌ Exception beim Senden an WhatsApp: {e}")

if __name__ == "__main__":
    run_bot()
