from yt_dlp import YoutubeDL

class SilentLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

urls = [
   "https://www.youtube.com/channel/UC8gxc2fYnL1tHPOXHXyI6sQ"
]

ydl_opts = {
    "quiet": True,
    "extract_flat": True,
    "logger": SilentLogger(),
}

for url in urls:
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        channel_id = info.get("channel_id") or info.get("id")
        if not channel_id:
            continue

        modified_id = channel_id[0] + "U" + channel_id[2:]
        playlist_url = f"https://www.youtube.com/playlist?list={modified_id}"

        print(playlist_url)
