from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # Wir testen die wahrscheinlichste URL-Variante für Zwickau
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
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery"
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
            
            # --- HIER IST DER FIX START ---
            all_raw_offers = []
            
            # Fall A: Die API liefert direkt eine Liste von Kategorien (Dein Fall)
            if isinstance(data, list):
                print(f"   ℹ️ Struktur erkannt: Liste mit {len(data)} Kategorien.")
                for category in data:
                    # Jedes Element sollte ein 'offers'-Feld haben
                    if isinstance(category, dict):
                        all_raw_offers.extend(category.get("offers", []))
            
            # Fall B: Die API liefert ein Objekt (Andere Regionen/Versionen)
            elif isinstance(data, dict):
                print("   ℹ️ Struktur erkannt: Dictionary.")
                if "data" in data and "categories" in data["data"]:
                    for cat in data["data"]["categories"]:
                        all_raw_offers.extend(cat.get("offers", []))
                elif "offers" in data:
                    all_raw_offers.extend(data["offers"])

            if not all_raw_offers:
                print("   ⚠️ Keine Angebote in der Liste gefunden.")
                continue
            # --- HIER IST DER FIX ENDE ---

            print(f"   ✅ {len(all_raw_offers)} Roh-Angebote geladen. Filtere nach Bier...")

            for offer in all_raw_offers:
                try:
                    title = offer.get("title", "")
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
                break # Wenn wir Daten haben, hören wir auf URLs zu testen

        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            continue

    print(f"✅ Fertig. {len(bier_data)} Angebote bei Kaufland gefunden.")
    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
