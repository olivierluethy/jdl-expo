#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from yt_dlp import YoutubeDL
from pathlib import Path
import time
import random
import sys
import re
import requests

# === Dateien ===
INPUT_FILE = "unique_channels.txt"
PROCESSED_FILE = "processed_channels.txt"
SQL_OUTPUT = "innerts.sql"


# === SQL Escaping ===
def sql_escape(value):
    if value is None:
        return ""
    return str(value).replace("'", "''")


# === Normalisierung (IDENTISCH zum JS) ===
def normalize_title(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(
        r"\b(official|video|audio|lyric|visualizer|live|remix|explicit|clean|acoustic|sped up|instrumental)\b",
        "",
        text,
        flags=re.I
    )
    text = re.sub(r"\b(ft\.?|feat\.?|featuring)\b", "", text, flags=re.I)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# === Wikipedia Bild ===
def fetch_artist_image(artist_name):
    url = (
        "https://en.wikipedia.org/w/api.php"
        "?action=query&format=json&prop=pageimages"
        "&piprop=original&origin=*&titles="
        + requests.utils.quote(artist_name)
    )
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "original" in page:
                return page["original"]["source"]
    except Exception:
        pass
    return ""


class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


ydl_opts = {
    "quiet": True,
    "extract_flat": False,
    "logger": SilentLogger(),
    "retries": 5,
}


# === Bereits verarbeitete Channels ===
processed = set()
if Path(PROCESSED_FILE).exists():
    processed = set(Path(PROCESSED_FILE).read_text(encoding="utf-8").splitlines())

if not Path(INPUT_FILE).exists():
    print(f"Fehler: {INPUT_FILE} nicht gefunden")
    sys.exit(1)

channels = [
    line.strip()
    for line in Path(INPUT_FILE).read_text(encoding="utf-8").splitlines()
    if line.strip().startswith("http") and line.strip() not in processed
]

if not channels:
    print("Nichts zu tun.")
    sys.exit(0)


# === Verarbeitung ===
with YoutubeDL(ydl_opts) as ydl, \
     open(SQL_OUTPUT, "a", encoding="utf-8") as sql, \
     open(PROCESSED_FILE, "a", encoding="utf-8") as done:

    total = len(channels)

    for idx, channel_url in enumerate(channels, 1):
        try:
            info = ydl.extract_info(channel_url, download=False)
            channel_id = info.get("channel_id") or info.get("id")

            if not channel_id or not channel_id.startswith("UC"):
                raise ValueError("Keine gültige Channel-ID")

            # === Uploads Playlist ===
            playlist_id = "UU" + channel_id[2:]
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

            playlist = ydl.extract_info(playlist_url, download=False)

            artist = playlist.get("uploader") or playlist.get("channel")
            if not artist:
                raise ValueError("Kein Artist-Name gefunden")

            artist_norm = normalize_title(artist)
            image_url = fetch_artist_image(artist)

            # === Artist SQL ===
            sql.write(
                "INSERT INTO artists (name, name_norm, image_url)\n"
                f"VALUES ('{sql_escape(artist)}', "
                f"'{sql_escape(artist_norm)}', "
                f"'{sql_escape(image_url)}')\n"
                "ON DUPLICATE KEY UPDATE image_url = VALUES(image_url), "
                "id = LAST_INSERT_ID(id);\n\n"
            )
            sql.write("SELECT LAST_INSERT_ID() AS artist_id;\n\n")

            # === Videos ===
            sql.write(
                "INSERT IGNORE INTO youtube_video_cache "
                "(title_norm, title, youtube_id, artist_id, duration, thumbnail)\nVALUES\n"
            )

            values = []
            for v in playlist.get("entries", []):
                if not v:
                    continue

                vid = v.get("id")
                title = v.get("title")
                duration = v.get("duration") or 0

                if not vid or not title:
                    continue

                values.append(
                    f"('{sql_escape(normalize_title(title))}', "
                    f"'{sql_escape(title)}', "
                    f"'{vid}', "
                    f"LAST_INSERT_ID(), "
                    f"{int(duration)}, "
                    f"'https://i.ytimg.com/vi/{vid}/mqdefault.jpg')"
                )

            if values:
                sql.write(",\n".join(values) + ";\n\n")

            print(f"[+] {artist} ({len(values)} Videos)")

        except Exception as e:
            print(f"[!] Fehler bei {channel_url}: {e}")

        # === Channel als verarbeitet markieren ===
        done.write(channel_url + "\n")
        done.flush()

        # Fortschritt
        progress = (idx / total) * 100
        bar_len = 40
        filled = int(bar_len * idx // total)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"\r{bar} {progress:6.2f}% ({idx}/{total})", end="", flush=True)

        time.sleep(random.uniform(0.5, 2.0))

print("\n\n✔ Fertig: SQL wurde generiert → innerts.sql")
