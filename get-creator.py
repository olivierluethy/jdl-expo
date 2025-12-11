import yt_dlp

url = "https://www.youtube.com/watch?v=WA4iX5D9Z64"

with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(url, download=False)
    channel_url = info.get('channel_url')
    print(channel_url)
