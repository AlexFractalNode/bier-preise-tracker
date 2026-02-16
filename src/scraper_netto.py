import requests
from bs4 import BeautifulSoup
import datetime
import time
import random
import os

def get_netto_prices():
    url = "https://www.netto-online.de/filialangebote"
    
    # Versuche Cookie aus Environment Variable zu holen (GitHub Secret)
    cookie_string = os.environ.get("NETTO_COOKIE")
    
    cookies = {}
    if cookie_string:
        # Den String in ein Dictionary umwandeln
        print("🍪 Nutze Cookie aus GitHub Secrets!")
        try:
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies[name] = value
        except:
            print("Konnte Cookie nicht parsen, nutze Fallback")
    
    if not cookies:
        cookies = {'netto_user_store_id': '8062'}
        
    headers = {
        # Ein sehr gängiger User-Agent
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.netto-online.de/",
        "Cache-Control": "max-age=0",
    }

    print(f"📡 Frage URL ab: {url}")
    
    try:
        # Kleiner Sleep, um nicht zu aggressiv zu wirken
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        
        # DEBUGGING: Was haben wir bekommen?
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.text.strip() if soup.title else "Kein Titel"
        print(f"📄 Seitentitel: {page_title}")
        
        # Checken, ob wir auf der Filial-Auswahl gelandet sind
        if "Filiale wählen" in response.text or "Markt wählen" in response.text:
            print("⚠️ WARNUNG: Der Scraper ist auf der 'Filiale wählen' Seite gelandet. Cookie funktioniert nicht.")
            return []

    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
        return []

    # Alle Produkte finden (angepasst an deinen HTML Code)
    # Netto nutzt product-list__item ODER tile-container, wir suchen beides
    product_tiles = soup.find_all('div', class_='product-list__item')
    
    print(f"🔍 Habe {len(product_tiles)} Produkt-Kacheln gefunden.")
    
    bier_data = []
    bier_keywords = ["Pils", "Helles", "Weizen", "Bier", "Lager", "Radler", "Export", "Kasten", "Ur-Krostitzer", "Sternquell"]

    for tile in product_tiles:
        try:
            # Titel
            title_tag = tile.find('span', class_='product__title')
            if not title_tag: continue
            name = title_tag.text.strip()
            
            # Preis
            price_container = tile.find('ins', class_='product__current-price') # Aktionspreis
            if not price_container:
                price_container = tile.find('div', class_='product__current-price') # Normalpreis
            
            if not price_container: continue

            # Preis säubern (Netto macht oft: 10.<span class="small">99</span>)
            # Wir holen einfach allen Text und entfernen Umbrüche
            raw_price = price_container.text.strip().replace('\n', '').replace('*', '')
            
            # Filter
            if any(k.lower() in name.lower() for k in bier_keywords):
                print(f"🍺 BIER GEFUNDEN: {name} für {raw_price}")
                
                bier_data.append({
                    "supermarkt": "Netto",
                    "name": name,
                    "preis": raw_price,
                    "datum": datetime.date.today().isoformat()
                })

        except Exception as e:
            continue

    return bier_data
