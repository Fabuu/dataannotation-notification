import time
import os
import requests
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# .env Datei laden für lokale Ausführung
load_dotenv()

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
    last_projects = None

    while True:
        try:
            with sync_playwright() as p:
                # Browser mit Argumenten starten um Speicher/Cache zu sparen
                browser = p.chromium.launch(
                    headless=True, 
                    args=[
                        "--disable-dev-shm-usage", 
                        "--no-sandbox", 
                        "--disk-cache-size=0" 
                    ]
                )
                context = browser.new_context()
                page = context.new_page()

                try:
                    # Erster Login Versuch
                    print("Starte Bot...")
                    perform_login(page)

                    # Initial Nachricht
                    if last_projects is None:
                         if GREEN_API_INSTANCE_ID and GREEN_API_TOKEN and WHATSAPP_RECIPIENT:
                             send_whatsapp_message(f"🤖 Bot gestartet!\nIch überwache jetzt die Seite für dich.\n\nLink: {TARGET_URL}")

                    check_count = 0
                    while True:
                        if check_count >= 60:
                             print("♻️ Browser-Neustart zur Bereinigung...")
                             break

                        try:
                            print(f"Prüfe Seite: {TARGET_URL}")
                            page.goto(TARGET_URL)
                            
                            # Prüfen ob wir vielleicht ausgeloggt wurden
                            if "login" in page.url:
                                print("Session abgelaufen, logge neu ein...")
                                perform_login(page)
                                page.goto(TARGET_URL)

                            # Warte bis das Element geladen ist
                            page.wait_for_selector(MONITOR_SELECTOR, timeout=5000)
                            
                            # Inhalt analysieren (NUR Links/Projektnamen)
                            element = page.query_selector(MONITOR_SELECTOR)
                            
                            current_projects = {} # Name -> Typ
                            if element:
                                links = element.query_selector_all('a')
                                for link in links:
                                    text = link.inner_text().strip()
                                    href = link.get_attribute('href') or ""
                                    if text:
                                        # Unterscheidung Projekt vs Qualifikation
                                        # Heuristik: 'workers/qualifications' in URL oder implizit
                                        if "qualification" in href:
                                            p_type = "Qualifikation"
                                        else:
                                            p_type = "Projekt"
                                        current_projects[text] = p_type

                            current_project_names = set(current_projects.keys())

                            if last_projects is None:
                                last_projects = current_project_names
                                print(f"Initialer Status: {len(current_project_names)} Projekte gefunden.")
                                
                            else:
                                # Vergleiche Sets
                                new_items = current_project_names - last_projects
                                gone_items = last_projects - current_project_names
                                
                                if new_items:
                                    print("⚠️ NEUE PROJEKTE/QUALIFIKATIONEN! ⚠️")
                                    
                                    msg_lines = ["🚨 Neue Aufgaben verfügbar! 🚨\n"]
                                    for item in new_items:
                                        p_type = current_projects.get(item, "Aufgabe")
                                        msg_lines.append(f"🆕 {p_type}: {item}")
                                    
                                    msg_lines.append(f"\nLink: {TARGET_URL}")
                                    final_msg = "\n".join(msg_lines)
                                    
                                    if GREEN_API_INSTANCE_ID and GREEN_API_TOKEN and WHATSAPP_RECIPIENT:
                                        send_whatsapp_message(final_msg)
                                    
                                    # State aktualisieren
                                    last_projects = current_project_names

                                elif gone_items:
                                    print(f"Info: {len(gone_items)} Projekte sind verschwunden.")
                                    # Still update state so we can detect if they come back!
                                    last_projects = current_project_names
                                else:
                                    print("Keine relevanten Änderungen.")

                        except Exception as e:
                            print(f"Fehler beim Prüfen: {e}")
                            # Bei Fehlern innerhalb der Loop nicht sofort abbrechen, sondern retryen
                        
                        check_count += 1
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
