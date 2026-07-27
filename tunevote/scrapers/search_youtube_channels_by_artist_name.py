"""
search_youtube_channels_by_artist_name.py — find YouTube channels for a list of artist names or URLs.

Description:
    Reads a mixed list of artist names and YouTube URLs from
    tunevote/data/artists.txt and resolves each one to a canonical channel URL.
    Entries that already look like URLs are handed to yt-dlp directly; plain
    names are turned into a YouTube search for "<name> official artist channel"
    and the first hit is taken. Six worker threads process the list in parallel.
    Results are checked against the channels already in
    tunevote/data/unique_channels.txt as well as against each other, and only
    genuinely new channel URLs are appended to that file.

Requirements:
    - Python 3.x
    - Packages: yt-dlp
    - External services: youtube.com (no API key)
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/artists.txt          — one artist name or YouTube URL per line
    tunevote/data/unique_channels.txt  — existing channels, used for deduplication

Outputs:
    tunevote/data/unique_channels.txt  — appended with the newly found channels
    Per-item status lines on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/search_youtube_channels_by_artist_name.py

Notes:
    Taking the first search result is a heuristic: for artists with a common
    name it can pick a fan channel or a topic channel rather than the official
    one, so the output is worth spot-checking. The file opens with a string
    literal holding a browser-console JavaScript snippet that scrapes a
    "similar artists" list from a music site; it is inert here and is kept only
    because it documents how the artist list was originally assembled.
    tunevote/data/artists.txt is not present in the repository and must be
    supplied before running.
"""

'''
(() => {
    const similarSection = document.querySelector("ol.similar-artists");
    if (!similarSection) {
        console.warn("No similar-artists section found");
        return;
    }

    const items = similarSection.querySelectorAll(
        "li.similar-artists-item-wrap h3.similar-artists-item-name a"
    );

    const output = [...items]
        .map(a => a.textContent.trim())
        .join("\n");

    // Fallback clipboard copy for DevTools
    const textarea = document.createElement("textarea");
    textarea.value = output;
    textarea.style.position = "fixed";
    textarea.style.top = "0";
    textarea.style.left = "0";
    textarea.style.opacity = "0";

    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();

    try {
        document.execCommand("copy");
        console.log("✅ Copied to clipboard:");
        console.log(output);
    } catch (err) {
        console.error("❌ Copy failed", err);
    }

    document.body.removeChild(textarea);
})();
'''

import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

CHANNELS_FILE = "tunevote/data/unique_channels.txt"
INPUT_FILE = "tunevote/data/artists.txt"
MAX_WORKERS = 6  # parallel threads (5-8 works best)


# ---------- yt-dlp Optionen ----------
YDL_OPTS = {
    "quiet": True,
    "skip_download": True,
    "extract_flat": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["default"],
        }
    },
}


# ---------- Load the input ----------
def load_inputs(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ---------- Name -> channel (improved) ----------
def search_channel_by_name(name: str) -> str | None:
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            # Append "official artist channel" to narrow the search
            query = f"ytsearch1:{name} official artist channel"
            info = ydl.extract_info(query, download=False)

            if not info or not info.get("entries"):
                return None

            # Take the first result
            entry = info["entries"][0]
            
            # Prefer uploader_url or channel_url
            channel_url = entry.get("uploader_url") or entry.get("channel_url")

            if channel_url:
                # Optional: use the channel ID so every link has the same form
                # (yt-dlp usually provides the ID in the info dict already)
                channel_id = entry.get("channel_id")
                if channel_id:
                    return f"https://www.youtube.com/channel/{channel_id}"
                
                return channel_url

            return None

    except Exception as e:
        # Error handling kept as-is
        print(f"[NAME ERROR] {name}: {e}")
        return None


# ---------- URL → Channel ----------
def get_old_channel_url(url: str) -> str | None:
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

            channel_id = info.get("channel_id")
            if channel_id:
                return f"https://www.youtube.com/channel/{channel_id}"

            return info.get("channel_url") or info.get("uploader_url")

    except Exception as e:
        print(f"[URL ERROR] {url}: {e}")
        return None


# ---------- Dispatcher ----------
def process_item(item: str) -> tuple[str, str | None]:
    if item.startswith("http"):
        return item, get_old_channel_url(item)
    else:
        return item, search_channel_by_name(item)


# ---------- Load the channels already known ----------
def load_existing_channels(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()

    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


# ---------- MAIN ----------
def main():
    inputs = load_inputs(INPUT_FILE)
    existing_channels = load_existing_channels(CHANNELS_FILE)

    new_channels = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_item, item) for item in inputs]

        for future in as_completed(futures):
            item, channel_url = future.result()

            if not channel_url:
                print(f"❌ No channel found for: {item}")
                continue

            if channel_url in existing_channels or channel_url in new_channels:
                print(f"⚠️ Already known: {channel_url}")
                continue

            new_channels.add(channel_url)
            print(f"✅ Found: {channel_url}")

    if new_channels:
        with open(CHANNELS_FILE, "a", encoding="utf-8") as f:
            for url in sorted(new_channels):
                f.write(url + "\n")

    print(f"\n🎉 Done! {len(new_channels)} new channels added.")


if __name__ == "__main__":
    main()
