# main.py
# Dieses Skript holt die Dauer von YouTube-Videos anhand ihrer IDs
# und generiert SQL-Update-Statements, die in eine Datei geschrieben werden.
# Es wird die Bibliothek yt_dlp verwendet, um die Videoinformationen abzurufen.
## Benötigte Bibliothek: yt_dlp (installierbar via pip)
# pip install yt_dlp
#--- Imports ---
# Das Problem war, dass die YouTube-Videos vorher falsch extrahiert wurden, weil bei einigen Videodauern auf der Seite ein Musik-Symbol angezeigt wurde. Daraufhin wurde die Dauer zum Teil einfach leer extrahiert. Daher wurde das Extraktionsskript so angepasst, dass die Dauer immer korrekt geholt wird – unabhängig vom Musik-Symbol. Aber damit war nicht einfach Schluss: Die Dauer bei den YouTube-Videos, die eben keine Dauer hatten, musste wieder gefüllt werden. Dazu wurden alle YouTube-Video-IDs aus der DB geholt, zu denen keine Dauer besteht. Diese IDs wurden dann an die Schnittstelle übergeben, um die Dauer aus dem jeweiligen Video zu holen. Anschließend wurde daraus ein fertiges SQL-Update-Statement erstellt, um die Spalte, zu der keine Dauer besteht, für alle betroffenen Videos entsprechend zu füllen.

import yt_dlp
import os
import re

# --- Rohinput: so wie du ihn hast ---
raw_input = """
('xyno53dCO7Q'),
('I2XfVml6o24'),
('QUzCFEJh8-I');
"""

# --- IDs extrahieren ---
video_ids = re.findall(r"\('([^']+)'\)", raw_input)

# --- Datei für die SQL Statements ---
base_filename = 'update_durations.txt'
output_file = os.path.join(os.path.dirname(__file__), base_filename)

# Prüfen, ob Datei existiert, und ggf. inkrementieren
counter = 1
while os.path.exists(output_file):
    name, ext = os.path.splitext(base_filename)
    output_file = os.path.join(os.path.dirname(__file__), f"{name}{counter}{ext}")
    counter += 1

# --- Funktion um Dauer in Sekunden zu holen ---
def get_duration_seconds(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'quiet': True, 'skip_download': True, 'forcejson': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return int(info['duration'])

# --- SQL Statements generieren ---
with open(output_file, 'w', encoding='utf-8') as f:
    for vid in video_ids:
        try:
            duration_sec = get_duration_seconds(vid)
            sql = f"UPDATE youtube_video_cache SET duration = {duration_sec} WHERE youtube_id = '{vid}';\n"
            f.write(sql)
            print(f"Processed {vid}: {duration_sec} seconds")
        except Exception as e:
            print(f"Fehler bei {vid}: {e}")
            f.write(f"-- Fehler bei {vid}: {e}\n")

print(f"Fertig! SQL Statements wurden in '{output_file}' gespeichert.")