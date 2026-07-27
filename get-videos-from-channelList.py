import yt_dlp
import requests
import re
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from unidecode import unidecode

# --- KONFIGURATION ---
OUTPUT_SQL_FILE = "insert.sql"
CHANNELS_FILE = "unique_channels.txt"
MAX_THREADS = 10  # sicher für YouTube + Wikipedia

# FINALER, SHORTS-SICHERER FILTER
ydl_opts_details = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'ignoreerrors': False,                      # WICHTIG: jetzt sichtbare Fehler!
    'match_filter': yt_dlp.match_filter_func(
        '!is_premium & duration > 60 & !is_short'   # ← der entscheidende Zusatz
    ),
}
# ----------------------

# --- HILFSFUNKTIONEN ---
class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def convert_channel_to_uploads_playlist(url):
    if "playlist?list=" in url:
        return url

    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
        "no_warnings": True,
        "logger": SilentLogger(),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return url
            channel_id = info.get("channel_id") or info.get("id")
            if channel_id and channel_id.startswith("UC"):
                return f"https://www.youtube.com/playlist?list=UU{channel_id[2:]}"
        except Exception as e:
            print(f"Konvertierungsfehler {url}: {e}", file=sys.stderr)
    return url

def normalize_name(name):
    if not name:
        return ""
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9\s]', '', unidecode(name).lower())).strip()

# --- Wikipedia-Cache ---
artist_image_cache = {}

def get_artist_image(artist_name):
    if not artist_name or artist_name in artist_image_cache:
        return artist_image_cache.get(artist_name, None)

    wp_url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "ArtistImageFetcher/1.0 (your-email@example.com)"}

    try:
        search = requests.get(wp_url, params={
            "action": "query", "list": "search", "srsearch": artist_name,
            "format": "json", "srlimit": 1, "origin": "*"
        }, headers=headers, timeout=8).json()
        if not search.get("query", {}).get("search"):
            artist_image_cache[artist_name] = None
            return None
        title = search["query"]["search"][0]["title"]

        img = requests.get(wp_url, params={
            "action": "query", "titles": title, "format": "json",
            "prop": "pageimages", "piprop": "original", "origin": "*"
        }, headers=headers, timeout=8).json()
        page = next(iter(img["query"]["pages"].values()))
        result = page.get("original", {}).get("source") or page.get("thumbnail", {}).get("source")
        artist_image_cache[artist_name] = result
        return result
    except Exception as e:
        print(f"Wiki-Fehler ({artist_name}): {e}", file=sys.stderr)
        artist_image_cache[artist_name] = None
        return None

# --- Channels laden ---
with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
    raw = [l.strip() for l in f if l.strip().startswith("https://www.youtube.com/")]

unique_channels = []
seen = set()
for url in raw:
    norm = re.sub(r'\W+', '', url.lower())
    if norm not in seen:
        seen.add(norm)
        unique_channels.append(url)

# --- Hauptloop ---
all_video_data = []
total_processed = 0

pbar = tqdm(unique_channels, desc="Channels", file=sys.stderr)

for idx, orig_url in enumerate(pbar, 1):
    playlist_url = convert_channel_to_uploads_playlist(orig_url)
    if playlist_url != orig_url:
        print(f"→ {playlist_url}", file=sys.stderr)

    # PHASE 1: nur sammeln, KEIN Filter
    tasks = []
    ydl_flat = yt_dlp.YoutubeDL({
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'no_warnings': True,
    })

    try:
        info = ydl_flat.extract_info(playlist_url, download=False)
        if not info or not info.get("entries"):
            print(f"Keine Videos bei {playlist_url}", file=sys.stderr)
            continue

        uploader_name = info.get("uploader") or info.get("channel") or "Unbekannt"
        channel_id = info.get("channel_id") or (info["entries"][0].get("channel_id") if info["entries"] else None)

        expected = info.get("playlist_count")
        actual = len(info["entries"])
        if expected and actual < expected:
            print(f"WARNUNG: Unvollständig! {actual}/{expected} Videos ({uploader_name})", file=sys.stderr)

        for e in info["entries"]:
            if not e:
                continue
            vid = e.get("id") or (e.get("url").split("v=")[-1] if e.get("url") and "v=" in e.get("url") else None)
            if vid:
                tasks.append({"id": vid, "channel_name": uploader_name, "channel_id": channel_id})
    except Exception as e:
        print(f"Phase 1 Fehler {playlist_url}: {e}", file=sys.stderr)
        continue

    found = len(tasks)
    pbar.set_postfix({
        "Künstler": uploader_name[:25],
        "Gefunden": found,
        "Verarbeitet": total_processed,
        "Kanal": f"{idx}/{len(unique_channels)}"
    })

    if not tasks:
        continue

    # PHASE 2: mit echtem Filter + doppelter Shorts-Sicherung
    def process(task):
        vid = task["id"]
        url = f"https://www.youtube.com/watch?v={vid}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts_details) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return None

                # DOPPELTE SHORTS-SICHERUNG (falls is_short mal fehlt)
                if info.get("is_short") or "/shorts/" in (info.get("webpage_url") or ""):
                    return None

                # Besserer Artist-Name (nicht nur vom Channel!)
                artist = info.get("uploader") or info.get("channel") or task["channel_name"]

                return {
                    'youtube_id': info["id"],
                    'title': info["title"],
                    'duration': info.get("duration"),
                    'thumbnail': info.get("thumbnail"),
                    'artist_name': artist,
                    'image_url': get_artist_image(artist),
                    'channel_id': task["channel_id"]
                }
        except Exception as e:
            print(f"Video-Fehler {vid}: {e}", file=sys.stderr)
            return None

    results = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as exec:
        for future in tqdm(as_completed([exec.submit(process, t) for t in tasks]),
                           total=len(tasks), desc=uploader_name[:30], leave=False, file=sys.stderr):
            r = future.result()
            if r:
                results.append(r)

    successful = len(results)
    total_processed += successful
    all_video_data.extend(results)

    if successful < found:
        print(f"{successful}/{found} Videos erfolgreich ({uploader_name})", file=sys.stderr)

# --- SQL schreiben ---
artists = {}
for v in all_video_data:
    norm = normalize_name(v['artist_name'])
    if norm not in artists:
        artists[norm] = {
            'name': v['artist_name'],
            'image_url': v['image_url'],
            'channel_id': v['channel_id']
        }

print(f"\nFertig: {total_processed} Videos → {OUTPUT_SQL_FILE}", file=sys.stderr)

with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as f:
    f.write("START TRANSACTION;\n")
    for norm, a in artists.items():
        img = f"'{a['image_url'].replace("'", "''")}'" if a['image_url'] else "NULL"
        ch = f"'{a['channel_id'].replace("'", "''")}'" if a['channel_id'] else "NULL"
        f.write(f"INSERT IGNORE INTO artists (name, name_norm, image_url, channel_id) VALUES ('{a['name'].replace("'", "''")}', '{norm}', {img}, {ch});\n")

    for v in all_video_data:
        tnorm = normalize_name(v['title'])
        anorm = normalize_name(v['artist_name'])
        thumb = f"'{v['thumbnail'].replace("'", "''")}'" if v['thumbnail'] else "NULL"
        dur = v['duration'] if v['duration'] else "NULL"
        f.write(f"INSERT IGNORE INTO youtube_video_cache (youtube_id, title, title_norm, artist_id, duration, thumbnail) "
                f"VALUES ('{v['youtube_id']}', '{v['title'].replace("'", "''")}', '{tnorm}', "
                f"(SELECT id FROM artists WHERE name_norm = '{anorm}'), {dur}, {thumb});\n")
    f.write("COMMIT;\n")

print("SQL-Datei erfolgreich erstellt.", file=sys.stderr)