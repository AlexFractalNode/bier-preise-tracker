from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # Zwickau Äußere Dresdner Str
    store_name = "zwickau-aussere-dresdner-str"
    url = f"https://filiale.kaufland.de/.kloffers.storeName={store_name}.json"
    
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://filiale.kaufland.de/",
    }

    print(f"📡 Lade Kaufland Daten: {url}")

    try:
        time.sleep(random.uniform(1, 3))
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Fehler: Status {response.status_code}")
            return []
            
        data = response.json()
        
        # --- DER UNIVERSAL-ENTPACKER ---
        all_offers = []

        # Hilfsfunktion: Findet Angebote, egal wie tief sie stecken
        def extract_offers(container):
            found = []
            if isinstance(container, list):
                for item in container:
                    found.extend(extract_offers(item))
            elif isinstance(container, dict):
                # Ist es ein Angebot? (Hat Preis und Titel)
                if "price" in container and "title" in container:
                    found.append(container)
                # Oder ist es eine Kategorie mit Unter-Angeboten?
                elif "offers" in container:
                    found.extend(extract_offers(container["offers"]))
                # Oder eine "data" wrapper?
                elif "data" in container:
                    found.extend(extract_offers(container["data"]))
                # Oder "categories"?
                elif "categories" in container:
                    found.extend(extract_offers(container["categories"]))
            return found

        all_offers = extract_offers(data)
        
        if not all_offers:
            print("⚠️ Keine Angebote extrahieren können. Struktur unbekannt.")
            return []
            
        print(f"📦 {len(all_offers)} Roh-Angebote extrahiert.")
        
        # DEBUG: Zeig uns das erste Element, damit wir wissen, was wir haben
        if len(all_offers) > 0:
            print(f"🔎 DEBUG - Erstes Item: {all_offers[0].get('title')} - {all_offers[0].get('price')}")

    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        return []

    # --- FILTERN & AUFBEREITEN ---
    bier_data = []
    
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery", "köstritzer"
    ]
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    for offer in all_offers:
        try:
            title = offer.get("title", "")
            subtitle = offer.get("subtitle", "")
            full_name = f"{title} {subtitle}".strip()
            
            # Filter
            name_lower = full_name.lower()
            is_match = any(k in name_lower for k in bier_keywords)
            is_ignored = any(k in name_lower for k in ignore_keywords)
            
            if is_match and not is_ignored:
                price = offer.get("price", 0.0)
                unit = offer.get("unit", "") # z.B. "je Ka. 20 x 0,5-l-Fl."
                
                print(f"   🍺 Gefunden: {full_name} für {price}€")
                
                bier_data.append({
                    "supermarkt": "Kaufland",
                    "name": full_name,
                    "preis": float(price),
                    "menge": unit,
                    "datum": datetime.date.today().isoformat()
                })
                
        except Exception:
            continue

    print(f"✅ Fertig. {len(bier_data)} Bier-Angebote bei Kaufland gefunden.")
    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
