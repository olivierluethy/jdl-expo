import yt_dlp
import time
import requests
import re
import sys
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from unidecode import unidecode # <-- NEUER IMPORT

# --- KONFIGURATION ---
OUTPUT_SQL_FILE = "database/dumps/tunevote_artists_and_videos_insert.sql" # Die Datei, die automatisch erstellt wird
channels = ["https://www.youtube.com/playlist?list=UULkAepWjdylmXSltofFvsYQ"]
MAX_THREADS = 30  # Kann je nach Systemleistung angepasst werden.

# Optionen für detaillierte Abfrage (MIT FILTERN FÜR SHORTS/PREMIUM)
ydl_opts_details = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'ignoreerrors': True,
    # Filter hinzugefügt: Ignoriere Premium-Videos UND Videos kürzer als 60 Sekunden (Shorts)
    'match_filter': yt_dlp.match_filter_func('!is_premium & duration > 60'), 
}
# ----------------------

# --- NEUE HILFSFUNKTION: Channel-URL → Uploads-Playlist-URL umwandeln ---
class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def convert_channel_to_uploads_playlist(url):
    """Wandelt jede erdenkliche YouTube-Channel-URL in die Uploads-Playlist (UU…) um."""
    
    # 1. Schnell-Check: Schon eine Playlist? → direkt zurückgeben
    if "playlist?list=" in url:
        return url

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "no_warnings": True,
        "logger": SilentLogger(),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return url

            # yt-dlp gibt bei jedem Channel-Typ (auch /c/ und @) die channel_id zurück
            channel_id = info.get("channel_id") or info.get("id")
            if channel_id and channel_id.startswith("UC"):
                uploads_id = "UU" + channel_id[2:]
                return f"https://www.youtube.com/playlist?list={uploads_id}"
        except:
            pass

    # Letzter Notfall-Fallback: Manuell aus /c/ oder @ versuchen (sollte eigentlich nie nötig sein)
    # Aber für absolute Sicherheit:
    if "/c/" in url:
        handle = url.split("/c/")[-1].split("?")[0]
        # yt-dlp kann das auch, aber wir machen es nochmal explizit:
        try:
            test_url = f"https://www.youtube.com/@{handle}"
            return convert_channel_to_uploads_playlist(test_url)  # Rekursion einmal
        except:
            pass

    return url
# -----------------------------------------------------------------------

# --- KONFIGURATION ERWEITERN: Alle Channel-Varianten automatisch umwandeln ---
processed_channels = []
for original_url in channels:
    # Alle bekannten Channel-Formate erkennen
    if any(x in original_url for x in ["/channel/UC", "/c/", "@", "/user/"]):
        playlist_url = convert_channel_to_uploads_playlist(original_url)
        print(f"Channel erkannt → konvertiert zu Uploads-Playlist: {playlist_url}", file=sys.stderr)
        processed_channels.append(playlist_url)
    else:
        processed_channels.append(original_url)

channels = processed_channels
# -----------------------------------------------------------------------
# ---------------------------------------------------------------

# --- HILFSFUNKTIONEN (wie von Ihnen bereitgestellt) ---

def normalize_name(name):
    if not name:
        return ""
        
    # --- GEÄNDERT: Erst in ASCII umwandeln, dann normalisieren ---
    # Mylène Farmer -> Mylene Farmer
    # Rag'n'Bone Man -> Rag'n'Bone Man (Akzente weg, Sonderzeichen noch da)
    normalized = unidecode(name) 

    normalized = normalized.lower()
    # Diese Zeile ist jetzt sicherer, da die meisten Sonderzeichen weg sind
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized) 
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # Ergebnis für 'Mylène Farmer' wäre jetzt: 'mylene farmer'
    return normalized

def get_artist_image(artist_name):
    """Holt das Bild von Wikipedia (blockiert, wird im Thread ausgeführt)."""
    # ... (Diese Funktion bleibt unverändert) ...
    if not artist_name:
        return None
    
    wp_url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "ArtistImageFetcher/1.0 (your-email@example.com)"}
    
    # 1. Suche nach dem exakten Künstler-Seitentitel
    search_params = {
        "action": "query", "list": "search", "srsearch": artist_name,
        "format": "json", "srlimit": 1, "origin": "*"
    }
    try:
        search_resp = requests.get(wp_url, params=search_params, headers=headers, timeout=5)
        search_data = search_resp.json()
        searches = search_data.get("query", {}).get("search", [])
        if not searches: return None
        # Zugriff auf das Titel-Feld des ersten Suchergebnisses
        page_title = searches[0]["title"] 
        
        # 2. Hole Bild (original bevorzugt)
        img_params = {
            "action": "query", "titles": page_title, "format": "json",
            "prop": "pageimages", "piprop": "original", "origin": "*"
        }
        img_resp = requests.get(wp_url, params=img_params, headers=headers, timeout=5)
        img_data = img_resp.json()
        
        pages = img_data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "original" in page:
                return page["original"]["source"]
            if "thumbnail" in page:
                return page["thumbnail"]["source"]
            
    except Exception as e:
        # Fehler werden hier geloggt, um Debugging zu erleichtern
        print(f"DEBUG(Wiki-API-Fehler für {artist_name}): {e}", file=sys.stderr)
        pass
    return None

# --- PHASE 1: URLs schnell erfassen und Artist-Info (flach & mit Filtern) ---

video_tasks = []
ydl_opts_flat = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'no_warnings': True}

print("Phase 1: Erfasse alle Video-URLs und Künstlerinformationen schnell (mit Filtern angewendet)...", file=sys.stderr)

with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl_flat:
    # Wichtig: yt-dlp wendet 'match_filter' Optionen auch im 'flat' Modus an!
    ydl_flat.params.update(ydl_opts_details) 
    for channel_url in channels:
        try:
            info = ydl_flat.extract_info(channel_url, download=False)
            if info is None:
                 print(f"WARNUNG: Konnte keine Info für {channel_url} abrufen. Überspringe.", file=sys.stderr)
                 continue

            uploader_name = info.get("uploader") or info.get("channel") or "Unbekannter Künstler"
            
            # --- ERGÄNZUNG A: Channel ID extrahieren ---
            channel_id = info.get("channel_id")
            if not channel_id and 'entries' in info and len(info['entries']) > 0:
                 # Manchmal liegt die channel_id im ersten Eintrag, falls der Playlist-Header sie nicht hat.
                 channel_id = info['entries'][0].get('channel_id')

            if 'entries' in info:
                for entry in info['entries']:
                    if entry and 'url' in entry:
                        video_tasks.append({
                            'url': entry['url'],
                            'artist_name': uploader_name,
                            'channel_id': channel_id # Füge die ID dem Task hinzu
                        })
        except Exception as e:
            print(f"FEHLER in Phase 1 bei {channel_url}: {e}", file=sys.stderr)


unique_tasks = {task['url']: task for task in video_tasks}.values()
video_tasks_list = list(unique_tasks)
total_videos = len(video_tasks_list)

print(f"Insgesamt {total_videos} Videos gefunden (nach Filterung). Starte Phase 2 (detaillierte Abfrage & Wikipedia mittels Threads).", file=sys.stderr)


# --- PHASE 2: Detaillierte Metadaten & Wikipedia parallel abfragen ---

def process_video_task(task):
    """Funktion zum Abrufen von Details und Bild in einem Thread."""
    video_url = task['url']
    artist_name = task['artist_name']
    channel_id = task['channel_id'] # Füge die ID hier hinzu
    
    # Stellen Sie sicher, dass es eine vollständige URL ist
    full_url = f"https://www.youtube.com/watch?v={video_url}" if len(video_url) == 11 else video_url

    try:
        with yt_dlp.YoutubeDL(ydl_opts_details) as ydl_detail:
            video_info = ydl_detail.extract_info(full_url, download=False)
            
            if video_info:
                # Hole Wikipedia Bild HIER INNEN, im selben Thread
                image_url = get_artist_image(artist_name)
                
                return {
                    'youtube_id': video_info.get("id"),
                    'title': video_info.get('title'),
                    'duration': video_info.get('duration'),
                    'thumbnail': video_info.get('thumbnail'),
                    'artist_name': artist_name,
                    'image_url': image_url,
                    'channel_id': channel_id # Füge die ID dem finalen Daten-Dictionary hinzu
                }
    except Exception:
        pass
    return None

all_video_data = []

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    future_to_task = {executor.submit(process_video_task, task): task for task in video_tasks_list}
    
    for future in tqdm(as_completed(future_to_task), total=total_videos, desc="Verarbeite Videos & Wikipedia parallel", file=sys.stderr):
        result = future.result()
        if result:
            all_video_data.append(result)

# --- PHASE 3: SQL-Statements generieren und in Datei schreiben ---

artists_to_insert = {}

for video in all_video_data:
    artist_norm = normalize_name(video['artist_name'])
    if artist_norm not in artists_to_insert:
        artists_to_insert[artist_norm] = {
            'name': video['artist_name'],
            'image_url': video['image_url'],
            'channel_id': video['channel_id'] # Füge die ID hier hinzu
        }

print(f"\n-- Generiere SQL-Statements und speichere in '{OUTPUT_SQL_FILE}' --", file=sys.stderr)

# Hier öffnen wir die Datei und schreiben direkt hinein, damit 'python script.py' funktioniert
with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as f:
    f.write("START TRANSACTION;\n")

    # 1. Artists einfügen
    for artist_norm, data in artists_to_insert.items():
        image_sql = f"'{data['image_url'].replace("'", "''")}'" if data['image_url'] else "NULL"
        
        # --- ERGÄNZUNG B: SQL-Statement für artists um channel_id erweitern ---
        channel_id_sql = f"'{data['channel_id'].replace("'", "''")}'" if data['channel_id'] else "NULL"

        f.write(f"INSERT IGNORE INTO artists (name, name_norm, image_url, channel_id) "
                f"VALUES ('{data['name'].replace("'", "''")}', '{artist_norm}', {image_sql}, {channel_id_sql});\n")

    # 2. Videos einfügen (der Rest Ihres Codes kann wie folgt abgeschlossen werden)
    for video in all_video_data:
        youtube_id = video['youtube_id']
        title = video['title']
        title_norm = normalize_name(title)
        duration = video['duration']
        thumbnail = video['thumbnail']
        artist_norm = normalize_name(video['artist_name'])

        thumbnail_sql = f"'{thumbnail.replace("'", "''")}'" if thumbnail else "NULL"
        duration_sql = duration if duration is not None else "NULL"
        
        f.write(f"INSERT IGNORE INTO youtube_video_cache "
                f"(youtube_id, title, title_norm, artist_id, duration, thumbnail) "
                f"VALUES ("
                f"'{youtube_id}', "
                f"'{title.replace("'", "''")}', "
                f"'{title_norm}', "
                f"(SELECT id FROM artists WHERE name_norm = '{artist_norm}'), " # Subquery um artist_id zu finden
                f"{duration_sql}, "
                f"{thumbnail_sql}"
                f");\n")
                
    f.write("COMMIT;\n")