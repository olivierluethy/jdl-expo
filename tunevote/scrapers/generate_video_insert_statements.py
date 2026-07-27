#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import yt_dlp
import time
import requests
import re
import sys

playlists = [
    "https://www.youtube.com/playlist?list=UUuRwdG_2dvII6VaJPppXqAw",
    # weitere Playlists hier hinzufügen
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
    
    # 1. Suche nach dem exakten Künstler-Seitentitel
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
        print(f"Wikipedia Search Fehler für '{artist_name}': {e}", file=sys.stderr)
        return None
    
    searches = search_data.get("query", {}).get("search", [])
    if not searches:
        return None
    page_title = searches[0]["title"]
    
    # 2. Hole Bild (original bevorzugt, sonst high-res thumbnail)
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
        print(f"Wikipedia Image Fehler für '{page_title}': {e}", file=sys.stderr)
        return None
    
    pages = img_data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "original" in page:
            return page["original"]["source"]
        if "thumbnail" in page:
            return page["thumbnail"]["source"]
    
    return None

# yt_dlp Optionen
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
        print(f"\nDurchsuche Playlist: {playlist_url}", file=sys.stderr)
        
        info = ydl_playlist.extract_info(playlist_url, download=False)
        artist = info.get("uploader") or info.get("channel") or "Unbekannter Künstler"
        artist_norm = normalize_name(artist)
        
        print(f"Künstler erkannt: {artist}", file=sys.stderr)
        
        # Wikipedia-Bild holen
        image_url = get_artist_image(artist)
        if image_url:
            print(f"Profilbild gefunden: {image_url}", file=sys.stderr)
        else:
            print("Kein Profilbild auf Wikipedia gefunden.", file=sys.stderr)
            image_url = None  # wird als NULL in SQL
        
        # INSERT für Artist
        image_sql = f"'{image_url.replace("'", "''")}'" if image_url else "NULL"
        print(f"INSERT IGNORE INTO artists (name, name_norm, image_url) "
              f"VALUES ('{artist.replace("'", "''")}', '{artist_norm}', {image_sql});")
        
        # Videos verarbeiten
        for entry in info.get("entries", []):
            if not entry or "url" not in entry:
                continue
            
            video_url = entry["url"]  # z.B. watch?v=...
            full_url = f"https://www.youtube.com/watch?v={video_url}" if len(video_url) == 11 else video_url
            
            try:
                video_info = ydl_video.extract_info(full_url, download=False)
                
                youtube_id = video_info.get("id")
                if not youtube_id:
                    continue
                
                title = video_info.get("title") or "Unbekannter Titel"
                title_norm = normalize_name(title)
                
                duration = video_info.get("duration")  # Sekunden, kann None sein
                
                # Beste Thumbnail-URL (highest resolution)
                thumbnails = video_info.get("thumbnails", [])
                thumbnail = thumbnails[-1]["url"] if thumbnails else None
                
                thumbnail_sql = f"'{thumbnail.replace("'", "''")}'" if thumbnail else "NULL"
                duration_sql = duration if duration is not None else "NULL"
                
                # INSERT für Video
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
                print(f"Fehler beim Extrahieren von {full_url}: {e}", file=sys.stderr)
            
            time.sleep(0.2)  # höflich zu YouTube
        
        print("", file=sys.stderr)  # Leerzeile zwischen Künstlern

print("\nFertig! INSERT-Statements wurden ausgegeben.", file=sys.stderr)