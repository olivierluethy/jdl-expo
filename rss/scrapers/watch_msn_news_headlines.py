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
            data=f"Neuer MSN-Artikel:\n{title}\n{link}".encode("utf-8"),
            headers={
                "Title": "MSN Artikel gefunden",
                "Priority": "4",
                "User-Agent": "msn-parser/1.0"
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ ntfy Fehler:", e)

def check_news():
    global seen_titles

    try:
        r = requests.get(
            SEARCH_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ Bing Fehler:", e)
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
    time.sleep(300)  # alle 5 Minuten