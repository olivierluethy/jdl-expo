# wikipedia.py
# Dieses Skript holt das Hauptbild eines Ortes von Wikipedia anhand des Ortsnamens.
# Es wird die Wikipedia-API verwendet, um die Bildinformationen abzurufen.
#--- Imports ---
# Benötigte Bibliothek: requests (installierbar via pip)
# pip install requests
#--- Funktion um Bild-URL zu holen ---
# Das Ziel ist es, für jeden Künstler auf YouTube, für die Tabelle artists, das Bild zu holen und den Link zur DB speichern. Dazu wird die Wikipedia-API abgefragt, um die Bildinformationen zu erhalten. Wenn ein Originalbild vorhanden ist, wird dessen URL zurückgegeben. Andernfalls wird versucht, eine alternative Bildquelle zu finden.

import requests

def get_place_image(place_name):
    # 1) Von Wikipedia den Bild-Dateinamen holen
    wp_url = "https://en.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "OrtAPI/1.0 (kontakt@example.com)"
    }

    wp_params = {
        "action": "query",
        "titles": place_name,
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "origin": "*"
    }

    wp_response = requests.get(wp_url, params=wp_params, headers=headers)
    try:
        wp_data = wp_response.json()
    except:
        print("Wikipedia JSON Fehler:", wp_response.text)
        return None

    pages = wp_data.get("query", {}).get("pages", {})

    file_url = None
    for _, page in pages.items():
        if "original" in page:
            file_url = page["original"]["source"]  # schon Original
            return file_url  # fertig!

    # Wenn kein Original-Bild da ist → versuche Datei über images-Liste zu finden
    # Dann muss über Commons die Originaldatei geholt werden
    img_url = None
    for _, page in pages.items():
        if "pageimages" in page:
            # Fallback
            img_url = page["pageimages"].get("source")
            return img_url

    return None


# Testen:
image_url = get_place_image("")
print("Bild URL:", image_url)
