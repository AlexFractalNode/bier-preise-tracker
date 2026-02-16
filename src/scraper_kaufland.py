from curl_cffi import requests
import json
import datetime
import time
import random

def get_kaufland_prices():
    # Wir probieren Varianten durch, da Kaufland oft Abkürzungen wie "str" nutzt
    # Zwickau Äußere Dresdner Str. ist die vermutete Filiale
    possible_stores = [
        "zwickau-aussere-dresdner-str",      # Wahrscheinlichste Variante
        "zwickau-aussere-dresdner-strasse",  # Lange Schreibweise
        "de-zwickau-aussere-dresdner-str",   # Mit Länderkürzel
    ]
    
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://filiale.kaufland.de/",
    }

    bier_data = []
    
    # Keywords
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mix"
    ]
    ignore_keywords = ["alkoholfrei", "malztrunk", "fassbrause"]

    for store_name in possible_stores:
        url = f"https://filiale.kaufland.de/.kloffers.storeName={store_name}.json"
        print(f"📡 Teste Kaufland URL: {url}")
        
        try:
            time.sleep(random.uniform(1, 3))
            response = session.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"   ❌ Status {response.status_code} - Weiter...")
                continue
            
            # Prüfen, ob die Antwort leer ist oder HTML enthält (statt JSON)
            if not response.text or response.text.strip().startswith("<"):
                print("   ❌ Antwort ist kein gültiges JSON (vermutlich HTML Fehlerseite).")
                continue

            data = response.json()
            
            # Checken, ob wir Kategorien haben
            if "data" not in data or "categories" not in data["data"]:
                print("   ⚠️ JSON erhalten, aber keine Kategorien gefunden (leeres Angebot?).")
                # Debugging: Zeig uns die Schlüssel der Antwort
                print(f"   Keys in Antwort: {list(data.keys())}")
                continue

            print(f"   ✅ Treffer! Gültige Daten für '{store_name}' gefunden.")
            
            # --- PARSING ---
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
                            price = offer.get("price", 0.0)
                            unit = offer.get("unit", "")
                            
                            # Kaufland hat oft seltsame Einheiten im Titel, wir nehmen 'unit' wenn da,
                            # ansonsten versuchen wir, es aus dem Titel zu raten.
                            
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
            
            # Wenn wir erfolgreich waren, brechen wir die Schleife über die Store-Namen ab
            if bier_data:
                break
            else:
                print("   ⚠️ Zwar Daten geladen, aber kein Bier gefunden. Probiere nächste URL...")

        except Exception as e:
            print(f"   ❌ Fehler bei diesem Versuch: {e}")
            continue

    print(f"✅ Fertig. {len(bier_data)} Angebote bei Kaufland gefunden.")
    return bier_data

if __name__ == "__main__":
    get_kaufland_prices()
