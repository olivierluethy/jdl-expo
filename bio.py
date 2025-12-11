from yt_dlp import YoutubeDL
import sys
import re

urls = [
    "https://www.youtube.com/channel/UCqECaJ8Gagnn7YCbPEzWH6g",
    "https://www.youtube.com/@MrBeast",
    "https://www.youtube.com/@KSI"
]

class ChannelIDLogger:
    def __init__(self):
        self.channel_id_printed = False

    def debug(self, msg):
        # Suche nach den page X: Downloading API JSON Meldungen
        if "[youtube:tab]" in msg and "page" in msg and "Downloading API JSON" in msg:

            # Channel-ID aus page 1 extrahieren
            if not self.channel_id_printed:
                match = re.search(r'\[youtube:tab\] ([\w-]+) page 1', msg)
                if match:
                    channel_id = match.group(1)

                    # Zweites Zeichen ersetzen (z. B. "C" → "U")
                    modified_id = channel_id[0] + "U" + channel_id[2:]

                    # Playlist-URL erzeugen
                    playlist_url = f"https://www.youtube.com/playlist?list={modified_id}"
                    print(playlist_url)

                    self.channel_id_printed = True

            # Wenn page > 1 → Abbrechen
            try:
                page_number = int(re.search(r'page (\d+):', msg).group(1))
                if page_number > 1:
                    raise SystemExit  # sauberer Abbruch pro URL
            except:
                pass

    def warning(self, msg):
        pass

    def error(self, msg):
        raise SystemExit


ydl_opts = {
    "quiet": True,
    "extract_flat": True,
}

# -----------------------------
# Verarbeitung mehrerer URLs
# -----------------------------
for url in urls:
    logger = ChannelIDLogger()
    ydl_opts["logger"] = logger

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=False)
    except SystemExit:
        continue
