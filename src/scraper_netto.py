import requests
from bs4 import BeautifulSoup
import datetime
import time
import random
import os

def get_netto_prices():
    url = "https://www.netto-online.de/filialangebote"
    
    # --- KORREKTUR 1: Variable initialisieren ---
    # Wir erstellen ein leeres Wörterbuch, bevor wir versuchen, es zu füllen.
    cookies = {} 
    
    # Versuche Cookie aus Environment Variable zu holen (GitHub Secret)
    cookie_string = os.environ.get("NETTO_COOKIE")
      
    if cookie_string:
        print("🍪 Nutze Cookie aus GitHub Secrets!")
        try:
            # Den String in ein Dictionary umwandeln
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    cookies[name] = value
        except Exception as e:
            print(f"Fehler beim Parsen des Cookies: {e}")
            # Falls das Parsen fehlschlägt, ist cookies immer noch {}, also leer.
    
    # --- KORREKTUR 2: Prüfen und Fallback setzen ---
    # Wenn cookies leer ist (kein Secret oder Fehler), nutzen wir den Fallback.
    if not cookies:
        print("⚠️ Kein Secret gefunden oder leer. Nutze Fallback-ID.")
        # Hier die ID aus deinem Screenshot (5872) nutzen!
        cookies = {'netto_user_stores_id': '5872'} 
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.netto-online.de/",
        "Cache-Control": "no-cache", 
    }

    print(f"📡 Frage URL ab: {url}")
    print(f"🍪 Genutzte Cookies (Store ID): {cookies.get('netto_user_stores_id', 'Unbekannt')}")
    
    try:
        time.sleep(random.uniform(1, 3))
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

        # Titel ausgeben zur Kontrolle
        soup = BeautifulSoup(response.text, 'html.parser')
        page_title = soup.title.text.strip() if soup.title else "Kein Titel"
        print(f"📄 Seitentitel geladen: {page_title}")
        print(f"✅ Status Code: {response.status_code}")
        
        if "Filiale wählen" in response.text or "Markt wählen" in response.text:
            print("⚠️ WARNUNG: Lande auf der 'Filiale wählen' Seite. Cookie wurde ignoriert oder ist ungültig.")
            return []

    except Exception as e:
        print(f"❌ Netzwerkfehler: {e}")
        return []

    # Elemente finden
    product_tiles = soup.find_all('div', class_='product-list__item')
    
    print(f"🔍 Habe {len(product_tiles)} Produkt-Kacheln gefunden.")
    
    bier_data = []
    # Erweiterte Liste für genauere Treffer
    bier_keywords = ["Pils", "Helles", "Weizen", "Bier", "Lager", "Radler", "Export", "Kasten", "Ur-Krostitzer", "Sternquell", "Radeberger", "Feldschlößchen", "Freiberger"]

    for tile in product_tiles:
        try:
            title_tag = tile.find('span', class_='product__title')
            if not title_tag: continue
            name = title_tag.text.strip()
            
            # Preis suchen (Aktion oder Normal)
            price_container = tile.find(class_='product__current-price') 
            if not price_container: continue

            # Preis säubern: "10. 99 *" -> "10.99"
            # Wir entfernen Zeilenumbrüche und das Sternchen
            raw_text = price_container.text.replace('*', '').replace('\n', '').replace('\r', '').strip()
            
            # Wenn der Preis leer ist, überspringen
            if not raw_text: continue
            
            # Filter: Ist es Bier?
            if any(k.lower() in name.lower() for k in bier_keywords):
                print(f"🍺 TREFFER: {name} für {raw_text}")
                
                bier_data.append({
                    "supermarkt": "Netto",
                    "name": name,
                    "preis": raw_text,
                    "datum": datetime.date.today().isoformat()
                })

        except Exception as e:
            # Fehler bei einem einzelnen Produkt ignorieren, weiter zum nächsten
            continue

    return bier_data
