'''
(() => {
    const similarSection = document.querySelector("ol.similar-artists");
    if (!similarSection) {
        console.warn("Keine similar-artists Section gefunden");
        return;
    }

    const items = similarSection.querySelectorAll(
        "li.similar-artists-item-wrap h3.similar-artists-item-name a"
    );

    const output = [...items]
        .map(a => a.textContent.trim())
        .join("\n");

    // Fallback-Kopieren für DevTools
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
        console.log("✅ In Zwischenablage kopiert:");
        console.log(output);
    } catch (err) {
        console.error("❌ Kopieren fehlgeschlagen", err);
    }

    document.body.removeChild(textarea);
})();
'''

import yt_dlp
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

CHANNELS_FILE = "unique_channels.txt"
INPUT_FILE = "artists.txt"
MAX_WORKERS = 6  # parallel threads (5–8 ist optimal)


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


# ---------- Input laden ----------
def load_inputs(path: str) -> list[str]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} nicht gefunden")

    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


# ---------- Name → Channel ----------
def search_channel_by_name(name: str) -> str | None:
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            query = f"ytsearch1:{name} channel"
            info = ydl.extract_info(query, download=False)

            if not info or not info.get("entries"):
                return None

            entry = info["entries"][0]

            channel_id = entry.get("channel_id")
            if channel_id:
                return f"https://www.youtube.com/channel/{channel_id}"

            return entry.get("channel_url")

    except Exception as e:
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


# ---------- Bestehende Channels laden ----------
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
                print(f"❌ Kein Channel gefunden für: {item}")
                continue

            if channel_url in existing_channels or channel_url in new_channels:
                print(f"⚠️ Bereits vorhanden: {channel_url}")
                continue

            new_channels.add(channel_url)
            print(f"✅ Gefunden: {channel_url}")

    if new_channels:
        with open(CHANNELS_FILE, "a", encoding="utf-8") as f:
            for url in sorted(new_channels):
                f.write(url + "\n")

    print(f"\n🎉 Fertig! {len(new_channels)} neue Channels hinzugefügt.")


if __name__ == "__main__":
    main()
