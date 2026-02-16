import json
import os
import pandas as pd
from jinja2 import Template
from datetime import datetime
import re

def parse_menge(menge_str):
    """
    Extrahiert Liter-Anzahl aus Strings wie '20 x 0,5 l', '0,5 l' oder '5 Liter'.
    Gibt die Gesamtmenge in Litern zurück.
    """
    if not isinstance(menge_str, str):
        return None
    
    menge_str = menge_str.lower().replace(',', '.').strip()
    
    # Fall 1: Kasten "20 x 0.5 l"
    # Regex Erklärung: 
    # (\d+)   -> Suche eine Zahl (Gruppe 1: Anzahl)
    # \s*x\s* -> Suche ein 'x' mit beliebig viel Leerzeichen drumherum
    # ([\d.]+) -> Suche eine Zahl mit Punkt (Gruppe 2: Volumen pro Flasche)
    match_kasten = re.search(r'(\d+)\s*x\s*([\d.]+)', menge_str)
    if match_kasten:
        anzahl = float(match_kasten.group(1))
        volumen = float(match_kasten.group(2))
        return anzahl * volumen

    # Fall 2: Einzelflasche "0.5 l" oder "5 l"
    match_single = re.search(r'([\d.]+)\s*l', menge_str)
    if match_single:
        return float(match_single.group(1))

    return None

def build_html():
    # 1. Daten laden
    data_path = 'data/preise.json'
    output_dir = 'public'
    output_file = os.path.join(output_dir, 'index.html')
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    products = []
    if data:
        df = pd.DataFrame(data)
        
        # --- CLEANING: Preise fixen ---
        df['preis'] = df['preis'].astype(str)
        df['preis'] = df['preis'].str.replace('.-', '.00', regex=False)
        df['preis'] = df['preis'].str.replace(',', '.', regex=False)
        df['preis'] = pd.to_numeric(df['preis'], errors='coerce')
        df = df.dropna(subset=['preis'])

        # --- CLEANING: Softdrinks rauswerfen ---
        # Wir definieren eine "Blacklist"
        verbotene_woerter = ["cola", "fanta", "sprite", "mezzo", "limo", "saft", "wasser", "energy", "mate"]
        # Wir behalten nur Zeilen, in denen KEINES der verbotenen Wörter vorkommt
        # lambda x: Überprüft für jeden Namen x, ob ein verbotenes Wort enthalten ist
        maske = df['name'].apply(lambda x: not any(bad in x.lower() for bad in verbotene_woerter))
        df = df[maske]

        # --- FEATURE ENGINEERING: Literpreis ---
        # 1. Gesamtvolumen berechnen (mit unserer Regex Funktion)
        df['volumen_liter'] = df['menge'].apply(parse_menge)
        
        # 2. Literpreis berechnen (Preis / Volumen)
        # Wir runden auf 2 Nachkommastellen
        df['literpreis'] = (df['preis'] / df['volumen_liter']).round(2)

        # Sortieren: Erst nach Literpreis (das ist der wahre Vergleich!), dann Preis
        # Produkte ohne Volumen (NaN) landen hinten
        df = df.sort_values(by=['literpreis', 'preis'], na_position='last')
        
        products = df.to_dict(orient='records')

    # 3. HTML Template (angepasst für Literpreis)
    template_str = """
    <!DOCTYPE html>
    <html lang="de" data-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🍺 Bier-Preise Zwickau</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
        <style>
            .billig { color: #2ecc71; font-weight: bold; }
            .teuer { color: #e74c3c; }
            .literpreis { font-size: 0.85em; color: #888; }
            td { vertical-align: middle; }
        </style>
    </head>
    <body>
        <main class="container">
            <hgroup>
                <h1>🍺 Zwickauer Bier-Tracker</h1>
                <h2>Die ehrlichsten Preise der Stadt (nach Liter sortiert)</h2>
            </hgroup>
            <p>Zuletzt aktualisiert: {{ timestamp }}</p>
            <figure>
                <table role="grid">
                    <thead>
                        <tr>
                            <th>Bier</th>
                            <th>Menge</th>
                            <th>Preis</th>
                            <th>Literpreis</th> <th>Markt</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in products %}
                        <tr>
                            <td>{{ p.name }}</td>
                            <td>{{ p.menge }}</td>
                            <td><strong>{{ "%.2f"|format(p.preis) }} €</strong></td>
                            <td>
                                {% if p.literpreis and p.literpreis > 0 %}
                                    <span class="literpreis">{{ "%.2f"|format(p.literpreis) }} €/l</span>
                                {% else %}
                                    <span class="meta">-</span>
                                {% endif %}
                            </td>
                            <td>{{ p.supermarkt }}</td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5">Kein Bier vor vier (oder keine Daten).</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </figure>
            <footer><small>Erstellt mit Python & GitHub Actions</small></footer>
        </main>
    </body>
    </html>
    """

    template = Template(template_str)
    html_output = template.render(
        products=products,
        timestamp=datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Webseite generiert: {output_file}")

if __name__ == "__main__":
    build_html()
