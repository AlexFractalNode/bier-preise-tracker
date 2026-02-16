from curl_cffi import requests
from bs4 import BeautifulSoup
import datetime
import time
import random
import os

def get_netto_prices():
    url = "https://www.netto-online.de/filialangebote"
    
    # Erweiterte Header, um wie ein echter Mac auszusehen
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.netto-online.de/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    # Fallback für Zwickau, falls Secret leer
    store_id = '5872'
    
    # Cookie aus Secret laden (falls vorhanden)
    cookies = {}
    cookie_string = os.environ.get("NETTO_COOKIE")
    if cookie_string:
        try:
            for item in cookie_string.split(';'):
                if '=' in item:
                    k, v = item.strip().split('=', 1)
                    cookies[k] = v
        except:
            pass
            
    # WICHTIG: Store ID muss gesetzt sein
    if 'netto_user_stores_id' not in cookies:
        cookies['netto_user_stores_id'] = store_id

    print(f"📡 Netto (Safari-Mode): {url} (Store: {cookies.get('netto_user_stores_id')})")
    
    try:
        # Wir tarnen uns als Safari Browser
        session = requests.Session(impersonate="safari15_5")
        
        # Cookies setzen
        for k, v in cookies.items():
            session.cookies.set(k, v, domain=".netto-online.de")

        time.sleep(random.uniform(2, 5))
        response = session.get(url, headers=headers, timeout=30)
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 403:
            print("❌ Zugriff verweigert (403). IP evtl. geblockt.")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Prüfung: Sind wir auf der richtigen Seite?
        if "Filiale wählen" in response.text:
            print("⚠️ Umleitung auf Filialfinder. Cookie ignoriert.")
            return []

    except Exception as e:
        print(f"❌ Fehler: {e}")
        return []

    # Daten extrahieren
    bier_data = []
    # Deine Keywords (erweitert um Mixery auszuschließen wenn nötig, aber wir haben ja den Cleaner)
    bier_keywords = [
        "pils", "helles", "weizen", "bier", "lager", "radler", "export", "kasten", 
        "ur-krostitzer", "sternquell", "radeberger", "feldschlößchen", "freiberger", 
        "wernesgrüner", "paulaner", "krombacher", "beck's", "hasseröder", "mixery"
    ]

    product_tiles = soup.find_all('div', class_='product-list__item')
    print(f"🔍 Elemente gefunden: {len(product_tiles)}")

    for tile in product_tiles:
        try:
            title_tag = tile.find('span', class_='product__title')
            if not title_tag: continue
            name = title_tag.text.strip()
            
            price_tag = tile.find(class_='product__current-price')
            if not price_tag: continue
            
            # Preis reinigen
            raw_price = price_tag.text.replace('*', '').replace('\n', '').replace('\r', '').strip()
            
            if any(k in name.lower() for k in bier_keywords):
                print(f"   🍺 Gefunden: {name} -> {raw_price}")
                bier_data.append({
                    "supermarkt": "Netto",
                    "name": name,
                    "preis": raw_price,
                    "menge": tile.find('span', class_='product-property__bundle-text').text.strip() if tile.find('span', class_='product-property__bundle-text') else "",
                    "datum": datetime.date.today().isoformat()
                })
        except:
            continue

    return bier_data
