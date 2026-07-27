import requests
from bs4 import BeautifulSoup
import time
import json
import os

# =========================
# KONFIGURATION
# =========================

NTFY_URL = "https://ntfy.sh/derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"
SEARCH_URL = "https://www.bing.com/news/search?q=site:msn.com+Firma&FORM=HDRSC6"
SEEN_FILE = "rss/data/seen_articles.json"
CHECK_INTERVAL = 300  # Sekunden

# 🔎 Schlagwörter / Phrasen
KEYWORDS = [
    "helvetus",
    "betrug",
    "luzerner firma wehrt sich",
    "uhren-armbändern"
]

# =========================
# HILFSFUNKTIONEN
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
            data=f"Neuer MSN-Artikel:\n\n{title}\n{link}".encode("utf-8"),
            headers={
                "Title": "MSN Artikel gefunden",
                "Priority": "4",
                "User-Agent": "msn-parser/1.0"
            },
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print("⚠️ ntfy Fehler:", e)

def fetch_article_content(url):
    """Lädt den Artikel und gibt den Text zurück."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("⚠️ Fehler beim Laden des Artikels:", e)
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    paragraphs = soup.find_all("p")
    content = " ".join(p.get_text(strip=True) for p in paragraphs)
    return content.lower()

def matches_keywords(title, content):
    """Prüft, ob eines der Keywords im Titel oder im Artikeltext vorkommt."""
    title_lower = title.lower()
    for kw in KEYWORDS:
        kw_lower = kw.lower()
        if kw_lower in title_lower or kw_lower in content:
            return True
    return False

# =========================
# NEWS-CHECK
# =========================

def check_news():
    global seen_titles

    try:
        r = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        print("⚠️ Bing Fehler:", e)
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

        # Artikelinhalt laden
        content = fetch_article_content(link)

        if matches_keywords(title, content):
            print(f"[TREFFER] → {title}")
            seen_titles.add(title_norm)
            save_seen(seen_titles)
            send_ntfy(title, link)

# =========================
# START
# =========================

seen_titles = load_seen()
print("📰 MSN Keyword Watcher gestartet...")

while True:
    check_news()
    time.sleep(CHECK_INTERVAL)
