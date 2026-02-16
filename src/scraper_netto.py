from curl_cffi import requests # Wir nutzen jetzt curl_cffi statt normalem requests!
from bs4 import BeautifulSoup
import datetime
import time
import random
import os

def get_netto_prices():
    url = "https://www.netto-online.de/filialangebote"
    
    # 1. Store ID setzen (Zwickau)
    # Das ist die wichtigste Info. Wir setzen sie hart, falls kein Secret da ist.
    store_id = '5872' 
    
    print(f"📡 Starte Stealth-Request an: {url}")
    print(f"🍪 Setze Store-ID: {store_id}")
    
    try:
        # 2. Session mit Browser-Tarnung erstellen
        # impersonate="chrome120" sorgt dafür, dass der Server denkt, 
        # wir wären ein echter Chrome Browser.
        session = requests.Session(impersonate="chrome120")
        
        # 3. Cookie setzen
        # Wir setzen den Cookie direkt in der Session
        session.cookies.set("netto_user_stores_id", store_id, domain=".netto-online.de")
        
        # Optional: Falls du den riesigen Cookie-String aus dem Secret hast, 
        # versuchen wir, ihn zusätzlich zu parsen (für Anti-Bot Token)
        full_cookie = os.environ.get("NETTO_COOKIE")
        if full_cookie:
            print("🍪 Versuche erweiterten Cookie aus Secrets zu laden...")
            for item in full_cookie.split(';'):
                if '=' in item:
                    try:
                        key, val = item.strip().split('=', 1)
                        session.cookies.set(key, val, domain=".netto-online.de")
                    except:
                        pass

        # 4. Request senden
        # timeout etwas höher setzen
        time.sleep(random.uniform(2, 5)) 
        response = session.get(url, timeout=30)
        
        print(f"✅ Status Code: {response.status_code}")
        
        # HTML parsen
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.text.strip() if soup.title else "Kein Titel"
        print(f"📄 Seitentitel: {page_title}")
        
        if response.status_code == 403 or "Access Denied" in page_title:
            print("❌ Zugriff verweigert! Der Bot-Schutz hat uns erkannt.")
            return []

        if "Filiale wählen" in response.text or "Markt wählen" in response.text:
            print("⚠️ Cookie ignoriert. Wir sind auf der Filial-Auswahl-Seite.")
            # Fallback: Manchmal hilft es, die PLZ an die URL anzuhängen (funktioniert bei manchen Shops)
            return []

    except Exception as e:
        print(f"❌ Kritischer Fehler beim Request: {e}")
        return []

    # 5. Daten extrahieren
    product_tiles = soup.find_all('div', class_='product-list__item')
    print(f"🔍 Habe {len(product_tiles)} Produkte gefunden.")
    
    bier_data = []
    # Erweiterte Keyword-Liste
    bier_keywords = ["Pils", "Helles", "Weizen", "Bier", "Lager", "Radler", "Export", "Kasten", "Ur-Krostitzer", "Sternquell", "Radeberger", "Feldschlößchen", "Freiberger", "Wernesgrüner", "Paulaner"]

    for tile in product_tiles:
        try:
            title_tag = tile.find('span', class_='product__title')
            if not title_tag: continue
            name = title_tag.text.strip()
            
            # Suche nach Preis (Aktion oder Normal)
            price_container = tile.find(class_='product__current-price')
            if not price_container: continue

            # Preis säubern
            raw_text = price_container.text.replace('*', '').replace('\n', '').replace('\r', '').strip()
            
            # Wenn Preis leer, weitermachen
            if not raw_text: continue
            
            # Ist es Bier?
            if any(k.lower() in name.lower() for k in bier_keywords):
                print(f"🍺 TREFFER: {name} für {raw_text}")
                
                bier_data.append({
                    "supermarkt": "Netto",
                    "name": name,
                    "preis": raw_text,
                    "datum": datetime.date.today().isoformat()
                })

        except Exception as e:
            continue

    return bier_data
