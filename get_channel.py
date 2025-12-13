import yt_dlp
import os

CHANNELS_FILE = "unique_channels.txt"

youtube_urls = [
    "https://www.youtube.com/@TateMcRae/",
    "https://www.youtube.com/@GracieAbrams/",
    "https://www.youtube.com/@alessirose/"
]

def get_old_channel_url(url: str) -> str | None:
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["default"],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            channel_id = info.get("channel_id")
            if channel_id:
                return f"https://www.youtube.com/channel/{channel_id}"

            uploader_url = info.get("uploader_url")
            if uploader_url and uploader_url.startswith("https://www.youtube.com/"):
                return uploader_url

            channel_url = info.get("channel_url")
            if channel_url:
                return channel_url

            return None

    except Exception as e:
        print(f"Fehler beim Extrahieren von {url}: {e}")
        return None


# Lade bestehende Channels (ohne Anführungszeichen)
existing_channels = set()
file_is_empty = False

if os.path.exists(CHANNELS_FILE):
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:  # Datei existiert, ist aber leer
            file_is_empty = True
        else:
            for line in content.splitlines():
                cleaned = line.strip().rstrip(",").strip('"')
                if cleaned:
                    existing_channels.add(cleaned)
else:
    # Datei existiert noch nicht → wird als leer behandelt
    file_is_empty = True

# Verarbeite jede URL
for url in youtube_urls:
    channel_url = get_old_channel_url(url)

    if channel_url:
        clean_url = channel_url.strip()

        if clean_url in existing_channels:
            print(f"Bereits vorhanden: {clean_url}")
        else:
            # Neu hinzufügen
            with open(CHANNELS_FILE, "a", encoding="utf-8") as f:
                if file_is_empty:
                    # Erste Eintrag ever → führenden Zeilenumbruch einfügen
                    f.write("\n")
                    file_is_empty = False  # Nur beim allerersten Mal
                f.write(f"{clean_url},\n")

            existing_channels.add(clean_url)
            print(f"Hinzugefügt: {clean_url}")
    else:
        print(f"Kein Channel gefunden für: {url}")

print("\nFertig! Neue Channels wurden ohne Anführungszeichen zu 'unique_channels.txt' hinzugefügt.")