from yt_dlp import YoutubeDL

url = "https://www.youtube.com/@KSI"  # oder https://www.youtube.com/c/ChannelName

ydl_opts = {}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    channel_id = info.get("channel_id")
    print("Channel-ID:", channel_id)
