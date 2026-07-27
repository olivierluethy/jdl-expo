"""
generate_duration_update_statements.py — build SQL UPDATEs that backfill missing video durations.

Description:
    Repairs rows in youtube_video_cache whose duration was scraped as empty. The
    original extraction read the runtime from the video listing page, where a
    music badge sometimes covered the duration and produced a blank value. This
    script takes the affected video IDs, pulled from the database as SQL-style
    tuples and pasted into the raw_input string, extracts them with a regular
    expression, asks yt-dlp for each video's real duration in seconds, and writes
    one UPDATE statement per video. If the target output file already exists the
    name is given an incrementing counter so an earlier batch is never
    overwritten.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    The raw_input string inside this file, holding rows of the form ('videoId'),

Outputs:
    tunevote/data/update_durations.txt — or update_durations1.txt, 2, … if that
    name is taken. One UPDATE statement per video; failures are written as SQL
    comments so the file stays valid. Progress goes to stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/processing/generate_duration_update_statements.py

Notes:
    The output path is resolved relative to this file, not to the working
    directory, so the file always lands in tunevote/data regardless of where the
    script is started. Videos that have since been deleted or made private
    cannot be repaired and are recorded as commented-out errors. Review the
    generated statements before applying them to a live database.
"""

# This script fetches the duration of YouTube videos by their IDs and
# generates SQL UPDATE statements, which are written to a file.
# It uses the yt_dlp library to retrieve the video information.
## Required library: yt_dlp (installable via pip)
# pip install yt_dlp
# --- Imports ---
# The problem: the durations of some YouTube videos were extracted incorrectly,
# because a music badge shown over the runtime on the listing page caused the
# duration to come back empty for part of the catalogue. The extraction script
# was then adjusted so the duration is always read correctly, regardless of that
# badge. That alone was not enough, though: the videos already stored without a
# duration had to be repaired. So every video ID with a missing duration was
# pulled from the database, those IDs were passed to this interface to fetch the
# duration from each video, and the result was turned into ready-made SQL UPDATE
# statements that fill the empty column for all affected videos.

import yt_dlp
import os
import re

# --- Raw input, pasted exactly as it comes out of the database ---
raw_input = """
('xyno53dCO7Q'),
('I2XfVml6o24'),
('QUzCFEJh8-I');
"""

# --- Extract the IDs ---
video_ids = re.findall(r"\('([^']+)'\)", raw_input)

# --- Output file for the SQL statements ---
base_filename = '../data/update_durations.txt'
output_file = os.path.join(os.path.dirname(__file__), base_filename)

# If the file already exists, add an incrementing counter to the name
counter = 1
while os.path.exists(output_file):
    name, ext = os.path.splitext(base_filename)
    output_file = os.path.join(os.path.dirname(__file__), f"{name}{counter}{ext}")
    counter += 1

# --- Function that fetches the duration in seconds ---
def get_duration_seconds(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'quiet': True, 'skip_download': True, 'forcejson': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return int(info['duration'])

# --- Generate the SQL statements ---
with open(output_file, 'w', encoding='utf-8') as f:
    for vid in video_ids:
        try:
            duration_sec = get_duration_seconds(vid)
            sql = f"UPDATE youtube_video_cache SET duration = {duration_sec} WHERE youtube_id = '{vid}';\n"
            f.write(sql)
            print(f"Processed {vid}: {duration_sec} seconds")
        except Exception as e:
            print(f"Error on {vid}: {e}")
            f.write(f"-- Error on {vid}: {e}\n")

print(f"Done! SQL statements were saved to '{output_file}'.")