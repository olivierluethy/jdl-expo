import re
import yt_dlp
import time
import random
import sys
import os

# === Dateien ===
raw_file = "artists_output(1).txt"          # Hier kommt dein großer SQL-ähnlicher Input rein
processed_file = "processed_videos.txt"   # Wird automatisch erstellt + erweitert
output_file = "unique_channels.txt"

# === Bereits verarbeitete Video-IDs laden ===
processed_ids = set()
if os.path.exists(processed_file):
    with open(processed_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                processed_ids.add(line)
    print(f"Überspringe {len(processed_ids)} bereits verarbeitete Videos.\n")

# === Raw-Input aus Datei laden (nicht mehr als String im Code!) ===
if not os.path.exists(raw_file):
    print(f"Fehler: {raw_file} nicht gefunden!")
    sys.exit(1)

with open(raw_file, 'r', encoding='utf-8') as f:
    raw_input = f.read()

# === Regex für Tupel ===
tuple_pattern = re.compile(
    r"\(\s*\d+\s*,\s*'([^']+)'\s*,"  # nur die Video-ID interessiert uns (2. Feld)
)

# Alle Video-IDs extrahieren
all_video_ids = tuple_pattern.findall(raw_input)
print(f"Gesamt gefunden: {len(all_video_ids)} Videos in {raw_file}")

# Nur die noch nicht verarbeiteten
videos_to_process = [vid for vid in all_video_ids if vid not in processed_ids]
print(f"Noch zu verarbeiten: {len(videos_to_process)}\n")

if not videos_to_process:
    print("Alle Videos bereits verarbeitet! Fertig.")
    sys.exit(0)

# === Bereits gefundene Kanäle laden ===
existing_channels = set()
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                existing_channels.add(line)

# === yt-dlp Optimierung ===
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,           # brauchen wir für channel_url
    'cachedir': False,
    'retries': 5,
    'sleep_interval': 0.4,
    'max_sleep_interval': 1.6,
}

# Dateien zum Anhängen öffnen
with yt_dlp.YoutubeDL(ydl_opts) as ydl, \
     open(output_file, 'a', encoding='utf-8') as channel_file, \
     open(processed_file, 'a', encoding='utf-8') as done_file:

    for idx, video_id in enumerate(videos_to_process, 1):
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            info = ydl.extract_info(video_url, download=False)
            channel_url = info.get('channel_url')

            if channel_url and channel_url not in existing_channels:
                channel_file.write(channel_url + '\n')
                existing_channels.add(channel_url)
                print(f"[+] Neu: {info.get('channel')} | {channel_url}")
            else:
                print(f"[~] Duplikat: {channel_url or 'kein Kanal'}")

            # === WICHTIG: Als erledigt markieren ===
            done_file.write(video_id + '\n')
            done_file.flush()  # Sofort auf Festplatte schreiben (auch bei Absturz sicher)

        except Exception as e:
            error_msg = str(e).lower()
            if "private" in error_msg or "unavailable" in error_msg or "deleted" in error_msg:
                print(f"[!] Gelöscht/Privat: {video_id}")
            else:
                print(f"[!] Fehler bei {video_id}: {e}")
            # Auch bei Fehler als "erledigt" markieren → nicht nochmal versuchen
            done_file.write(video_id + '\n')
            done_file.flush()

        # Fortschrittsanzeige
        progress = (idx / len(videos_to_process)) * 100
        bar_length = 40
        filled = int(bar_length * idx // len(videos_to_process))
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r{bar} {progress:6.2f}% ({idx}/{len(videos_to_process)})", end='', flush=True)

        # Human-like Pause
        time.sleep(random.uniform(0.5, 2.1))

# === Optional: raw_videos.txt bereinigen (nur verbleibende übrig lassen) ===
print("\n\nBereinige raw_videos.txt ...")
remaining_lines = []
with open(raw_file, 'r', encoding='utf-8') as f:
    for line in f:
        if re.search(r"\(\s*\d+\s*,\s*'(" + "|".join(processed_ids) + r")'", line):
            continue  # bereits verarbeitet → weglassen
        remaining_lines.append(line)

with open(raw_file, 'w', encoding='utf-8') as f:
    f.writelines(remaining_lines)

print(f"\nFertig! {len(videos_to_process)} Videos verarbeitet.")
print(f"Unique Kanäle: {len(existing_channels)} → {output_file}")
print(f"Verbleibende in {raw_file}: {len(remaining_lines)} Zeilen")