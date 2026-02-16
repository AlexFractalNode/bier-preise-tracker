import json
import os
import pandas as pd
from jinja2 import Template
from datetime import datetime

def build_html():
    # 1. Daten laden
    data_path = 'data/preise.json'
    output_dir = 'public'
    output_file = os.path.join(output_dir, 'index.html')
    
    # Sicherstellen, dass der Output-Ordner existiert
    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    # 2. Daten mit Pandas aufbereiten (optional, aber praktisch für Sortierung)
    if data:
        df = pd.DataFrame(data)
        
        # --- FIX: Daten bereinigen BEVOR wir rechnen ---
        # 1. Sicherstellen, dass die Spalte Text ist
        df['preis'] = df['preis'].astype(str)
        
        # 2. "1.-" oder "1,-" ersetzen durch "1.00"
        # Regex=False ist schneller und sicherer für einfache Ersetzungen
        df['preis'] = df['preis'].str.replace('.-', '.00', regex=False)
        df['preis'] = df['preis'].str.replace(',-', '.00', regex=False)
        
        # 3. Deutsches Komma gegen Punkt tauschen
        df['preis'] = df['preis'].str.replace(',', '.', regex=False)
        
        # 4. Leerraum entfernen und in Zahl umwandeln
        df['preis'] = pd.to_numeric(df['preis'].str.strip(), errors='coerce')
        
        # 5. Zeilen löschen, wo der Preis ungültig war (NaN)
        df = df.dropna(subset=['preis'])
        # --- FIX ENDE ---

        # Sortieren: Erst nach Preis, dann nach Name
        df = df.sort_values(by=['preis', 'name'])
        products = df.to_dict(orient='records')
    else:
        products = []
        
    # 3. Das HTML Template (Jinja2 + Pico.css für schnelles Design)
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
            .meta { font-size: 0.8em; color: #888; }
            td { vertical-align: middle; }
        </style>
    </head>
    <body>
        <main class="container">
            <hgroup>
                <h1>🍺 Zwickauer Bier-Tracker</h1>
                <h2>Die aktuellen Angebote bei Netto (Filiale 5872)</h2>
            </hgroup>

            <p>Zuletzt aktualisiert: {{ timestamp }}</p>

            <figure>
                <table role="grid">
                    <thead>
                        <tr>
                            <th scope="col">Bier / Produkt</th>
                            <th scope="col">Menge</th>
                            <th scope="col">Preis</th>
                            <th scope="col">Markt</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for p in products %}
                        <tr>
                            <td>{{ p.name }}</td>
                            <td>{{ p.menge }}</td>
                            <td class="{{ 'billig' if p.preis < 10 else '' }}">
                                {{ "%.2f"|format(p.preis) }} €
                            </td>
                            <td>{{ p.supermarkt }}</td>
                        </tr>
                        {% else %}
                        <tr>
                            <td colspan="4">Keine Bier-Angebote gefunden (oder der Scraper hat Durst).</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </figure>
            
            <footer>
                <small>Erstellt mit Python & GitHub Actions. <a href="https://github.com/AlexFractalNode/bier-preise-tracker">Code auf GitHub</a></small>
            </footer>
        </main>
    </body>
    </html>
    """

    # 4. Rendern
    template = Template(template_str)
    html_output = template.render(
        products=products,
        timestamp=datetime.now().strftime("%d.%m.%Y um %H:%M Uhr")
    )

    # 5. Speichern
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Webseite generiert: {output_file}")

if __name__ == "__main__":
    build_html()
