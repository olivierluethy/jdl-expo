"""
watch_msn_news_multi_query.py — watch several Bing News queries for MSN articles, matching headline and body.

Description:
    The most complete of the three MSN watchers and the one to prefer. It works
    like watch_msn_news_with_keywords.py — fetching each unseen article and
    matching a keyword list against the headline and the full body text — but
    sweeps six different Bing News searches per cycle instead of one, which
    widens coverage considerably since Bing surfaces different articles for
    different query terms. A failure on one query is reported and skipped without
    affecting the others. Matches are pushed to an ntfy topic, and seen headlines
    are persisted as indented, non-escaped JSON so the file stays readable.

Requirements:
    - Python 3.x
    - Packages: requests, beautifulsoup4
    - External services: bing.com, msn.com and ntfy.sh
    - Environment variables / credentials needed: none — the ntfy topic is
      hardcoded and acts as a shared secret, see SECURITY_NOTES.md

Inputs:
    The SEARCH_URLS, KEYWORDS and CHECK_INTERVAL constants in this file.
    rss/data/seen_articles.json — seen headlines, read if present

Outputs:
    rss/data/seen_articles.json — rewritten whenever a new match is found
    Push notifications to the configured ntfy topic; hits printed on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python rss/scrapers/watch_msn_news_multi_query.py

Notes:
    This script never terminates on its own — stop it with Ctrl-C. The file name
    has nothing to do with the Go programming language; the original name was
    golang.py and was simply misleading. Six queries multiply both the runtime
    and the request volume per cycle. Only matching headlines are remembered, so
    non-matching articles are re-downloaded every cycle. All three MSN watchers
    share the same seen-articles file, so running more than one at a time will
    have them overwrite each other's state.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os

# =========================
# CONFIGURATION
# =========================

NTFY_URL = "https://ntfy.sh/derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"
SEARCH_URLS = [
    "https://www.bing.com/news/search?q=site:msn.com+Firma&FORM=HDRSC6",
    "https://www.bing.com/news/search?q=site:msn.com+betrug&FORM=HDRSC6",
    "https://www.bing.com/news/search?q=site:msn.com+uhren&FORM=HDRSC6",
    "https://www.bing.com/news/search?q=site:msn.com+luzerner&FORM=HDRSC6",
    "https://www.bing.com/news/search?q=site:msn.com+helvetus&FORM=HDRSC6",
    "https://www.bing.com/news/search?q=site:msn.com+stralium&FORM=HDRSC6"
]
SEEN_FILE = "rss/data/seen_articles.json"
CHECK_INTERVAL = 300  # seconds

# 🔎 Keywords and phrases to match
KEYWORDS = [
    "helvetus",
    "betrug",
    "luzerner",
    "uhren-armbändern"
]

# =========================
# HELPER FUNCTIONS
# =========================

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)

def send_ntfy(title, link):
    try:
        requests.post(
            NTFY_URL,
            data=f"New MSN article:\n\n{title}\n{link}".encode("utf-8"),
            headers={
                "Title": "MSN article found",
                "Priority": "4",
                "User-Agent": "msn-parser/1.0"
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ ntfy error:", e)

def fetch_article_content(url):
    """Download the article and return its text."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("⚠️ Error loading the article:", e)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    paragraphs = soup.find_all("p")
    content = " ".join(p.get_text(strip=True) for p in paragraphs)
    return content.lower()

def matches_keywords(title, content):
    """Check whether any keyword appears in the headline or the article body."""
    title_lower = title.lower()
    for kw in KEYWORDS:
        kw_lower = kw.lower()
        if kw_lower in title_lower or kw_lower in content:
            return True
    return False

# =========================
# NEWS CHECK
# =========================

def check_news():
    global seen_titles

    for url in SEARCH_URLS:
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"⚠️ Bing error on {url}: {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.select("a.title")  # or possibly "a.news-card-title", depending on the Bing layout

        for a in articles:
            title = a.get_text(strip=True)
            link = a.get("href")

            if not title or not link:
                continue

            title_norm = title.lower()
            if title_norm in seen_titles:
                continue

            # Load the article body
            content = fetch_article_content(link)

            if matches_keywords(title, content):
                print(f"[MATCH] → {title}")
                seen_titles.add(title_norm)
                save_seen(seen_titles)
                send_ntfy(title, link)

# =========================
# START
# =========================

seen_titles = load_seen()
print("📰 MSN keyword watcher started...")

while True:
    check_news()
    time.sleep(CHECK_INTERVAL)
