from yt_dlp import YoutubeDL

# Hier kannst du beliebig eine @-Handle-URL oder normale Channel-URL eingeben
INPUT = "https://www.youtube.com/@CBSMornings"

ydl_opts = {
    "quiet": True,
    "no_download": True,
    "extract_flat": True,
    "playlist_items": "1",
    "skip_playlist_after_errors": 1,
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(INPUT, download=False)

channel_id = info.get("channel_id")

if channel_id and channel_id.startswith("UC"):
    # Normale Channel-URL
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    
    # Uploads-Playlist: Ersetze die ersten zwei Zeichen "UC" durch "UU"
    uploads_playlist_id = "UU" + channel_id[2:]
    uploads_playlist_url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

    print("Channel-URL:", channel_url)
    print("Channel-ID:", channel_id)
    print()
    print("Uploads-Playlist-URL:", uploads_playlist_url)
    print("Uploads-Playlist-ID:", uploads_playlist_id)
else:
    print("Fehler: Channel-ID konnte nicht extrahiert werden.")
    print("Versuche eine andere URL-Variante, z. B. mit /videos am Ende.")