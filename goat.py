import yt_dlp
import time

# Ziel-Datei
output_file = "taylor_swift_videos.txt"

# Offizielle Kanäle von Taylor Swift
channels = [
    "https://www.youtube.com/playlist?list=UUuRwdG_2dvII6VaJPppXqAw",
]

# yt-dlp Optionen – wir laden nichts herunter, nur Metadaten/URLs holen
ydl_opts = {
    'quiet': False,
    'extract_flat': True,           # Nur Metadaten, keine Downloads
    'skip_download': True,
    'no_warnings': False,
    'playlistend': None,            # Alle Videos holen (kein Limit)
    'retries': 10,
    'fragment_retries': 10,
}

all_urls = set()  # Duplikate vermeiden

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for channel_url in channels:
        print(f"\nDurchsuche Kanal: {channel_url}")
        try:
            # Kanal-Playlist "Videos" automatisch laden
            info = ydl.extract_info(channel_url, download=False)

            if 'entries' in info:
                for entry in info['entries']:
                    if entry and 'url' in entry:
                        video_url = f"{entry['url']}"
                        all_urls.add(video_url)
            else:
                print("Kein 'entries'-Feld gefunden – möglicherweise falsche URL oder Privatsphäre-Einstellungen.")

        except Exception as e:
            print(f"Fehler bei {channel_url}: {e}")

        # Höflichkeitspause zwischen den Kanälen
        time.sleep(2)

# In Datei speichern
with open(output_file, "w", encoding="utf-8") as f:
    for url in sorted(all_urls):
        f.write(url + "\n")

print(f"\nFertig! {len(all_urls)} eindeutige Video-URLs wurden in '{output_file}' gespeichert.")