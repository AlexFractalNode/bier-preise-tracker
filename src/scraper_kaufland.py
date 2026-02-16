from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # Zwickau Äußere Dresdner Str
    possible_stores = [
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
    
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery", "köstritzer"
    ]
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    for store_name in possible_stores:
        url = f"https://filiale.kaufland.de/.kloffers.storeName={store_name}.json"
        print(f"📡 Teste Kaufland URL: {url}")
        
        try:
            time.sleep(random.uniform(1, 3))
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ Status {response.status_code}")
                continue
            
            data = response.json()
            all_raw_offers = []
            
            # --- LOGIK UPDATE ---
            if isinstance(data, list):
                print(f"   ℹ️ Liste erkannt ({len(data)} Einträge). Gehe davon aus, dass dies direkt die Angebote sind.")
                all_raw_offers = data # Wir nehmen die Liste direkt!
            elif isinstance(data, dict):
                # Alte Logik als Fallback, falls sich die API ändert
                if "data" in data and "categories" in data["data"]:
                     for cat in data["data"]["categories"]:
                        all_raw_offers.extend(cat.get("offers", []))
                elif "offers" in data:
                    all_raw_offers.extend(data["offers"])

            if not all_raw_offers:
                print("   ⚠️ Keine Daten extrahiert.")
                continue

            print(f"   ✅ Durchsuche {len(all_raw_offers)} Angebote nach Bier...")

            for offer in all_raw_offers:
                try:
                    # Kaufland hat manchmal 'title' und manchmal 'name'
                    title = offer.get("title") or offer.get("name") or ""
                    subtitle = offer.get("subtitle", "")
                    full_name = f"{title} {subtitle}".strip()
                    
                    name_lower = full_name.lower()
                    is_match = any(k in name_lower for k in bier_keywords)
                    is_ignored = any(k in name_lower for k in ignore_keywords)
                    
                    if is_match and not is_ignored:
                        price = offer.get("price", 0.0)
                        unit = offer.get("unit", "")
                        
                        print(f"   🍺 Gefunden: {full_name} für {price}€")
                        
                        bier_data.append({
                            "supermarkt": "Kaufland",
                            "name": full_name,
                            "preis": float(price),
                            "menge": unit,
                            "datum": datetime.date.today().isoformat()
                        })
                        
                except Exception as e:
                    continue
            
            if bier_data:
                break 

        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            continue

    print(f"✅ Fertig. {len(bier_data)} Angebote bei Kaufland gefunden.")
    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
