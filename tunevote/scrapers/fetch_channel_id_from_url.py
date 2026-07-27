#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_channel_id_from_url.py — print the YouTube channel ID for one channel URL.

Description:
    The smallest building block of the channel pipeline. It hands a single
    hardcoded channel URL to yt-dlp, reads the channel_id field out of the
    returned metadata and prints it. The channel ID is the input that every
    other step needs, because appending it (with "UC" swapped for "UU") to a
    playlist URL exposes the channel's complete upload history — which proved
    more reliable than scraping the /videos page, where the newest uploads were
    sometimes missing.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    The url variable inside this file. No command-line arguments are parsed.

Outputs:
    One line on stdout: "Channel-ID: <id>". No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/fetch_channel_id_from_url.py

Notes:
    Accepts /channel/... and /c/... URL forms. Unlike the other scripts here it
    runs yt-dlp with default options, so yt-dlp prints its own progress output.
"""

import sys
import re
# --- Imports ---
# This script extracts the channel ID of a YouTube channel from its URL.
# It uses the yt_dlp library to retrieve the channel information.
# Required library: yt_dlp (installable via pip)
# pip install yt_dlp
# --- Extracting the channel ID ---
# The goal is to extract the channel ID so that a small trick gives access to a
# playlist holding every video of that channel: the channel ID is needed to build
# the playlist URL in "UU" form (that is, "UU" plus the ID without its "UC" prefix).
# This really does yield all videos of a channel. The earlier approach, which used
# only the channel name, worked but did not always pick up the newest uploads.
# Going through the channel ID is reliable.

from yt_dlp import YoutubeDL

url = "https://www.youtube.com/channel/UC-pOuHFcndLpyfWSPVqXt_A"  # or https://www.youtube.com/c/ChannelName

ydl_opts = {}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    channel_id = info.get("channel_id")
    print("Channel ID:", channel_id)
