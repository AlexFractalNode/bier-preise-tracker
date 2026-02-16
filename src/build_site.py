import json
import os
import pandas as pd
from jinja2 import Template
from datetime import datetime
import re


def parse_menge(menge_str):
    if not isinstance(menge_str, str):
        return None
    # NEU: Wir ersetzen Bindestriche durch Leerzeichen, damit "0,5-l" zu "0.5 l" wird
    menge_str = menge_str.lower().replace(',', '.').replace('-', ' ').strip()
    
    # Der Rest bleibt gleich
    match_kasten = re.search(r'(\d+)\s*x\s*([\d.]+)', menge_str)
    # ...
    if match_kasten:
        anzahl = float(match_kasten.group(1))
        volumen = float(match_kasten.group(2))
        return anzahl * volumen

    match_single = re.search(r'([\d.]+)\s*l', menge_str)
    if match_single:
        return float(match_single.group(1))

    return None

def build_html():
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
    min_literpreis = 999.0 # Startwert für Vergleich

    if data:
        df = pd.DataFrame(data)
        
        # --- CLEANING: Preise fixen ---
        df['preis'] = df['preis'].astype(str)
        # WICHTIG: Das hier repariert den "1.-" Fehler von Mixery/Netto
        df['preis'] = df['preis'].str.replace('.-', '.00', regex=False) 
        df['preis'] = df['preis'].str.replace(',-', '.00', regex=False)
        df['preis'] = df['preis'].str.replace(',', '.', regex=False)
        
        # Umwandeln und Fehler ignorieren (z.B. leere Preise)
        df['preis'] = pd.to_numeric(df['preis'], errors='coerce')
        df = df.dropna(subset=['preis'])
        
        verbotene_woerter = ["cola", "fanta", "sprite", "mezzo", "limo", "saft", "wasser", "energy", "mate"]
        maske = df['name'].apply(lambda x: not any(bad in x.lower() for bad in verbotene_woerter))
        df = df[maske]

        # --- FEATURE ENGINEERING ---
        df['volumen_liter'] = df['menge'].apply(parse_menge)
        df['literpreis'] = (df['preis'] / df['volumen_liter']).round(2)

        # --- NEU: Den günstigsten Literpreis finden ---
        if not df['literpreis'].dropna().empty:
            min_literpreis = df['literpreis'].min()

        df = df.sort_values(by=['literpreis', 'preis'], na_position='last')
        products = df.to_dict(orient='records')

    # 3. HTML Template (mit neuer CSS-Logik)
    template_str = """
    <!DOCTYPE html>
    <html lang="de" data-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🍺 Bier-Preise Zwickau</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
        <style>
            /* Design-Anpassungen */
            td { vertical-align: middle; }
            
            /* NEU: Klasse für Angebotspreis (immer grün) */
            .angebot-preis { 
                color: #2ecc71; /* Helles Grün */
                font-weight: bold;
            }

            /* NEU: Klasse für den absoluten Gewinner */
            .best-deal {
                color: #2ecc71; 
                font-weight: 800;
                text-decoration: underline;
                font-size: 1.1em;
            }
            
            .literpreis { font-size: 0.85em; color: #888; }
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
                            <th>Literpreis</th>
                            <th>Markt</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in products %}
                        <tr>
                            <td>{{ p.name }}</td>
                            <td>{{ p.menge }}</td>
                            
                            <td class="angebot-preis">
                                {{ "%.2f"|format(p.preis) }} €
                            </td>
                            
                            <td>
                                {% if p.literpreis and p.literpreis > 0 %}
                                    <span class="{{ 'best-deal' if p.literpreis == min_lp else 'literpreis' }}">
                                        {{ "%.2f"|format(p.literpreis) }} €/l
                                    </span>
                                {% else %}
                                    <span class="meta">-</span>
                                {% endif %}
                            </td>
                            
                            <td>{{ p.supermarkt }}</td>
                        </tr>
                        {% else %}
                        <tr><td colspan="5">Keine Daten gefunden.</td></tr>
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
    
    # NEU: Wir übergeben 'min_lp' (Minimum Literpreis) an das Template
    html_output = template.render(
        products=products,
        min_lp=min_literpreis, 
        timestamp=datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Webseite generiert: {output_file}")

if __name__ == "__main__":
    build_html()
