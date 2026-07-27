"""
resolve_channel_list_to_uploads_playlists.py — batch-convert a channel list into uploads playlist URLs.

Description:
    The production version of the single-channel resolvers in this folder. It
    reads every channel URL from tunevote/data/unique_channels.txt, subtracts
    the ones already recorded in tunevote/data/processed_channels.txt, and
    resolves the remainder to uploads playlist URLs using a pool of ten threads.
    Each successful result is appended to tunevote/data/unique_playlists.txt and
    the source URL is appended to the processed file, so an interrupted run can
    simply be restarted. Ctrl-C is caught and the results gathered so far are
    still flushed to disk before the script exits.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/unique_channels.txt   — one channel URL per line
    tunevote/data/processed_channels.txt — resume log, read if present

Outputs:
    tunevote/data/unique_playlists.txt   — appended, one playlist URL per line
    tunevote/data/processed_channels.txt — appended, one channel URL per line
    Progress lines on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/resolve_channel_list_to_uploads_playlists.py

Notes:
    Both output files are opened in append mode, so re-running never truncates
    earlier results. Ten concurrent workers is a deliberate compromise; raising
    it increases the chance of YouTube throttling the requests. Channels that
    fail are not written to the processed file and will be retried next run.
"""

from yt_dlp import YoutubeDL
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

CHANNELS_FILE = "tunevote/data/unique_channels.txt"
PLAYLISTS_FILE = "tunevote/data/unique_playlists.txt"
PROCESSED_FILE = "tunevote/data/processed_channels.txt"

class SilentLogger:
    def debug(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        pass

ydl_opts = {
    "quiet": True,
    "extract_flat": True,
    "logger": SilentLogger(),
}

def load_lines(filepath):
    if not os.path.exists(filepath):
        return set()
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def append_lines(filepath, lines):
    if not lines:
        return
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def extract_channel_id(info, url):
    channel_id = info.get("channel_id") or info.get("id")
    if not channel_id:
        match = re.search(r"(UC[a-zA-Z0-9_-]{22})", url)
        if match:
            channel_id = match.group(1)
    return channel_id

def channel_to_uploads_playlist(channel_id):
    return "https://www.youtube.com/playlist?list=UU" + channel_id[2:]

def process_channel(url):
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        channel_id = extract_channel_id(info, url)
        if not channel_id:
            return url, None, "⚠ No channel ID"
        playlist_url = channel_to_uploads_playlist(channel_id)
        return url, playlist_url, None
    except Exception as e:
        return url, None, str(e)

def main():
    all_channels = load_lines(CHANNELS_FILE)
    processed_channels = load_lines(PROCESSED_FILE)
    remaining_channels = [u for u in all_channels if u not in processed_channels]

    total = len(remaining_channels)
    if total == 0:
        print("✅ All channels already processed.")
        return

    print(f"▶ Processing {total} remaining channels...")

    playlists_to_append = []
    processed_to_append = []
    completed_count = 0

    max_workers = 10  # 10-20 is a reasonable range to experiment with
    futures = []
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_channel, url) for url in remaining_channels]
            for future in as_completed(futures):
                url, playlist_url, error = future.result()
                completed_count += 1

                if playlist_url:
                    playlists_to_append.append(playlist_url)
                    processed_to_append.append(url)
                    status = f"✔"
                else:
                    status = f"❌ ({error})"

                print(f"[{completed_count}/{total}] {status} {url}")

    except KeyboardInterrupt:
        print("\n⏹ KeyboardInterrupt detected! Saving cached results...")
    finally:
        # Always make sure the results gathered so far are written out
        append_lines(PLAYLISTS_FILE, playlists_to_append)
        append_lines(PROCESSED_FILE, processed_to_append)
        print(f"✅ Saved {len(processed_to_append)} processed channels. {total - completed_count} remaining.")

if __name__ == "__main__":
    main()
