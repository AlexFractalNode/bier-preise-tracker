import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime

def get_netto_prices(store_id="8062"): # 8062 ist oft Teil der PLZ oder interne ID
    # 1. URL für Filialangebote
    url = "https://www.netto-online.de/filialangebote"
    
    # 2. WICHTIG: Cookies setzen, um die Filiale zu simulieren
    # Ohne das bekommst du nur eine "Filiale wählen" Seite
    cookies = {
        '5872': store_id,  # Das sagt dem Server: "Ich bin in diesem Markt"
        # Optional: Manchmal braucht man auch eine PLZ im Cookie, 
        # aber oft reicht die Store-ID, die Netto beim ersten Besuch setzt.
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Lade Angebote für Store ID {store_id}...")
    response = requests.get(url, headers=headers, cookies=cookies)
    
    if response.status_code != 200:
        print("Fehler beim Laden der Seite")
        return []

    # 3. HTML Parsen
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Alle Produkte finden
    product_tiles = soup.find_all('div', class_='product-list__item')
    
    bier_data = []
    
    # Keywords, nach denen wir suchen (um Waschmittel etc. auszuschließen)
    bier_keywords = ["Pils", "Helles", "Weizen", "Bier", "Lager", "Radler", "Export", "Kasten"]

    for tile in product_tiles:
        try:
            # Titel extrahieren
            title_tag = tile.find('span', class_='product__title')
            if not title_tag:
                continue
            name = title_tag.text.strip()
            
            # Einfacher Filter: Ist es Bier?
            if not any(keyword.lower() in name.lower() for keyword in bier_keywords):
                continue

            # Preis extrahieren
            # Netto nutzt <ins> für Aktionspreise und div für normale
            price_tag = tile.find(class_='product__current-price')
            if price_tag:
                # Der Preis kommt oft als "9. 49 *" -> wir reinigen das
                raw_price = price_tag.text.replace('*', '').strip()
                # Entferne Zeilenumbrüche, falls vorhanden
                price = float(raw_price.replace('\n', '').replace('\r', ''))
            else:
                price = 0.0

            # Menge extrahieren (z.B. "20 x 0,5 l")
            amount_tag = tile.find('span', class_='product-property__bundle-text')
            amount = amount_tag.text.strip() if amount_tag else "n/a"

            # Pfand extrahieren (wichtig für Endpreis)
            deposit_tag = tile.find('span', class_='product-property__deposit-text')
            deposit = deposit_tag.text.strip() if deposit_tag else "0"

            bier_data.append({
                "supermarkt": "Netto Marken-Discount",
                "name": name,
                "preis": price,
                "menge": amount,
                "datum": datetime.date.today().isoformat(),
                "pfand_info": deposit
            })
            
        except Exception as e:
            print(f"Fehler bei einem Produkt: {e}")
            continue

    return bier_data

if __name__ == "__main__":
    # Testlauf
    angebote = get_netto_prices()
    df = pd.DataFrame(angebote)
    print(df)
    # Speichern für später
    # df.to_csv("netto_bier.csv", index=False)
