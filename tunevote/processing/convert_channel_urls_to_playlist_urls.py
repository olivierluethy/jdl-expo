"""
convert_channel_urls_to_playlist_urls.py — turn channel URLs into uploads playlist URLs offline.

Description:
    The network-free counterpart to the resolver scripts in tunevote/scrapers.
    Because a channel's uploads playlist ID is simply its channel ID with the
    leading "UC" replaced by "UU", the conversion needs no lookup at all as long
    as the URL already contains the channel ID. This script reads the channel
    list, skips any line that is not in /channel/ form, performs the two-letter
    substitution, and appends the resulting playlist URL to the output file. It
    runs instantly over any number of lines.

Requirements:
    - Python 3.x
    - Packages: none beyond the standard library
    - External services: none
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/unique_channels.txt — one channel URL per line

Outputs:
    tunevote/data/unique_playlists.txt — appended, one playlist URL per line

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/processing/convert_channel_urls_to_playlist_urls.py

Notes:
    Only URLs containing /channel/ and an ID starting with "UC" are converted;
    @handle and /c/ URLs are skipped silently because their channel ID is not
    present in the URL and can only be obtained from YouTube. Use
    tunevote/scrapers/resolve_channel_list_to_uploads_playlists.py for those. The
    output is opened in append mode and is not deduplicated, so repeated runs
    will add repeated lines.
"""

INPUT_FILE = "tunevote/data/unique_channels.txt"
OUTPUT_FILE = "tunevote/data/unique_playlists.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:

    for line in infile:
        line = line.strip()
        if not line:
            continue

        # Expected format:
        # https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxx
        if "/channel/" not in line:
            continue

        channel_id = line.split("/channel/")[-1]

        # UC -> UU
        if channel_id.startswith("UC"):
            playlist_id = "UU" + channel_id[2:]
        else:
            # Unexpected format -> skip this line
            continue

        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        outfile.write(playlist_url + "\n")
