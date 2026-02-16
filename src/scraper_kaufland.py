from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # --- HIER DEINE KOPIERTE URL EINFÜGEN ---
    # Ersetze diesen Platzhalter mit der URL, die du gerade kopiert hast!
    # Sie sollte auf .json enden.
    manual_url = "https://filiale.kaufland.de/.kloffers.storeName=zwickau-aussere-dresdner-strasse.json" 
    
    # Falls du die URL noch nicht hast, lassen wir die Automatik drin,
    # aber mit erweitertem "Röntgen-Blick" (Debug).
    possible_stores = [
        manual_url, # Priorität 1: Deine manuelle URL
        "zwickau-aussere-dresdner-str",
        "de-zwickau-aussere-dresdner-str"
    ]
    
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://filiale.kaufland.de/",
    }

    bier_data = []
    bier_keywords = ["pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery"]
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    for store_input in possible_stores:
        # URL bauen, falls es keine volle URL ist
        if store_input.startswith("http"):
            url = store_input
        else:
            url = f"https://filiale.kaufland.de/.kloffers.storeName={store_input}.json"

        print(f"📡 Prüfe URL: {url}")
        
        try:
            time.sleep(random.uniform(1, 3))
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ Status {response.status_code}")
                continue
            
            data = response.json()
            
            # --- RÖNTGEN-BLICK: Was haben wir bekommen? ---
            if isinstance(data, list) and len(data) > 0:
                print(f"   ℹ️ Liste mit {len(data)} Elementen.")
                # Zeig uns die Schlüssel des ersten Elements, damit wir wissen, was es ist!
                print(f"   🔎 KEYS des ersten Elements: {list(data[0].keys())}")
            elif isinstance(data, dict):
                 print(f"   ℹ️ Dictionary erkannt. Keys: {list(data.keys())}")
            
            # --- EXTRAKTION ---
            all_raw_offers = []

            # Hilfsfunktion zum rekursiven Finden
            def find_items_with_price(obj):
                found = []
                if isinstance(obj, dict):
                    # Wenn es wie ein Angebot aussieht (hat Preis und Titel)
                    if "price" in obj and "title" in obj:
                        found.append(obj)
                    # Weitersuchen in allen Values
                    for k, v in obj.items():
                        if isinstance(v, (dict, list)):
                            found.extend(find_items_with_price(v))
                elif isinstance(obj, list):
                    for item in obj:
                        found.extend(find_items_with_price(item))
                return found

            all_raw_offers = find_items_with_price(data)

            if not all_raw_offers:
                print("   ⚠️ Keine Angebote mit 'price' und 'title' gefunden.")
                continue

            print(f"   ✅ {len(all_raw_offers)} Angebote extrahiert! Filtere Bier...")

            for offer in all_raw_offers:
                try:
                    title = offer.get("title", "")
                    subtitle = offer.get("subtitle", "")
                    full_name = f"{title} {subtitle}".strip()
                    
                    if any(k in full_name.lower() for k in bier_keywords) and not any(k in full_name.lower() for k in ignore_keywords):
                        price = offer.get("price", 0.0)
                        unit = offer.get("unit", "")
                        print(f"   🍺 {full_name} -> {price}€")
                        
                        bier_data.append({
                            "supermarkt": "Kaufland",
                            "name": full_name,
                            "preis": float(price),
                            "menge": unit,
                            "datum": datetime.date.today().isoformat()
                        })
                except:
                    continue
            
            if bier_data:
                break # Erfolg!

        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            continue

    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
