import re
import yt_dlp
import time
import random
import sys
import os

raw_input = """  
(1, 'e-ORhEE9VVg', 'Taylor Swift - Blank Space', 'taylor swift blank space', 273, 'https://i.ytimg.com/vi/e-ORhEE9VVg/mqdefault.jpg', '2025-11-09 21:34:03'),
(2, 'nfWlot6h_JM', 'Taylor Swift - Shake It Off', 'taylor swift shake it off', 242, 'https://i.ytimg.com/vi/nfWlot6h_JM/mqdefault.jpg', '2025-11-09 21:34:03'),
(3, 'VuNIsY6JdUw', 'Taylor Swift - You Belong With Me', 'taylor swift you belong with me', 229, 'https://i.ytimg.com/vi/VuNIsY6JdUw/mqdefault.jpg', '2025-11-09 21:34:03'),
"""

# Regex, um echte Video-Tupel zu erkennen
tuple_pattern = re.compile(
    r"\(\s*(\d+)\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*(\d+)\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*\)"
)

videos = tuple_pattern.findall(raw_input)
total_videos = len(videos)
print(f"Gefundene Videos: {total_videos}\n")

output_file = "unique_channels.txt"

# Bereits existierende Kanäle laden, falls die Datei existiert
existing_channels = set()
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                existing_channels.add(parts[1])  # Kanal-URL als eindeutiges Kriterium

# yt-dlp Optionen
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'sleep_interval': 3,
    'max_sleep_interval': 8,
    'sleep_interval_subtitles': 1,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl, open(output_file, 'a', encoding='utf-8') as out_file:
    for idx, vid in enumerate(videos, 1):
        video_id = vid[1]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        try:
            info = ydl.extract_info(video_url, download=False)
            channel_name = info.get('channel') or info.get('uploader')
            channel_url = info.get('channel_url')

            if channel_url not in existing_channels:
                # In Datei schreiben und Set aktualisieren
                out_file.write(f"{channel_name}\t{channel_url}\n")
                existing_channels.add(channel_url)
                print(f"Neu hinzugefügt: {channel_name} | {channel_url}")
            else:
                print(f"Bereits vorhanden, übersprungen: {channel_name} | {channel_url}")

        except Exception as e:
            print(f"Fehler bei Video {video_id}: {e}\n")

        # Fortschritt berechnen
        progress = (idx / total_videos) * 100
        bar_length = 30
        filled_length = int(bar_length * idx // total_videos)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\rProgress: |{bar}| {progress:.1f}% ({idx}/{total_videos})\n")
        sys.stdout.flush()

        # Kleine zufällige Pause zur Sicherheit
        time.sleep(random.uniform(1, 4))

print("\n\nFertig! Alle einzigartigen Kanäle gespeichert in", output_file)
