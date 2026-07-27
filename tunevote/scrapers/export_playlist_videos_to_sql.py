"""
export_playlist_videos_to_sql.py — export one playlist to a ready-to-import SQL file.

Description:
    Runs in three phases. Phase one converts any channel URL form (/channel/,
    /c/, @handle, /user/) into the corresponding uploads playlist and collects
    every video URL from it with a flat, fast yt-dlp pass. Phase two fetches full
    metadata for each video across thirty threads and looks up the artist's
    Wikipedia image in the same worker. Phase three groups the results by
    normalized artist name and writes a single transactional SQL file containing
    INSERT IGNORE statements for the artists table followed by the videos.
    Artist names are passed through unidecode first, so accented names normalize
    to their ASCII form.

Requirements:
    - Python 3.x
    - Packages: yt-dlp, requests, tqdm, unidecode
    - External services: youtube.com, en.wikipedia.org (neither needs a key)
    - Environment variables / credentials needed: none

Inputs:
    The channels list inside this file. No command-line arguments are parsed.

Outputs:
    database/dumps/tunevote_artists_and_videos_insert.sql — overwritten on every
    run, wrapped in START TRANSACTION / COMMIT. Progress goes to stderr.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/export_playlist_videos_to_sql.py

Notes:
    The output file is opened with mode "w", so each run replaces the previous
    export — copy it elsewhere if you need to keep it. The match filter
    '!is_premium & duration > 60' drops Premium-only videos and treats anything
    under sixty seconds as a Short; export_channel_list_videos_to_sql.py adds a
    stricter second check for Shorts that slip through. Thirty threads is
    aggressive and can trigger YouTube throttling on a slow connection.
"""

import yt_dlp
import time
import requests
import re
import sys
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from unidecode import unidecode # <-- NEUER IMPORT

# --- CONFIGURATION ---
OUTPUT_SQL_FILE = "database/dumps/tunevote_artists_and_videos_insert.sql" # The file that is created automatically
channels = ["https://www.youtube.com/playlist?list=UULkAepWjdylmXSltofFvsYQ"]
MAX_THREADS = 30  # Tune to the performance of the machine.

# Options for the detailed query (WITH FILTERS FOR SHORTS/PREMIUM)
ydl_opts_details = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'ignoreerrors': True,
    # Filter: ignore Premium videos AND anything shorter than 60 seconds (Shorts)
    'match_filter': yt_dlp.match_filter_func('!is_premium & duration > 60'), 
}
# ----------------------

# --- HELPER: convert a channel URL into an uploads playlist URL ---
class SilentLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

def convert_channel_to_uploads_playlist(url):
    """Convert any form of YouTube channel URL into its uploads playlist (UU…)."""
    
    # 1. Quick check: already a playlist? Return it unchanged.
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

            # yt-dlp returns channel_id for every channel form, including /c/ and @
            channel_id = info.get("channel_id") or info.get("id")
            if channel_id and channel_id.startswith("UC"):
                uploads_id = "UU" + channel_id[2:]
                return f"https://www.youtube.com/playlist?list={uploads_id}"
        except:
            pass

    # Last-resort fallback: try /c/ or @ manually (should never be needed)
    # Kept for absolute safety:
    if "/c/" in url:
        handle = url.split("/c/")[-1].split("?")[0]
        # yt-dlp can do this too, but do it explicitly once more:
        try:
            test_url = f"https://www.youtube.com/@{handle}"
            return convert_channel_to_uploads_playlist(test_url)  # recurse exactly once
        except:
            pass

    return url
# -----------------------------------------------------------------------

# --- Convert every channel URL variant automatically ---
processed_channels = []
for original_url in channels:
    # Detect all known channel URL formats
    if any(x in original_url for x in ["/channel/UC", "/c/", "@", "/user/"]):
        playlist_url = convert_channel_to_uploads_playlist(original_url)
        print(f"Channel detected → converted to uploads playlist: {playlist_url}", file=sys.stderr)
        processed_channels.append(playlist_url)
    else:
        processed_channels.append(original_url)

channels = processed_channels
# -----------------------------------------------------------------------
# ---------------------------------------------------------------

# --- HELPER FUNCTIONS ---

def normalize_name(name):
    if not name:
        return ""
        
    # --- Transliterate to ASCII first, then normalize ---
    # Mylène Farmer -> Mylene Farmer
    # Rag'n'Bone Man -> Rag'n'Bone Man (accents gone, punctuation still present)
    normalized = unidecode(name) 

    normalized = normalized.lower()
    # Safer now that most special characters have been transliterated away
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized) 
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    # 'Mylène Farmer' now normalizes to 'mylene farmer'
    return normalized

def get_artist_image(artist_name):
    """Fetch the artist image from Wikipedia (blocking; runs inside a worker thread)."""
    # ... (this function is unchanged) ...
    if not artist_name:
        return None
    
    wp_url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "ArtistImageFetcher/1.0 (your-email@example.com)"}
    
    # 1. Find the best-matching Wikipedia page title for the artist
    search_params = {
        "action": "query", "list": "search", "srsearch": artist_name,
        "format": "json", "srlimit": 1, "origin": "*"
    }
    try:
        search_resp = requests.get(wp_url, params=search_params, headers=headers, timeout=5)
        search_data = search_resp.json()
        searches = search_data.get("query", {}).get("search", [])
        if not searches: return None
        # Take the title field of the first search result
        page_title = searches[0]["title"] 
        
        # 2. Fetch the image, preferring the original
        img_params = {
            "action": "query", "titles": page_title, "format": "json",
            "prop": "pageimages", "piprop": "original", "origin": "*"
        }
        img_resp = requests.get(wp_url, params=img_params, headers=headers, timeout=5)
        img_data = img_resp.json()
        
        pages = img_data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "original" in page:
                return page["original"]["source"]
            if "thumbnail" in page:
                return page["thumbnail"]["source"]
            
    except Exception as e:
        # Errors are logged here to make debugging easier
        print(f"DEBUG(Wikipedia API error for {artist_name}): {e}", file=sys.stderr)
        pass
    return None

# --- PHASE 1: quickly collect the URLs and artist info (flat, with filters) ---

video_tasks = []
ydl_opts_flat = {'quiet': True, 'extract_flat': True, 'skip_download': True, 'no_warnings': True}

print("Phase 1: quickly collecting all video URLs and artist information (filters applied)...", file=sys.stderr)

with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl_flat:
    # Important: yt-dlp applies 'match_filter' in flat mode as well.
    ydl_flat.params.update(ydl_opts_details) 
    for channel_url in channels:
        try:
            info = ydl_flat.extract_info(channel_url, download=False)
            if info is None:
                 print(f"WARNING: could not retrieve info for {channel_url}. Skipping.", file=sys.stderr)
                 continue

            uploader_name = info.get("uploader") or info.get("channel") or "Unknown artist"
            
            # --- Extract the channel ID ---
            channel_id = info.get("channel_id")
            if not channel_id and 'entries' in info and len(info['entries']) > 0:
                 # Sometimes channel_id is only on the first entry, not the playlist header.
                 channel_id = info['entries'][0].get('channel_id')

            if 'entries' in info:
                for entry in info['entries']:
                    if entry and 'url' in entry:
                        video_tasks.append({
                            'url': entry['url'],
                            'artist_name': uploader_name,
                            'channel_id': channel_id # carry the ID through with the task
                        })
        except Exception as e:
            print(f"ERROR in phase 1 on {channel_url}: {e}", file=sys.stderr)


unique_tasks = {task['url']: task for task in video_tasks}.values()
video_tasks_list = list(unique_tasks)
total_videos = len(video_tasks_list)

print(f"Found {total_videos} videos in total (after filtering). Starting phase 2 (detailed query and Wikipedia lookups across threads).", file=sys.stderr)


# --- PHASE 2: fetch detailed metadata and Wikipedia images in parallel ---

def process_video_task(task):
    """Fetch video details and the artist image inside one worker thread."""
    video_url = task['url']
    artist_name = task['artist_name']
    channel_id = task['channel_id'] # carried through from phase 1
    
    # Make sure this is a complete URL
    full_url = f"https://www.youtube.com/watch?v={video_url}" if len(video_url) == 11 else video_url

    try:
        with yt_dlp.YoutubeDL(ydl_opts_details) as ydl_detail:
            video_info = ydl_detail.extract_info(full_url, download=False)
            
            if video_info:
                # Fetch the Wikipedia image HERE, inside the same thread
                image_url = get_artist_image(artist_name)
                
                return {
                    'youtube_id': video_info.get("id"),
                    'title': video_info.get('title'),
                    'duration': video_info.get('duration'),
                    'thumbnail': video_info.get('thumbnail'),
                    'artist_name': artist_name,
                    'image_url': image_url,
                    'channel_id': channel_id # include the ID in the final record
                }
    except Exception:
        pass
    return None

all_video_data = []

with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    future_to_task = {executor.submit(process_video_task, task): task for task in video_tasks_list}
    
    for future in tqdm(as_completed(future_to_task), total=total_videos, desc="Processing videos and Wikipedia in parallel", file=sys.stderr):
        result = future.result()
        if result:
            all_video_data.append(result)

# --- PHASE 3: generate the SQL statements and write them to a file ---

artists_to_insert = {}

for video in all_video_data:
    artist_norm = normalize_name(video['artist_name'])
    if artist_norm not in artists_to_insert:
        artists_to_insert[artist_norm] = {
            'name': video['artist_name'],
            'image_url': video['image_url'],
            'channel_id': video['channel_id'] # keep the ID for the artists insert
        }

print(f"\n-- Generating SQL statements and saving to '{OUTPUT_SQL_FILE}' --", file=sys.stderr)

# Write directly to the file so a plain 'python script.py' run produces the output
with open(OUTPUT_SQL_FILE, "w", encoding="utf-8") as f:
    f.write("START TRANSACTION;\n")

    # 1. Insert the artists
    for artist_norm, data in artists_to_insert.items():
        image_sql = f"'{data['image_url'].replace("'", "''")}'" if data['image_url'] else "NULL"
        
        # --- Extend the artists INSERT with the channel_id column ---
        channel_id_sql = f"'{data['channel_id'].replace("'", "''")}'" if data['channel_id'] else "NULL"

        f.write(f"INSERT IGNORE INTO artists (name, name_norm, image_url, channel_id) "
                f"VALUES ('{data['name'].replace("'", "''")}', '{artist_norm}', {image_sql}, {channel_id_sql});\n")

    # 2. Insert the videos
    for video in all_video_data:
        youtube_id = video['youtube_id']
        title = video['title']
        title_norm = normalize_name(title)
        duration = video['duration']
        thumbnail = video['thumbnail']
        artist_norm = normalize_name(video['artist_name'])

        thumbnail_sql = f"'{thumbnail.replace("'", "''")}'" if thumbnail else "NULL"
        duration_sql = duration if duration is not None else "NULL"
        
        f.write(f"INSERT IGNORE INTO youtube_video_cache "
                f"(youtube_id, title, title_norm, artist_id, duration, thumbnail) "
                f"VALUES ("
                f"'{youtube_id}', "
                f"'{title.replace("'", "''")}', "
                f"'{title_norm}', "
                f"(SELECT id FROM artists WHERE name_norm = '{artist_norm}'), " # subquery resolving artist_id
                f"{duration_sql}, "
                f"{thumbnail_sql}"
                f");\n")
                
    f.write("COMMIT;\n")