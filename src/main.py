import json
import datetime
import os
import sys

# Damit Module gefunden werden
sys.path.append(os.path.join(os.path.dirname(__file__)))

from scraper_netto import get_netto_prices
from scraper_kaufland import get_kaufland_prices

def load_existing_data():
    filepath = 'data/preise.json'
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def main():
    print("🚀 Starte Scraping Pipeline...")
    
    # 1. Alte Daten laden (Sicherung!)
    existing_data = load_existing_data()
    print(f"📦 Alte Daten geladen: {len(existing_data)} Einträge.")
    
    new_data_netto = []
    new_data_kaufland = []

    # --- NETTO ---
    print("\n--- Scrape Netto ---")
    try:
        netto_result = get_netto_prices()
        if netto_result:
            print(f"✅ Netto erfolgreich: {len(netto_result)} Angebote.")
            new_data_netto = netto_result
        else:
            print("⚠️ Netto Scraper leer/geblockt. Behalte alte Netto-Daten.")
            # Wir filtern die alten Daten nach Netto und behalten sie
            new_data_netto = [d for d in existing_data if d.get('supermarkt') == 'Netto' or d.get('supermarkt') == 'Netto Marken-Discount']
    except Exception as e:
        print(f"❌ Fehler bei Netto: {e}")
        new_data_netto = [d for d in existing_data if d.get('supermarkt') == 'Netto' or d.get('supermarkt') == 'Netto Marken-Discount']

    # --- KAUFLAND ---
    print("\n--- Scrape Kaufland ---")
    try:
        kaufland_result = get_kaufland_prices()
        if kaufland_result:
            print(f"✅ Kaufland erfolgreich: {len(kaufland_result)} Angebote.")
            new_data_kaufland = kaufland_result
        else:
            print("⚠️ Kaufland Scraper leer. Behalte alte Kaufland-Daten.")
            new_data_kaufland = [d for d in existing_data if d.get('supermarkt') == 'Kaufland']
    except Exception as e:
        print(f"❌ Fehler bei Kaufland: {e}")
        new_data_kaufland = [d for d in existing_data if d.get('supermarkt') == 'Kaufland']

    # --- ZUSAMMENFÜHREN ---
    total_data = new_data_netto + new_data_kaufland
    
    print(f"\n💾 Speichere insgesamt {len(total_data)} Angebote.")
    
    os.makedirs('data', exist_ok=True)
    with open('data/preise.json', 'w', encoding='utf-8') as f:
        json.dump(total_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
