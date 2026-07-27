"""
check_channel_availability.py — sort a channel list into reachable and dead channels.

Description:
    Maintenance tool for the channel list, which accumulates dead entries as
    channels are renamed, made private or deleted. It reads every URL from the
    channel file, skipping blank lines and lines starting with "#", and probes
    each one with yt-dlp across eight threads. A channel counts as available if
    yt-dlp returns metadata with a title or an entries list. The results are
    written to two separate files, each headed with the timestamp of the run, and
    a summary of the totals is printed at the end.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/unique_channels.txt — one channel URL per line

Outputs:
    tunevote/data/available_channels.txt — overwritten, reachable channels
    tunevote/data/dead_channels.txt      — overwritten, unreachable channels
    Per-channel status and a summary on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/check_channel_availability.py

Notes:
    Both output files are opened with mode "w" and are deleted outright when the
    corresponding list comes back empty, so a run against an unreachable network
    can remove a previous good result — keep a copy if that matters. A transient
    network failure is indistinguishable from a genuinely dead channel here, so
    confirm before acting on the dead list. Two of the informational messages use
    plain strings where an f-string was intended and therefore print the literal
    placeholder text; this is cosmetic and was left untouched.
"""

import yt_dlp
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================
# File names
# =============================
input_file = 'tunevote/data/unique_channels.txt'
available_file = 'tunevote/data/available_channels.txt'
dead_file = 'tunevote/data/dead_channels.txt'

# =============================
# Function that probes a single channel
# =============================
def check_channel_availability(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url.strip(), download=False)
        if info and (info.get('title') or info.get('entries') is not None):
            return True  # Channel exists
        return False     # Channel does not exist or is invalid
    except Exception:
        return False

# =============================
# Check the input file
# =============================
if not os.path.exists(input_file):
    print(f"❌ Error: the file '{input_file}' was not found.")
    exit()

with open(input_file, 'r', encoding='utf-8') as f:
    channels = [line.strip() for line in f if line.strip() and not line.startswith('#')]

if not channels:
    print("⚠️ No channels found in the file.")
    exit()

# =============================
# Prepare the result lists
# =============================
available = []
dead = []

print(f"{len(channels)} channels found – starting the check with 8 threads...\n")

# =============================
# Probe the channels with a thread pool
# =============================
with ThreadPoolExecutor(max_workers=8) as executor:
    future_to_url = {executor.submit(check_channel_availability, url): url for url in channels}
    for i, future in enumerate(as_completed(future_to_url), 1):
        url = future_to_url[future]
        try:
            result = future.result()
            if result:
                available.append(url)
                status = "✅ Available"
            else:
                dead.append(url)
                status = "❌ Unavailable"
        except Exception as e:
            dead.append(url)
            status = f"❌ Error: {e}"

        print(f"[{i}/{len(channels)}] {url}")
        print(f" {status}")
        print("-" * 60)

# =============================
# Save the results (files are created or overwritten, never appended)
# =============================
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    # Available channels: only write a file if there are any
    if available:
        with open(available_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Available channels – checked on {timestamp} ===\n\n")
            f.write("\n".join(available) + "\n")
        print(f"✅ {len(available)} available channels saved to '{available_file}'.")
    else:
        # If none are available, remove any stale file from an earlier run
        if os.path.exists(available_file):
            os.remove(available_file)
        print("ℹ️ No available channels → file '{available_file}' not created/removed.")

    # Dead channels: only write a file if there are any
    if dead:
        with open(dead_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Dead channels – checked on {timestamp} ===\n\n")
            f.write("\n".join(dead) + "\n")
        print(f"❌ {len(dead)} dead channels saved to '{dead_file}'.")
    else:
        if os.path.exists(dead_file):
            os.remove(dead_file)
        print("ℹ️ No dead channels → file '{dead_file}' not created/removed.")

except Exception as e:
    print(f"\n❌ Error while writing the files: {e}")

# =============================
# Summary
# =============================
print("\n" + "="*60)
print("Check complete!")
print(f"Total: {len(channels)}")
print(f"✅ Available: {len(available)}")
print(f"❌ Unavailable: {len(dead)}")
print("="*60)