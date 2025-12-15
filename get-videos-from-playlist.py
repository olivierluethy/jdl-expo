import yt_dlp
import time
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- KONFIGURATION ---
output_file = "taylor_swift_videos_sorted_threaded.json"
channels = ["https://www.youtube.com/playlist?list=UU0WP5P-ufpRfjbNrmOWwLBQ"]
MAX_THREADS = 30  # Anzahl der gleichzeitigen Anfragen. 

# Optionen für detaillierte Abfrage mit Filtern
ydl_opts_details = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'forceprintjson': True,
    'ignoreerrors': True,
    # Filter: Ignoriere Premium-Videos ODER Videos kürzer als 60 Sekunden (Shorts)
    'match_filter': yt_dlp.match_filter_func('!is_premium & duration > 60'), 
}
# ----------------------

# --- PHASE 1: URLs schnell erfassen, um die Gesamtanzahl zu kennen (flach) ---
print("Phase 1: Erfasse alle Video-URLs schnell (mit Filtern angewendet)...")
all_urls = set()
ydl_opts_flat = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'no_warnings': True}

with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl_flat:
    ydl_flat.params.update(ydl_opts_details) 
    for channel_url in channels:
        info = ydl_flat.extract_info(channel_url, download=False)
        if 'entries' in info:
            for entry in info['entries']:
                if entry and 'url' in entry:
                    all_urls.add(entry['url'])

video_urls_list = list(all_urls)
total_videos = len(video_urls_list)
print(f"Insgesamt {total_videos} Videos gefunden (nach Filterung). Starte Phase 2 (detaillierte Abfrage mittels Threads).")

# --- PHASE 2: Detaillierte Metadaten parallel abfragen mit Fortschrittsanzeige ---

def get_video_details(video_url):
    """Funktion zum Abrufen von Details für eine einzelne URL in einem Thread."""
    try:
        with yt_dlp.YoutubeDL(ydl_opts_details) as ydl_detail:
            info = ydl_detail.extract_info(video_url, download=False)
            if info:
                # HIER WERDEN DIE VIEWS ENTFERNT
                return {
                    'title': info.get('title', 'N/A'),
                    'url': info.get('webpage_url', 'N/A'),
                    'duration_seconds': info.get('duration', 0),
                    # 'views': info.get('view_count', 0), # Diese Zeile wurde entfernt
                }
    except Exception:
        pass
    return None

all_video_data = []

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    future_to_url = {executor.submit(get_video_details, url): url for url in video_urls_list}
    
    for future in tqdm(as_completed(future_to_url), total=total_videos, desc="Verarbeite Videos parallel"):
        result = future.result()
        if result:
            all_video_data.append(result)

# --- PHASE 3: Sortieren und Speichern ---
# HIER WIRD DIE SORTIERUNG ANGEPASST (jetzt nach 'title' alphabetisch)
sorted_videos = sorted(
    all_video_data,
    key=lambda x: x['title'].lower(), # Sortiert alphabetisch nach Titel
    reverse=False # Aufsteigend sortieren
)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sorted_videos, f, ensure_ascii=False, indent=4)

print(f"\nFertig! {len(sorted_videos)} Videos wurden in '{output_file}' gespeichert (ohne Views, alphabetisch sortiert).")
