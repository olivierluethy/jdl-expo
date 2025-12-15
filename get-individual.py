from yt_dlp import YoutubeDL
import re

class SilentLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

urls = [
    "https://www.youtube.com/channel/UCkajFamD9odK1vtdXMhEUcg"
]

ydl_opts = {
    "quiet": True,
    "extract_flat": True,
    "logger": SilentLogger(),
}

for url in urls:
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # 1️⃣ Normaler Weg über yt-dlp Infos
        channel_id = info.get("channel_id") or info.get("id")

        # 2️⃣ Edge-Case: yt-dlp kennt nur die Uploads-Playlist implizit
        if not channel_id:
            match = re.search(r"(UC[a-zA-Z0-9_-]{22})", url)
            if match:
                channel_id = match.group(1)

        if not channel_id:
            continue

        # 3️⃣ Uploads-Playlist erzeugen (UC → UU)
        uploads_playlist_id = "UU" + channel_id[2:]
        playlist_url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

        print(playlist_url)
