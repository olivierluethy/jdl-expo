#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_video_insert_statements_duplicate.py — byte-identical copy of generate_video_insert_statements.py.

Description:
    Walks each playlist in the hardcoded playlists list and treats the playlist
    uploader as the artist. For that artist it queries the English Wikipedia API
    twice — once to find the best-matching page title, once to fetch that page's
    lead image — and emits an INSERT IGNORE for the artists table. It then
    fetches metadata for every video in the playlist and emits an INSERT IGNORE
    into youtube_video_cache for each, resolving the artist_id with a subquery on
    the normalized artist name. All SQL goes to stdout, progress to stderr.

Requirements:
    - Python 3.x
    - Packages: yt-dlp, requests
    - External services: youtube.com, en.wikipedia.org (neither needs a key)
    - Environment variables / credentials needed: none

Inputs:
    The playlists list inside this file. No command-line arguments are parsed.

Outputs:
    SQL INSERT statements on stdout; progress and errors on stderr.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/generate_video_insert_statements_duplicate.py > inserts.sql

Notes:
    This file is a byte-for-byte duplicate of
    generate_video_insert_statements.py, which is why the duplication is stated
    in its name rather than hidden behind an invented difference. It was kept
    because it is not empty and the reorganization rules forbid deleting
    non-empty files. Nothing depends on it — deleting it is safe once you have
    confirmed the two files are still identical.
"""


import yt_dlp
import time
import requests
import re
import sys

playlists = [
    "https://www.youtube.com/playlist?list=UUuRwdG_2dvII6VaJPppXqAw",
    # add further playlists here
]

def normalize_name(name):
    if not name:
        return ""
    normalized = name.lower()
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def get_artist_image(artist_name):
    if not artist_name:
        return None
    
    wp_url = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "ArtistImageFetcher/1.0 (your-email@example.com)"}
    
    # 1. Find the best-matching Wikipedia page title for the artist
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": artist_name,
        "format": "json",
        "srlimit": 1,
        "origin": "*"
    }
    try:
        search_resp = requests.get(wp_url, params=search_params, headers=headers, timeout=10)
        search_data = search_resp.json()
    except Exception as e:
        print(f"Wikipedia search error for '{artist_name}': {e}", file=sys.stderr)
        return None
    
    searches = search_data.get("query", {}).get("search", [])
    if not searches:
        return None
    page_title = searches[0]["title"]
    
    # 2. Fetch the image, preferring the original over a high-res thumbnail
    img_params = {
        "action": "query",
        "titles": page_title,
        "format": "json",
        "prop": "pageimages",
        "pithumbsize": 1024,
        "piprop": "thumbnail|original",
        "origin": "*"
    }
    try:
        img_resp = requests.get(wp_url, params=img_params, headers=headers, timeout=10)
        img_data = img_resp.json()
    except Exception as e:
        print(f"Wikipedia image error for '{page_title}': {e}", file=sys.stderr)
        return None
    
    pages = img_data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "original" in page:
            return page["original"]["source"]
        if "thumbnail" in page:
            return page["thumbnail"]["source"]
    
    return None

# yt_dlp options
ydl_playlist_opts = {
    'quiet': True,
    'extract_flat': True,
    'skip_download': True,
}

ydl_video_opts = {
    'quiet': True,
    'skip_download': True,
}

with yt_dlp.YoutubeDL(ydl_playlist_opts) as ydl_playlist, \
     yt_dlp.YoutubeDL(ydl_video_opts) as ydl_video:

    for playlist_url in playlists:
        print(f"\nScanning playlist: {playlist_url}", file=sys.stderr)
        
        info = ydl_playlist.extract_info(playlist_url, download=False)
        artist = info.get("uploader") or info.get("channel") or "Unknown artist"
        artist_norm = normalize_name(artist)
        
        print(f"Artist detected: {artist}", file=sys.stderr)
        
        # Fetch the artist image from Wikipedia
        image_url = get_artist_image(artist)
        if image_url:
            print(f"Profile image found: {image_url}", file=sys.stderr)
        else:
            print("No profile image found on Wikipedia.", file=sys.stderr)
            image_url = None  # written as NULL in the SQL output
        
        # INSERT for the artist
        image_sql = f"'{image_url.replace("'", "''")}'" if image_url else "NULL"
        print(f"INSERT IGNORE INTO artists (name, name_norm, image_url) "
              f"VALUES ('{artist.replace("'", "''")}', '{artist_norm}', {image_sql});")
        
        # Process the videos
        for entry in info.get("entries", []):
            if not entry or "url" not in entry:
                continue
            
            video_url = entry["url"]  # for example watch?v=...
            full_url = f"https://www.youtube.com/watch?v={video_url}" if len(video_url) == 11 else video_url
            
            try:
                video_info = ydl_video.extract_info(full_url, download=False)
                
                youtube_id = video_info.get("id")
                if not youtube_id:
                    continue
                
                title = video_info.get("title") or "Unknown title"
                title_norm = normalize_name(title)
                
                duration = video_info.get("duration")  # seconds, may be None
                
                # Best thumbnail URL (highest resolution)
                thumbnails = video_info.get("thumbnails", [])
                thumbnail = thumbnails[-1]["url"] if thumbnails else None
                
                thumbnail_sql = f"'{thumbnail.replace("'", "''")}'" if thumbnail else "NULL"
                duration_sql = duration if duration is not None else "NULL"
                
                # INSERT for the video
                print(f"INSERT IGNORE INTO youtube_video_cache "
                      f"(youtube_id, title, title_norm, artist_id, duration, thumbnail) "
                      f"VALUES ("
                      f"'{youtube_id}', "
                      f"'{title.replace("'", "''")}', "
                      f"'{title_norm}', "
                      f"(SELECT id FROM artists WHERE name_norm = '{artist_norm}'), "
                      f"{duration_sql}, "
                      f"{thumbnail_sql}"
                      f");")
                
            except Exception as e:
                print(f"Error extracting {full_url}: {e}", file=sys.stderr)
            
            time.sleep(0.2)  # stay polite towards YouTube
        
        print("", file=sys.stderr)  # blank line between artists

print("\nDone! INSERT statements have been written to stdout.", file=sys.stderr)