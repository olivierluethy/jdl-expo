"""
watch_msn_news_headlines.py — watch Bing News for MSN articles matching a headline keyword.

Description:
    The earliest and simplest of the three MSN watchers. Every five minutes it
    requests a single Bing News search page restricted to msn.com, parses the
    result list with BeautifulSoup, and looks at each result's headline. A
    headline containing the keyword that has not been seen before is pushed to an
    ntfy topic and recorded in a JSON file, so the alert is not repeated on the
    next cycle or after a restart. Both the Bing request and the ntfy push are
    wrapped in error handling, so a network failure skips the cycle rather than
    killing the watcher.

Requirements:
    - Python 3.x
    - Packages: requests, beautifulsoup4
    - External services: bing.com and ntfy.sh
    - Environment variables / credentials needed: none — the ntfy topic is
      hardcoded and acts as a shared secret, see SECURITY_NOTES.md

Inputs:
    The SEARCH_URL and NTFY_URL constants in this file.
    rss/data/seen_articles.json — seen headlines, read if present

Outputs:
    rss/data/seen_articles.json — rewritten whenever a new match is found
    Push notifications to the configured ntfy topic.

Usage:
    # from the repository root, with the virtual environment activated
    python rss/scrapers/watch_msn_news_headlines.py

Notes:
    This script never terminates on its own — stop it with Ctrl-C. It matches
    the headline only and never opens the article, so a relevant piece whose
    headline omits the keyword is missed; watch_msn_news_with_keywords.py in this
    folder adds full-text matching. The parser depends on Bing rendering results
    as <a class="title">, which is undocumented and breaks silently whenever Bing
    changes its markup — no results and no error is the symptom. All three MSN
    watchers share the same seen-articles file.
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import os

NTFY_URL = "https://ntfy.sh/derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"
SEARCH_URL = "https://www.bing.com/news/search?q=site:msn.com+Betrug+Luzerner+Firma+wehrt+sich&FORM=HDRSC6"

SEEN_FILE = "rss/data/seen_articles.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)

seen_titles = load_seen()

def send_ntfy(title, link):
    try:
        requests.post(
            NTFY_URL,
            data=f"New MSN article:\n{title}\n{link}".encode("utf-8"),
            headers={
                "Title": "MSN article found",
                "Priority": "4",
                "User-Agent": "msn-parser/1.0"
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ ntfy error:", e)

def check_news():
    global seen_titles

    try:
        r = requests.get(
            SEARCH_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ Bing error:", e)
        return

    soup = BeautifulSoup(r.text, "html.parser")
    articles = soup.select("a.title")

    for a in articles:
        title = a.get_text(strip=True)
        link = a.get("href")

        if not title or not link:
            continue

        if "betrug" in title.lower() and title not in seen_titles:
            seen_titles.add(title)
            save_seen(seen_titles)
            send_ntfy(title, link)


while True:
    check_news()
    time.sleep(300)  # every 5 minutes