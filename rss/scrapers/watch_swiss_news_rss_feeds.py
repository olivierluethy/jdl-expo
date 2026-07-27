"""
watch_swiss_news_rss_feeds.py — poll Swiss news RSS feeds and alert on keyword hits.

Description:
    Runs as a long-lived watcher over roughly forty RSS feeds from the major
    Swiss outlets: 20 Minuten, Blick, Luzerner Zeitung, NZZ and Tages-Anzeiger.
    Every cycle it parses each feed, inspects the fifteen newest entries and
    compares their headlines against the search terms case-insensitively. A new
    match is printed and pushed to an ntfy topic as a high-priority notification,
    and its link is remembered so the same article is never reported twice. If a
    cycle produces no match at all, a low-priority status message is sent instead
    so it stays obvious that the watcher is still alive. The loop then sleeps for
    the configured interval and starts again.

Requirements:
    - Python 3.x
    - Packages: feedparser, requests
    - External services: the listed RSS feeds and ntfy.sh
    - Environment variables / credentials needed: none — the ntfy topic is
      hardcoded and acts as a shared secret, see SECURITY_NOTES.md

Inputs:
    The FEEDS list, SUCHWOERTER search terms and INTERVAL constant in this file.

Outputs:
    Push notifications to the configured ntfy topic; match reports on stdout.
    No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python rss/scrapers/watch_swiss_news_rss_feeds.py

Notes:
    This script never terminates on its own — stop it with Ctrl-C. Seen links are
    held in memory only, so restarting it will re-report articles that are still
    in the feeds. The heartbeat fires once per cycle, which at the default 240
    second interval is about fifteen notifications an hour; raise INTERVAL if
    that is too noisy. One Blick feed is listed twice, which is harmless because
    matches are deduplicated by link.
"""

import feedparser
import time
import datetime
import requests

# ────────────────────────────────────────────────
#          CONFIGURATION - ADJUST HERE
# ────────────────────────────────────────────────

NTFY_SERVER = "https://ntfy.sh"
NTFY_TOPIC  = "derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"

INTERVAL = 240  # 4 minutes
SUCHWOERTER = ["helvetus", "stralium"]  # matched case-insensitively

FEEDS = [
    ## RSS feeds from 20minuten.ch
    "https://partner-feeds.20min.ch/rss/20minuten/",
    "https://partner-feeds.20min.ch/rss/20minuten/schweiz",
    "https://partner-feeds.20min.ch/rss/20minuten/schweiz/wirtschaft",
    "https://partner-feeds.20min.ch/rss/20minuten/schweiz/politik",
    "https://partner-feeds.20min.ch/rss/20minuten/schweiz/finanzen",
    ## RSS feeds from Blick.ch
    "https://www.blick.ch/schweiz/rss.xml",           # ← priority 1
    "https://www.blick.ch/rss.xml",                   # everything
    "https://www.blick.ch/wirtschaft/rss.xml",        # often company-related
    "https://www.blick.ch/people-tv/rss.xml",         # Helvetus occasionally appears here
    "https://www.blick.ch/ausland/rss.xml",
    "https://www.blick.ch/wirtschaft/rss.xml",
    "https://www.blick.ch/politik/rss.xml",
    "https://www.blick.ch/sport/rss.xml",
    ## RSS feeds from Luzerner Zeitung
    "https://www.luzernerzeitung.ch/zentralschweiz.rss",
    "https://www.luzernerzeitung.ch/zentralschweiz/luzern.rss",
    "https://www.luzernerzeitung.ch/schweiz.rss",
    "https://www.luzernerzeitung.ch/international.rss",
    "https://www.luzernerzeitung.ch/wirtschaft.rss",
    "https://www.luzernerzeitung.ch/leben/ratgeber.rss",
    "https://www.luzernerzeitung.ch/meinung/leserbriefe.rss",
    "https://www.luzernerzeitung.ch/meinung/kommentare.rss",
    ## RSS feeds from NZZ
    "https://www.nzz.ch/startseite.rss",
    "https://www.nzz.ch/schweiz.rss",
    "https://www.nzz.ch/wirtschaft.rss",
    "https://www.nzz.ch/international.rss",
    "https://www.nzz.ch/recent.rss",
    ## RSS feeds from Tages-Anzeiger
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/front",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/schweiz",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/wirtschaft",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/wirtschaft/recht-und-konsum",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/sonntagszeitung",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/panorama/vermischtes",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/ausland",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/ausland/europa",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/wirtschaft-news",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/news-heute",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/aktuell",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/wirtschaft/kurzmeldungen-wirtschaft",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/podcast/unter-verdacht",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/news",
    "https://partner-feeds.publishing.tamedia.ch/rss/tagesanzeiger/news-uebersicht",
]

gesehen = set()

# ────────────────────────────────────────────────
#        Function that sends a message to ntfy
# ────────────────────────────────────────────────

def sende_ntfy(titel, text, priority="default"):
    headers = {
        "Title": titel,
        "Priority": priority,
    }
    try:
        r = requests.post(
            f"{NTFY_SERVER}/{NTFY_TOPIC}",
            data=text.encode("utf-8"),
            headers=headers,
            timeout=10
        )
        if r.status_code not in (200, 201):
            print(f"ntfy error: HTTP {r.status_code} – {r.text}")
    except Exception as e:
        print(f"ntfy send error: {e}")

# ────────────────────────────────────────────────
#                 Start the watcher
# ────────────────────────────────────────────────

print("20min watcher started\n")
print(f"Searching for: {', '.join(SUCHWOERTER)} (case-insensitive)")
print(f"ntfy notifications sent to topic: {NTFY_TOPIC}")
print(f"Server: {NTFY_SERVER}\n")

while True:
    found_in_cycle = False
    jetzt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:15]:  # only the 15 newest entries
                title_lower = entry.title.lower()
                link = entry.get("link", "Kein Link")

                # Case-insensitive match
                if any(w.lower() in title_lower for w in SUCHWOERTER) and link not in gesehen:
                    found_in_cycle = True

                    meldung = (
                        f"NEW ARTICLE on 20min!\n\n"
                        f"{entry.title.strip()}\n\n"
                        f"{link}\n\n"
                        f"({jetzt})"
                    )

                    print("\n" + "═" * 80)
                    print(meldung)
                    print("═" * 80 + "\n")

                    sende_ntfy(
                        "20min Alert: Helvetus / Stralium",
                        meldung,
                        priority="high"
                    )

                    gesehen.add(link)

        except Exception as e:
            print(f"Feed error on {feed_url}: {e}")

    # ────────────────────────────────────────────────
    # Send a status message when the cycle produced no match
    # ────────────────────────────────────────────────
    if not found_in_cycle:
        status_meldung = (
            f"Status check ({jetzt})\n\n"
            f"No new articles matching:\n"
            f"{', '.join(SUCHWOERTER)}"
        )

        sende_ntfy(
            "20min watcher: no matches",
            status_meldung,
            priority="low"
        )

        print("→ No matches – status message sent")

    time.sleep(INTERVAL)
