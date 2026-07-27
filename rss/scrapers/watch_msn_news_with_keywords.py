"""
watch_msn_news_with_keywords.py — watch Bing News for MSN articles, matching on headline and body.

Description:
    The second generation of the MSN watcher. It polls one Bing News search page
    restricted to msn.com every five minutes and, for each result it has not seen
    before, downloads the article itself and joins all its paragraph text into a
    single lowercase string. A configurable list of keywords is then matched
    against both the headline and that body text, so relevant articles are caught
    even when the headline gives nothing away. Matches are pushed to an ntfy topic
    and the headline is stored in a JSON file so it is reported only once.

Requirements:
    - Python 3.x
    - Packages: requests, beautifulsoup4
    - External services: bing.com, msn.com and ntfy.sh
    - Environment variables / credentials needed: none — the ntfy topic is
      hardcoded and acts as a shared secret, see SECURITY_NOTES.md

Inputs:
    The SEARCH_URL, KEYWORDS and CHECK_INTERVAL constants in this file.
    rss/data/seen_articles.json — seen headlines, read if present

Outputs:
    rss/data/seen_articles.json — rewritten whenever a new match is found
    Push notifications to the configured ntfy topic; hits printed on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python rss/scrapers/watch_msn_news_with_keywords.py

Notes:
    This script never terminates on its own — stop it with Ctrl-C. Fetching every
    unseen article makes each cycle considerably slower and more visible to the
    sites involved than the headline-only version. Only headlines that actually
    matched are remembered, so an article that is fetched but does not match is
    downloaded again on every subsequent cycle. The parser depends on Bing
    rendering results as <a class="title">, which breaks silently if that markup
    changes. All three MSN watchers share the same seen-articles file.
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
SEARCH_URL = "https://www.bing.com/news/search?q=site:msn.com+Firma&FORM=HDRSC6"
SEEN_FILE = "rss/data/seen_articles.json"
CHECK_INTERVAL = 300  # seconds

# 🔎 Keywords and phrases to match
KEYWORDS = [
    "helvetus",
    "betrug",
    "luzerner firma wehrt sich",
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

    try:
        r = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("⚠️ Bing error:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a.title")

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
