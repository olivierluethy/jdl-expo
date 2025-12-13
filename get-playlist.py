from yt_dlp import YoutubeDL
from pathlib import Path
import time
import random
import sys

# === Dateien ===
INPUT_FILE = "unique_channels.txt"
OUTPUT_FILE = "unique_playlists.txt"
PROCESSED_FILE = "processed_channels.txt"


class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


ydl_opts = {
    "quiet": True,
    "extract_flat": True,
    "logger": SilentLogger(),
    "retries": 5,
    "sleep_interval": 0.4,
    "max_sleep_interval": 1.6,
}


# === Bereits verarbeitete Channels laden ===
processed_channels = set()
if Path(PROCESSED_FILE).exists():
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        processed_channels = {line.strip() for line in f if line.strip()}

print(f"Überspringe {len(processed_channels)} bereits verarbeitete Kanäle.\n")


# === Alle Channel-URLs laden ===
if not Path(INPUT_FILE).exists():
    print(f"Fehler: {INPUT_FILE} nicht gefunden!")
    sys.exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    all_channels = [
        line.strip()
        for line in f
        if line.strip().startswith("http")
    ]

channels_to_process = [
    ch for ch in all_channels if ch not in processed_channels
]

print(f"Gesamt Kanäle: {len(all_channels)}")
print(f"Noch zu verarbeiten: {len(channels_to_process)}\n")

if not channels_to_process:
    print("Alle Kanäle wurden bereits verarbeitet. Fertig.")
    sys.exit(0)


# === Bereits vorhandene Playlists laden ===
existing_playlists = set()
if Path(OUTPUT_FILE).exists():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        existing_playlists = {line.strip() for line in f if line.strip()}


# === Verarbeitung ===
with YoutubeDL(ydl_opts) as ydl, \
     open(OUTPUT_FILE, "a", encoding="utf-8") as playlist_file, \
     open(PROCESSED_FILE, "a", encoding="utf-8") as processed_file:

    total = len(channels_to_process)

    for idx, channel_url in enumerate(channels_to_process, 1):
        try:
            info = ydl.extract_info(channel_url, download=False)
            channel_id = info.get("channel_id") or info.get("id")

            if channel_id and channel_id.startswith("UC"):
                playlist_id = "UU" + channel_id[2:]
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

                if playlist_url not in existing_playlists:
                    playlist_file.write(playlist_url + "\n")
                    playlist_file.flush()
                    existing_playlists.add(playlist_url)
                    print(f"[+] Playlist: {playlist_url}")
                else:
                    print(f"[~] Duplikat: {playlist_url}")
            else:
                print(f"[!] Keine gültige Channel-ID: {channel_url}")

        except Exception as e:
            print(f"[!] Fehler bei {channel_url}: {e}")

        # === WICHTIG: Channel als verarbeitet markieren ===
        processed_file.write(channel_url + "\n")
        processed_file.flush()

        # Fortschrittsbalken
        progress = (idx / total) * 100
        bar_len = 40
        filled = int(bar_len * idx // total)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r{bar} {progress:6.2f}% ({idx}/{total})", end="", flush=True)

        # Human-like Pause
        time.sleep(random.uniform(0.5, 2.0))

print("\n\nFertig!")
print(f"Playlists gesamt: {len(existing_playlists)} → {OUTPUT_FILE}")
print(f"Verarbeitete Kanäle: {len(processed_channels) + total} → {PROCESSED_FILE}")
