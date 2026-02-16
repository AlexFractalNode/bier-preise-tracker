import json
import datetime
# Später importieren wir hier die einzelnen Scraper
# from scraper_netto import get_netto_prices

def main():
    all_deals = []
    
    print("Starte Scraping...")
    
    # Beispiel-Dummy-Daten (bis wir die echten Scraper schreiben)
    # Hier würdest du später loopen: for market in markets: ...
    timestamp = datetime.datetime.now().isoformat()
    
    # TODO: Echte Scraper hier aufrufen
    # all_deals.extend(get_netto_prices("08056")) # Zwickau PLZ
    
    print(f"Fertig. {len(all_deals)} Angebote gefunden.")
    
    # Speichern
    with open('data/preise.json', 'w', encoding='utf-8') as f:
        json.dump(all_deals, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
