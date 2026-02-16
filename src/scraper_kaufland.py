from curl_cffi import requests
import json
import datetime
import re
import time
import random

def get_kaufland_prices():
    # 1. Die versteckte API URL für Zwickau (Äußere Dresdner Str.)
    # Falls das nicht deine Filiale ist, müssen wir "de-zwickau-aussere-dresdner-strasse" austauschen.
    store_name = "de-zwickau-aussere-dresdner-strasse"
    url = f"https://filiale.kaufland.de/.kloffers.storeName={store_name}.json"
    
    print(f"📡 Kaufland API abfragen: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://filiale.kaufland.de/",
    }
    
    try:
        # Tarnung einschalten
        session = requests.Session(impersonate="chrome120")
        time.sleep(random.uniform(1, 3))
        
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Kaufland API Fehler: Status {response.status_code}")
            return []
            
        data = response.json()
        
    except Exception as e:
        print(f"❌ Netzwerkfehler bei Kaufland: {e}")
        return []

    # 2. Daten verarbeiten
    bier_data = []
    
    # Keywords für Bier
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mix"
    ]
    
    # Keywords zum Ausschluss
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    # Die JSON Struktur von Kaufland durchsuchen
    # Die Angebote stecken oft in Kategorien. Wir suchen einfach alles ab.
    if "data" in data and "categories" in data["data"]:
        categories = data["data"]["categories"]
        
        for cat in categories:
            # Wir gehen durch alle Angebote in dieser Kategorie
            for offer in cat.get("offers", []):
                try:
                    title = offer.get("title", "")
                    subtitle = offer.get("subtitle", "")
                    full_name = f"{title} {subtitle}".strip()
                    
                    # Filter prüfen
                    name_lower = full_name.lower()
                    is_match = any(k in name_lower for k in bier_keywords)
                    is_ignored = any(k in name_lower for k in ignore_keywords)
                    
                    if is_match and not is_ignored:
                        # Preis holen (ist im JSON eine Zahl, z.B. 8.99)
                        price = offer.get("price", 0.0)
                        
                        # Menge holen (steht in "unit", z.B. "je Ka. 20 x 0,5-l-Fl.")
                        unit = offer.get("unit", "")
                        
                        print(f"🍺 Kaufland Treffer: {full_name} für {price}€")
                        
                        bier_data.append({
                            "supermarkt": "Kaufland",
                            "name": full_name,
                            "preis": float(price),
                            "menge": unit,
                            "datum": datetime.date.today().isoformat()
                        })
                        
                except Exception as e:
                    continue

    print(f"✅ {len(bier_data)} Angebote bei Kaufland gefunden.")
    return bier_data

if __name__ == "__main__":
    # Testlauf lokal
    print(get_kaufland_prices())
