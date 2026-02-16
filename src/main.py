import json
import datetime
import os
import sys

# Damit Module gefunden werden
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Scraper importieren
from scraper_netto import get_netto_prices
from scraper_kaufland import get_kaufland_prices # <-- NEU

def main():
    all_deals = []
    
    print("🚀 Starte Scraping Pipeline...")

    # --- 1. NETTO ---
    print("\n--- Netto ---")
    try:
        netto_deals = get_netto_prices()
        print(f"Netto: {len(netto_deals)} Angebote.")
        all_deals.extend(netto_deals)
    except Exception as e:
        print(f"Fehler bei Netto: {e}")

    # --- 2. KAUFLAND (NEU) ---
    print("\n--- Kaufland ---")
    try:
        kaufland_deals = get_kaufland_prices()
        print(f"Kaufland: {len(kaufland_deals)} Angebote.")
        all_deals.extend(kaufland_deals)
    except Exception as e:
        print(f"Fehler bei Kaufland: {e}")

    # --- SPEICHERN ---
    print(f"\n💾 Fertig. Insgesamt {len(all_deals)} Angebote geladen.")
    
    os.makedirs('data', exist_ok=True)
    filepath = 'data/preise.json'
    
    # JSON sauber speichern
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(all_deals, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
