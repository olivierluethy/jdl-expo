"""
extract_channel_urls_from_video_ids.py — recover the owning channel for each video ID in a dump.

Description:
    Works backwards from video IDs to the channels that published them, which
    avoids having to visit every channel by hand. It reads a text file of
    SQL-tuple-shaped rows, pulls the video ID out of each row with a regular
    expression, and skips any ID already listed in the resume log. For every
    remaining video it asks yt-dlp for the channel_url and appends it to the
    unique channels file if it has not been seen before. Each processed ID is
    written to the resume log immediately and flushed, so a crash costs at most
    one lookup. When the run finishes, the input file is rewritten with the
    processed rows removed.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/artists_output(1).txt — SQL-tuple rows, produced by
                                          tunevote/processing/extract_unique_artists_from_dump.py
    tunevote/data/processed_videos.txt  — resume log, read if present

Outputs:
    tunevote/data/unique_channels.txt  — appended with newly discovered channels
    tunevote/data/processed_videos.txt — appended with every ID attempted
    tunevote/data/artists_output(1).txt — rewritten without processed rows
    A progress bar and per-video status lines on stdout.

Notes:
    Videos that fail are also marked processed so they are not retried forever;
    deleted and private videos are reported separately from real errors. A
    random pause of 0.5–2.1 seconds after every lookup keeps the request pattern
    from looking automated, which makes a full run over thousands of videos slow
    — budget hours, not minutes. The final cleanup step builds one large regex
    by joining every processed ID with "|", which becomes expensive once the
    resume log holds tens of thousands of entries.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/extract_channel_urls_from_video_ids.py
"""

import re
import yt_dlp
import time
import random
import sys
import os

# === Files ===
raw_file = "tunevote/data/artists_output(1).txt"          # The large SQL-shaped input goes here
processed_file = "tunevote/data/processed_videos.txt"   # Created automatically and appended to
output_file = "tunevote/data/unique_channels.txt"

# === Load the video IDs already processed ===
processed_ids = set()
if os.path.exists(processed_file):
    with open(processed_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                processed_ids.add(line)
    print(f"Skipping {len(processed_ids)} already processed videos.\n")

# === Load the raw input from a file (no longer a string inside the code) ===
if not os.path.exists(raw_file):
    print(f"Error: {raw_file} not found!")
    sys.exit(1)

with open(raw_file, 'r', encoding='utf-8') as f:
    raw_input = f.read()

# === Regex for the row tuples ===
tuple_pattern = re.compile(
    r"\(\s*\d+\s*,\s*'([^']+)'\s*,"  # only the video ID matters here (second field)
)

# Extract every video ID
all_video_ids = tuple_pattern.findall(raw_input)
print(f"Found in total: {len(all_video_ids)} videos in {raw_file}")

# Keep only the ones not processed yet
videos_to_process = [vid for vid in all_video_ids if vid not in processed_ids]
print(f"Still to process: {len(videos_to_process)}\n")

if not videos_to_process:
    print("All videos already processed. Done.")
    sys.exit(0)

# === Load the channels already discovered ===
existing_channels = set()
if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                existing_channels.add(line)

# === yt-dlp tuning ===
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'extract_flat': False,           # needed to get channel_url
    'cachedir': False,
    'retries': 5,
    'sleep_interval': 0.4,
    'max_sleep_interval': 1.6,
}

# Open the output files in append mode
with yt_dlp.YoutubeDL(ydl_opts) as ydl, \
     open(output_file, 'a', encoding='utf-8') as channel_file, \
     open(processed_file, 'a', encoding='utf-8') as done_file:

    for idx, video_id in enumerate(videos_to_process, 1):
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            info = ydl.extract_info(video_url, download=False)
            channel_url = info.get('channel_url')

            if channel_url and channel_url not in existing_channels:
                channel_file.write(channel_url + '\n')
                existing_channels.add(channel_url)
                print(f"[+] New: {info.get('channel')} | {channel_url}")
            else:
                print(f"[~] Duplicate: {channel_url or 'no channel'}")

            # === IMPORTANT: mark this video as done ===
            done_file.write(video_id + '\n')
            done_file.flush()  # Flush immediately so a crash cannot lose progress

        except Exception as e:
            error_msg = str(e).lower()
            if "private" in error_msg or "unavailable" in error_msg or "deleted" in error_msg:
                print(f"[!] Deleted/private: {video_id}")
            else:
                print(f"[!] Error on {video_id}: {e}")
            # Mark failures as done too, so they are not retried forever
            done_file.write(video_id + '\n')
            done_file.flush()

        # Progress bar
        progress = (idx / len(videos_to_process)) * 100
        bar_length = 40
        filled = int(bar_length * idx // len(videos_to_process))
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r{bar} {progress:6.2f}% ({idx}/{len(videos_to_process)})", end='', flush=True)

        # Human-like pause between requests
        time.sleep(random.uniform(0.5, 2.1))

# === Optional: prune the input file so only unprocessed rows remain ===
print("\n\nPruning the raw input file ...")
remaining_lines = []
with open(raw_file, 'r', encoding='utf-8') as f:
    for line in f:
        if re.search(r"\(\s*\d+\s*,\s*'(" + "|".join(processed_ids) + r")'", line):
            continue  # already processed -> drop this row
        remaining_lines.append(line)

with open(raw_file, 'w', encoding='utf-8') as f:
    f.writelines(remaining_lines)

print(f"\nDone! {len(videos_to_process)} videos processed.")
print(f"Unique channels: {len(existing_channels)} → {output_file}")
print(f"Remaining in {raw_file}: {len(remaining_lines)} lines")