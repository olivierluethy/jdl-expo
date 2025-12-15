from yt_dlp import YoutubeDL

# Hier kannst du beliebig eine @-Handle-URL oder normale Channel-URL eingeben
INPUT = "https://www.youtube.com/@CBSMornings"

ydl_opts = {
    "quiet": True,               # Keine unnötigen Logs
    "no_download": True,         # Nichts herunterladen
    "extract_flat": True,        # Nur Metadaten, keine tiefen Video-Infos
    "playlist_items": "1",       # Nur den ersten Eintrag verarbeiten (genug für Channel-Info)
    "skip_playlist_after_errors": 1,  # Bei Fehler sofort abbrechen
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(INPUT, download=False)

# Die Channel-ID ist im Haupt-Dict unter 'channel_id' verfügbar
channel_id = info.get("channel_id")

if channel_id:
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    print(channel_url)
else:
    print("Fehler: Channel-ID konnte nicht extrahiert werden.")
    print("Versuche eine andere URL-Variante, z. B. mit /videos am Ende.")