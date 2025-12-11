from yt_dlp import YoutubeDL
import sys
import re

url = "https://www.youtube.com/@daftpunk"

class ChannelIDLogger:
    channel_id_printed = False

    def debug(self, msg):
        # Prüfen, ob es die "page X"-Meldung ist
        if "[youtube:tab]" in msg and "page" in msg and "Downloading API JSON" in msg:
            if not self.channel_id_printed:
                match = re.search(r'\[youtube:tab\] ([\w-]+) page 1', msg)

                if match:
                    channel_id = match.group(1)
                    # Zweites Zeichen ersetzen
                    modified_id = channel_id[0] + 'U' + channel_id[2:]
                    # URL zusammensetzen
                    playlist_url = f"https://www.youtube.com/playlist?list={modified_id}"
                    print(playlist_url)
                    self.channel_id_printed = True

            # Extrahiere Seitenzahl und breche ab, falls Seite > 1
            try:
                page_number = int(re.search(r'page (\d+):', msg).group(1))
                if page_number > 1:
                    sys.exit(0)
            except Exception:
                pass

    def warning(self, msg):
        pass  # keine Ausgabe
    def error(self, msg):
        sys.exit(1)

ydl_opts = {
    "logger": ChannelIDLogger(),
    "quiet": True,
    "extract_flat": True,
}

with YoutubeDL(ydl_opts) as ydl:
    ydl.extract_info(url, download=False)
