from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # Schritt 1: ID herausfinden
    # Diese URL lieferte im Log die Liste mit 'klNr'
    meta_url = "https://filiale.kaufland.de/.kloffers.storeName=zwickau-aussere-dresdner-strasse.json"
    
    session = requests.Session(impersonate="chrome120")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    print("📡 Schritt 1: Hole Store-ID (klNr)...")
    store_id = None
    try:
        response = session.get(meta_url, headers=headers)
        data = response.json()
        
        # Wir suchen die 'klNr' im ersten Element der Liste
        if isinstance(data, list) and len(data) > 0:
            store_id = data[0].get('klNr')
            print(f"✅ Store ID gefunden: {store_id}")
        else:
            print(f"❌ Konnte keine Store ID finden. Datenstruktur: {str(data)[:100]}")
            return []
            
    except Exception as e:
        print(f"❌ Fehler bei Schritt 1: {e}")
        return []

    # Schritt 2: Echte Angebote laden mit der ID
    # Hier ändern wir "storeName=" zu "storeId=" !!!
    offers_url = f"https://filiale.kaufland.de/.kloffers.storeId={store_id}.json"
    print(f"📡 Schritt 2: Lade Angebote von {offers_url}")
    
    bier_data = []
    
    try:
        time.sleep(random.uniform(1, 3))
        response = session.get(offers_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Fehler Schritt 2: Status {response.status_code}")
            return []
            
        data = response.json()
        
        # Universal-Entpacker (wie vorhin)
        all_offers = []
        def extract_offers(container):
            found = []
            if isinstance(container, list):
                for item in container:
                    found.extend(extract_offers(item))
            elif isinstance(container, dict):
                if "price" in container and "title" in container:
                    found.append(container)
                elif "offers" in container:
                    found.extend(extract_offers(container["offers"]))
                elif "data" in container:
                    found.extend(extract_offers(container["data"]))
                elif "categories" in container:
                    found.extend(extract_offers(container["categories"]))
            return found

        all_offers = extract_offers(data)
        print(f"📦 {len(all_offers)} Angebote extrahiert.")
        
        # Filtern nach Bier
        bier_keywords = ["pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery"]
        ignore_keywords = ["alkoholfrei", "malztrunk"]

        for offer in all_offers:
            title = offer.get("title", "")
            subtitle = offer.get("subtitle", "")
            full_name = f"{title} {subtitle}".strip()
            name_lower = full_name.lower()
            
            if any(k in name_lower for k in bier_keywords) and not any(k in name_lower for k in ignore_keywords):
                price = float(offer.get("price", 0.0))
                unit = offer.get("unit", "")
                
                print(f"   🍺 Gefunden: {full_name} -> {price}")
                bier_data.append({
                    "supermarkt": "Kaufland",
                    "name": full_name,
                    "preis": price,
                    "menge": unit,
                    "datum": datetime.date.today().isoformat()
                })

    except Exception as e:
        print(f"❌ Fehler bei Schritt 2: {e}")

    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
