import json
import datetime
import os
import sys

# Damit Python Module im selben Ordner findet, wenn man das Skript aus dem Root-Verzeichnis startet
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Importiere deinen Scraper
from scraper_netto import get_netto_prices

def main():
    all_deals = []
    
    print("Starte Scraping Pipeline...")
    timestamp = datetime.datetime.now().isoformat()

    # --- NETTO SCRAPER ---
    print("Scrape Netto...")
    try:
        # Hier könntest du die Store-ID für Zwickau übergeben, falls nötig
        # Die ID findest du über die Netto-Webseite -> Cookies (wie vorhin besprochen)
        netto_deals = get_netto_prices() 
        print(f"Netto: {len(netto_deals)} Angebote gefunden.")
        all_deals.extend(netto_deals)
    except Exception as e:
        print(f"Fehler bei Netto: {e}")
    
    # --- ENDE NETTO ---

    print(f"Fertig. Insgesamt {len(all_deals)} Angebote geladen.")
    
    # Sicherstellen, dass der Ordner 'data' existiert
    os.makedirs('data', exist_ok=True)
    
    # Speichern
    filepath = 'data/preise.json'
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_deals, f, indent=4, ensure_ascii=False)
    
    print(f"Daten gespeichert in {filepath}")

if __name__ == "__main__":
    main()
