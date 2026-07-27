"""
print_uploads_playlist_for_channel.py — print the uploads playlist URL for one channel.

Description:
    Resolves a single hardcoded channel URL to its uploads playlist. It first
    asks yt-dlp for the channel ID; if yt-dlp does not return one, it falls back
    to pulling the ID straight out of the URL with a regular expression. The
    channel ID is then converted to the uploads playlist ID by replacing the
    leading "UC" with "UU", and the resulting playlist URL is printed. yt-dlp's
    own logging is silenced so the only output is the URL itself, which makes
    the script easy to pipe into another command.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    The urls list inside this file. No command-line arguments are parsed.

Outputs:
    One playlist URL per entry in urls, on stdout. No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/print_uploads_playlist_for_channel.py

Notes:
    print_uploads_playlist_for_channel_uc8gxc2f.py in this same folder contains
    identical logic and differs only in the channel it targets. Both were kept
    because neither file is empty; consider consolidating them.
"""

from yt_dlp import YoutubeDL
import re

class SilentLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

urls = [
    "https://www.youtube.com/channel/UCkajFamD9odK1vtdXMhEUcg"
]

ydl_opts = {
    "quiet": True,
    "extract_flat": True,
    "logger": SilentLogger(),
}

for url in urls:
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # 1. Normal path: take the channel ID from yt-dlp's metadata
        channel_id = info.get("channel_id") or info.get("id")

        # 2. Edge case: yt-dlp did not report an ID, so recover it from the URL
        if not channel_id:
            match = re.search(r"(UC[a-zA-Z0-9_-]{22})", url)
            if match:
                channel_id = match.group(1)

        if not channel_id:
            continue

        # 3. Build the uploads playlist ID by swapping the leading UC for UU
        uploads_playlist_id = "UU" + channel_id[2:]
        playlist_url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

        print(playlist_url)
