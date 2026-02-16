from curl_cffi import requests
import json
import datetime
import random
import time

def get_kaufland_prices():
    # Wir nutzen die offizielle Mobile App API (V2)
    # Das ist viel stabiler als die Webseite.
    
    # Mögliche IDs für Zwickau (aus deinen Logs/Schnipseln)
    # 3240783 = Zwickau, Äußere Dresdner Str. (Sehr wahrscheinlich korrekt)
    # 375483 = Andere ID aus Log
    store_ids = ["3240783", "375483"]
    
    session = requests.Session(impersonate="chrome120")
    headers = {
        "User-Agent": "Kaufland-App/42.0 (Android; 10; Mobile)",
        "Accept-Language": "de-DE",
        "Content-Type": "application/json"
    }

    bier_data = []
    
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery", "köstritzer"
    ]
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    for store_id in store_ids:
        # V2 API Endpoint
        url = f"https://api.kaufland.com/v2/offers?storeId={store_id}&limit=300&offset=0&types=loyalty,mm"
        print(f"📡 Prüfe Kaufland API (V2) für Store {store_id}...")
        
        try:
            time.sleep(random.uniform(1, 2))
            response = session.get(url, headers=headers, timeout=20)
            
            if response.status_code != 200:
                print(f"   ❌ Fehler Status: {response.status_code}")
                continue
                
            data = response.json()
            
            # Die Angebote stecken direkt in einer Liste
            if not isinstance(data, list):
                print("   ⚠️ Unerwartetes Format (keine Liste).")
                continue
                
            print(f"   📦 {len(data)} Angebote geladen.")
            
            found_beers = 0
            for offer in data:
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
                    
                    # Wenn Unit leer ist, versuchen wir es aus dem quantity feld
                    if not unit and "quantity" in offer:
                        unit = offer["quantity"]

                    print(f"   🍺 Gefunden: {full_name} für {price}€")
                    
                    bier_data.append({
                        "supermarkt": "Kaufland",
                        "name": full_name,
                        "preis": float(price),
                        "menge": unit,
                        "datum": datetime.date.today().isoformat()
                    })
                    found_beers += 1
            
            if found_beers > 0:
                print(f"   ✅ Erfolg bei Store {store_id}!")
                break # Wir haben den richtigen Store gefunden

        except Exception as e:
            print(f"   ❌ Fehler: {e}")
            continue

    return bier_data

if __name__ == "__main__":
    # Testlauf
    print(get_kaufland_prices())
