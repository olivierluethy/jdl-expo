import yt_dlp
import time
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- KONFIGURATION ---
output_file = "taylor_swift_videos_sorted_threaded.json"
channels = "https://www.youtube.com/playlist?list=UU0WP5P-ufpRfjbNrmOWwLBQ",
MAX_THREADS = 30  # Anzahl der gleichzeitigen Anfragen. 
                  # Kann auf 20, 30 oder mehr erhöht werden, je nach Ihrer Internetbandbreite und PC-Leistung.

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
    # Wichtig: yt-dlp wendet 'match_filter' Optionen auch im 'flat' Modus an!
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
                return {
                    'title': info.get('title', 'N/A'),
                    'url': info.get('webpage_url', 'N/A'),
                    'duration_seconds': info.get('duration', 0),
                    'views': info.get('view_count', 0),
                }
    except Exception:
        # Fehler in Threads schlucken oder loggen
        pass
    return None

all_video_data = []

# ThreadPoolExecutor für parallele Ausführung
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Futures (Platzhalter für Ergebnisse) für jede URL starten
    future_to_url = {executor.submit(get_video_details, url): url for url in video_urls_list}
    
    # Fortschrittsanalken mit tqdm überwachen
    for future in tqdm(as_completed(future_to_url), total=total_videos, desc="Verarbeite Videos parallel"):
        result = future.result()
        if result:
            all_video_data.append(result)

# --- PHASE 3: Sortieren und Speichern ---
sorted_videos = sorted(
    all_video_data,
    key=lambda x: x['views'],
    reverse=True
)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sorted_videos, f, ensure_ascii=False, indent=4)

print(f"\nFertig! {len(sorted_videos)} Videos wurden nach Beliebtheit sortiert und in '{output_file}' gespeichert.")
