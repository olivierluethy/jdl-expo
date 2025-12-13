import yt_dlp

youtube_urls = [
    # "https://www.youtube.com/@ErosRamazzotti",
    "https://www.youtube.com/@DomenicoModugnoOfficial",
    "https://www.youtube.com/@claudiobaglionitv",
    "https://www.youtube.com/@laurapausinitv",
    "https://www.youtube.com/@TizianoFerro",
    "https://www.youtube.com/@VascoRossi",
    "https://www.youtube.com/@Jovanotti",
    "https://www.youtube.com/@ligabue",
    "https://www.youtube.com/@negramaro",
    "https://www.youtube.com/@fabrifibra",
    "https://www.youtube.com/@salmo",
    "https://www.youtube.com/@manuarenaofficial",
    "https://www.youtube.com/@francescomichelini",
    "https://www.youtube.com/@alessandromannarino",
    "https://www.youtube.com/@francescogabbani",
    "https://www.youtube.com/@ermalmeta",
    "https://www.youtube.com/@biagioantonacci",
    "https://www.youtube.com/@nektarofficial",
    "https://www.youtube.com/@subsonica",
    "https://www.youtube.com/@marcoMengoni",
    "https://www.youtube.com/@fabriFibraVEVO",
    "https://www.youtube.com/@thegiornalisti",
    "https://www.youtube.com/@marracash",
    "https://www.youtube.com/@caparezza",
    "https://www.youtube.com/@gemitaiz",
    "https://www.youtube.com/@salvinomusic",
    "https://www.youtube.com/@liricaofficial",
    "https://www.youtube.com/@comatriofficial",
    "https://www.youtube.com/@thekolors",
    "https://www.youtube.com/@maneskin",
    "https://www.youtube.com/@officialmadh",
    "https://www.youtube.com/@umbertotozziofficial",
    "https://www.youtube.com/@AndreaBocelli",
    "https://www.youtube.com/@Zuccheromusic",
    "https://www.youtube.com/@JuiceWRLD",
    "https://www.youtube.com/@LewisCapaldi",
    # weitere URLs hier eintragen
    # "https://www.youtube.com/@Metallica",
    # "https://www.youtube.com/@Coldplay",
]

def get_old_channel_url(url: str) -> str | None:
    """
    Gibt bevorzugt die alte Channel-URL zurück: https://www.youtube.com/channel/UC...
    """
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,  # Keine tiefgehende Video-Extraktion → keine Warnings
        "extractor_args": {
            "youtube": {
                "player_client": ["default"],  # Unterdrückt JS- und SABR-Warnings
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Priorität 1: channel_id → alte Form (das ist, was du willst)
            channel_id = info.get("channel_id")
            if channel_id:
                return f"https://www.youtube.com/channel/{channel_id}"

            # Fallback 1: uploader_url (meist die @-Handle-Form)
            uploader_url = info.get("uploader_url")
            if uploader_url and uploader_url.startswith("https://www.youtube.com/"):
                return uploader_url

            # Fallback 2: channel_url (falls vorhanden)
            channel_url = info.get("channel_url")
            if channel_url:
                return channel_url

            return None

    except Exception as e:
        print(f"Fehler beim Extrahieren von {url}: {e}")
        return None


for url in youtube_urls:
    channel_url = get_old_channel_url(url)

    if channel_url:
        print(f'"{channel_url}",')
    else:
        print(f'Kein Channel gefunden für: {url}')