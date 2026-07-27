"""
resolve_channel_handle_to_uploads_playlist.py — resolve a YouTube @handle to its channel ID and uploads playlist.

Description:
    Takes a single YouTube channel URL in @handle form and asks yt-dlp for the
    channel metadata. From the returned channel ID (which always starts with
    "UC") it derives the channel's uploads playlist ID by replacing the leading
    "UC" with "UU" — an undocumented YouTube convention that yields a playlist
    containing every public upload of that channel. It prints the canonical
    channel URL, the channel ID, the uploads playlist URL and the playlist ID.
    The target URL is hardcoded in the INPUT constant near the top of the file.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key; yt-dlp scrapes the public site)
    - Environment variables / credentials needed: none

Inputs:
    The INPUT constant inside this file. No command-line arguments are parsed.

Outputs:
    Four lines on stdout. No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/resolve_channel_handle_to_uploads_playlist.py

Notes:
    Edit INPUT to point at a different channel. If yt-dlp cannot determine the
    channel ID the script prints an error and suggests retrying with a /videos
    suffix on the URL. YouTube rate-limits aggressive use of yt-dlp.
"""

from yt_dlp import YoutubeDL

# Accepts either an @handle URL or a regular channel URL
INPUT = "https://www.youtube.com/@CBSMornings/"

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
    # Canonical channel URL
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    
    # Uploads playlist: replace the leading "UC" with "UU"
    uploads_playlist_id = "UU" + channel_id[2:]
    uploads_playlist_url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

    print("Channel URL:", channel_url)
    print("Channel ID:", channel_id)
    print()
    print("Uploads playlist URL:", uploads_playlist_url)
    print("Uploads playlist ID:", uploads_playlist_id)
else:
    print("Error: could not extract the channel ID.")
    print("Try a different URL form, for example with /videos at the end.")