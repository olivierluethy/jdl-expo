# JDL Expo

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A collection of Python tooling that grew around three unrelated jobs. The bulk
of it is the **TuneVote** data pipeline: scripts that scrape YouTube channel and
video metadata with `yt-dlp`, enrich it with artist images from Wikipedia, and
turn it into SQL that feeds a MySQL database. Alongside that sit a set of
long-running **news watchers** that poll Swiss RSS feeds and Bing/MSN for a few
keywords and push alerts via ntfy, and a small **CV toolchain** that renders an
HTML resume to a pixel-perfect PDF through headless Chromium. The three share
nothing but a Python environment.

If you want to understand *why* the YouTube code looks the way it does — why the
YouTube Data API is avoided, what the `UC` → `UU` playlist trick is, and which
approaches were tried and abandoned — read
[`docs/project_history_en.md`](docs/project_history_en.md).

> ⚠️ **This repository contains hardcoded database credentials and notification
> secrets in plain text.** They were left exactly as they were found. Read
> [`SECURITY_NOTES.md`](SECURITY_NOTES.md) before sharing this repository or
> running anything under `database/`.

---

## Folder map

```
.
├── README.md                  # this file
├── INVENTORY.md               # what every file was, before the reorganization
├── MIGRATION_REPORT.md        # what moved where, and why
├── SECURITY_NOTES.md          # every hardcoded credential, by file and line
├── requirements.txt           # dependencies, derived from actual imports
│
├── tunevote/                  # everything YouTube-related
│   ├── scrapers/              # fetching channel and video data from YouTube
│   ├── processing/            # transforming and enriching what was scraped
│   ├── data/                  # channel lists and resume logs — outputs, keep
│   └── frontend/              # the React session page (app source, not a script)
│
├── rss/                       # all non-YouTube scraping
│   ├── scrapers/              # RSS and Bing/MSN news watchers
│   ├── notifications/         # ntfy connectivity check
│   └── data/                  # seen-article state — output, keep
│
├── cv/                        # resume tooling
│   ├── scripts/               # HTML → PDF converter
│   ├── templates/             # HTML sources of the CV
│   └── output/                # rendered PDFs — outputs, keep
│
├── database/                  # MySQL tooling and dumps
│   ├── schema_inspection/     # read a live schema off a server
│   ├── connections/           # shared connection helpers (currently empty)
│   ├── parsers/               # import a dump into MySQL
│   └── dumps/                 # .sql exports — data, keep
│
├── docs/                      # project history, German original + translation
└── venv/                      # local virtual environment (git-ignored)
```

Each of `tunevote/`, `rss/`, `cv/` and `database/` has its own README with more
detail than the index below.

---

## File index

Every script in the repository. **Run all of them from the repository root** —
the paths inside them are relative to it.

### tunevote/scrapers/ — fetching data from YouTube

| Script | Purpose | How to run |
|---|---|---|
| `search_youtube_channels_by_artist_name.py` | Resolve artist names or URLs to YouTube channel URLs | `python tunevote/scrapers/search_youtube_channels_by_artist_name.py` |
| `resolve_channel_list_to_uploads_playlists.py` | Batch-convert the channel list to uploads playlists; resumable | `python tunevote/scrapers/resolve_channel_list_to_uploads_playlists.py` |
| `resolve_channel_handle_to_uploads_playlist.py` | One `@handle` → channel ID and uploads playlist | `python tunevote/scrapers/resolve_channel_handle_to_uploads_playlist.py` |
| `fetch_channel_id_from_url.py` | Print the channel ID for one channel URL | `python tunevote/scrapers/fetch_channel_id_from_url.py` |
| `print_uploads_playlist_for_channel.py` | One channel URL → uploads playlist URL | `python tunevote/scrapers/print_uploads_playlist_for_channel.py` |
| `print_uploads_playlist_for_channel_uc8gxc2f.py` | Same logic, different hardcoded channel | `python tunevote/scrapers/print_uploads_playlist_for_channel_uc8gxc2f.py` |
| `extract_channel_urls_from_video_ids.py` | Work backwards from video IDs to their channels | `python tunevote/scrapers/extract_channel_urls_from_video_ids.py` |
| `export_channel_list_videos_to_sql.py` | Every video of every listed channel → one SQL file | `python tunevote/scrapers/export_channel_list_videos_to_sql.py` |
| `export_playlist_videos_to_sql.py` | One playlist → one SQL file, 30 threads | `python tunevote/scrapers/export_playlist_videos_to_sql.py` |
| `generate_video_insert_statements.py` | Playlist → SQL INSERTs on stdout, with Wikipedia images | `python tunevote/scrapers/generate_video_insert_statements.py > out.sql` |
| `generate_video_insert_statements_duplicate.py` | Byte-identical copy of the above | `python tunevote/scrapers/generate_video_insert_statements_duplicate.py > out.sql` |
| `check_channel_availability.py` | Split the channel list into reachable and dead | `python tunevote/scrapers/check_channel_availability.py` |
| `fetch_song_genre_musicbrainz.py` | Genre tags from MusicBrainz | `python tunevote/scrapers/fetch_song_genre_musicbrainz.py` |

### tunevote/processing/ — transforming what was scraped

| Script | Purpose | How to run |
|---|---|---|
| `extract_unique_artists_from_dump.py` | Reduce a video dump to one row per artist | `python tunevote/processing/extract_unique_artists_from_dump.py` |
| `generate_duration_update_statements.py` | Build SQL UPDATEs that backfill missing durations | `python tunevote/processing/generate_duration_update_statements.py` |
| `deduplicate_channel_list.py` | Remove duplicate URLs from the channel list, in place | `python tunevote/processing/deduplicate_channel_list.py` |
| `convert_channel_urls_to_playlist_urls.py` | Offline `UC` → `UU` conversion, no network | `python tunevote/processing/convert_channel_urls_to_playlist_urls.py` |

### tunevote/frontend/

| File | Purpose | How to run |
|---|---|---|
| `session_page.jsx` | React component for a live TuneVote listening session | Not runnable from this repository — no build setup exists here |

### rss/scrapers/ and rss/notifications/

| Script | Purpose | How to run |
|---|---|---|
| `watch_swiss_news_rss_feeds.py` | Poll ~40 Swiss news RSS feeds, alert on keyword hits | `python rss/scrapers/watch_swiss_news_rss_feeds.py` |
| `watch_msn_news_multi_query.py` | Six Bing/MSN searches, match headline and body | `python rss/scrapers/watch_msn_news_multi_query.py` |
| `watch_msn_news_with_keywords.py` | One Bing/MSN search, match headline and body | `python rss/scrapers/watch_msn_news_with_keywords.py` |
| `watch_msn_news_headlines.py` | One Bing/MSN search, match headline only | `python rss/scrapers/watch_msn_news_headlines.py` |
| `send_test_notification_ntfy.py` | Send one test push to verify the ntfy topic | `python rss/notifications/send_test_notification_ntfy.py` |

The four watchers run forever; stop them with Ctrl-C. The three MSN watchers
share one state file — run only one at a time.

### cv/scripts/

| Script | Purpose | How to run |
|---|---|---|
| `convert_resume_html_to_pdf.py` | Render an HTML resume to PDF via headless Chromium | `python cv/scripts/convert_resume_html_to_pdf.py cv/templates/olivier_luethy_cv_en.html -o cv/output/cv_en.pdf` |

The only script here with a real CLI. Needs `playwright install chromium` in
addition to `pip install`.

### database/

| Script | Purpose | How to run |
|---|---|---|
| `schema_inspection/export_mysql_schema_to_sql.py` | Dump every `CREATE TABLE` to a .sql file | `python database/schema_inspection/export_mysql_schema_to_sql.py` |
| `parsers/import_sql_dump_into_mysql.py` | Execute a large dump against MySQL | `python database/parsers/import_sql_dump_into_mysql.py` |

Both contain hardcoded credentials — see [`SECURITY_NOTES.md`](SECURITY_NOTES.md).

---

## Setup

Written out separately and completely per platform. Pick your own.

### Ubuntu / Linux

Ubuntu does not ship `venv` or `pip` with the base Python package, so install
those first:

```bash
# 1. Check the Python version (3.8 or newer; this repo was used with 3.12)
python3 --version

# 2. Install the prerequisites
sudo apt update
sudo apt install python3-venv python3-pip

# 3. Create the virtual environment in the repository root
cd /path/to/jdl-expo
python3 -m venv .venv

# 4. Activate it — the prompt gains a (.venv) prefix
source .venv/bin/activate

# 5. Install the dependencies
pip install -r requirements.txt

# 5b. Only if you need the CV converter — downloads the browser itself
playwright install chromium

# 6. Run a script from the repository root
python tunevote/scrapers/check_channel_availability.py

# 7. Leave the environment when you are done
deactivate
```

### macOS

```bash
# 1. Check the Python version. macOS ships an old Python; if it is missing or
#    below 3.8, install a current one with Homebrew:
python3 --version
brew install python

# 2. Create the virtual environment in the repository root
cd /path/to/jdl-expo
python3 -m venv .venv

# 3. Activate it — the prompt gains a (.venv) prefix
source .venv/bin/activate

# 4. Install the dependencies
pip install -r requirements.txt

# 4b. Only if you need the CV converter
playwright install chromium

# 5. Run a script from the repository root
python tunevote/scrapers/check_channel_availability.py

# 6. Leave the environment when you are done
deactivate
```

### Windows — PowerShell

```powershell
# 1. Check the Python version. If this fails, install Python from python.org
#    or the Microsoft Store and tick "Add Python to PATH".
python --version

# 2. Create the virtual environment in the repository root
cd C:\path\to\jdl-expo
python -m venv .venv

# 3. Activate it — the prompt gains a (.venv) prefix
.\.venv\Scripts\Activate.ps1

# If that is blocked with "running scripts is disabled on this system",
# allow signed local scripts for your user once, then activate again:
#     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Install the dependencies
pip install -r requirements.txt

# 4b. Only if you need the CV converter
playwright install chromium

# 5. Run a script from the repository root
python tunevote\scrapers\check_channel_availability.py

# 6. Leave the environment when you are done
deactivate
```

### Windows — CMD

```bat
:: 1. Check the Python version
python --version

:: 2. Create the virtual environment in the repository root
cd C:\path\to\jdl-expo
python -m venv .venv

:: 3. Activate it — the prompt gains a (.venv) prefix
.venv\Scripts\activate.bat

:: 4. Install the dependencies
pip install -r requirements.txt

:: 4b. Only if you need the CV converter
playwright install chromium

:: 5. Run a script from the repository root
python tunevote\scrapers\check_channel_availability.py

:: 6. Leave the environment when you are done
deactivate
```

### A note on the existing `venv/`

There is already a `venv/` folder in this repository. It is git-ignored, holds
only Playwright and its dependencies, and was built for Python 3.12 on this
machine — so it is not portable and does not cover most of `requirements.txt`.
The instructions above deliberately create a fresh `.venv/` instead. Both names
are git-ignored.

---

## Requirements

`requirements.txt` was generated by reading the import statements of every
script, not by freezing an environment. Versions are left unpinned except where
the version could actually be verified.

| Package | Imported as | Used by |
|---|---|---|
| `yt-dlp` | `yt_dlp` | Every YouTube scraper and processor |
| `requests` | `requests` | Wikipedia lookups, ntfy pushes, the MSN watchers |
| `beautifulsoup4` | `bs4` | The three MSN watchers |
| `feedparser` | `feedparser` | The Swiss RSS watcher |
| `unidecode` | `unidecode` | Accent folding in the two SQL exporters |
| `tqdm` | `tqdm` | Progress bars in the two SQL exporters |
| `mysql-connector-python` | `mysql.connector` | Both `database/` scripts |
| `musicbrainzngs` | `musicbrainzngs` | The MusicBrainz genre lookup |
| `playwright==1.60.0` | `playwright` | The CV converter |

Only `playwright` is pinned; its version was read from the dist-info in the
existing `venv/`. The rest are bare names because no tested version could be
confirmed — pinning a guess would be worse than not pinning.

`playwright` additionally needs its browser downloaded after installation:

```bash
playwright install chromium
```

---

## Data folders

**Nothing in a `data/`, `dumps/` or `output/` folder is scratch. Do not delete
any of it.** These are the results of long scraping runs, live database exports
and finished document renders — several of them cannot be regenerated.

| Folder | Holds | Why it matters |
|---|---|---|
| `tunevote/data/` | Channel lists and resume logs | `processed_channels.txt` and `processed_videos.txt` are what let an interrupted scrape continue. Deleting them means re-doing hours of rate-limited lookups. |
| `rss/data/` | `seen_articles.json` | Deduplication state. Delete it and the watchers re-alert on articles already reported. |
| `database/dumps/` | Four `.sql` exports, ~48 MB total | Real exported data, including a dump with a `users` table. |
| `cv/output/` | Four rendered PDFs | Finished documents; regenerating an old one needs the exact source it was built from, which is not always recoverable. |

Some scripts also produce files that are **not** committed and that land in the
**current working directory** — the repository root, if you follow the
run-from-root convention: `unique_playlists.txt`, `available_channels.txt`,
`dead_channels.txt` and `artists_output.txt`. These paths were left as the
original author wrote them rather than redirected into `tunevote/data/`, so the
scripts behave exactly as before. Move the results yourself if you want them
filed under a domain folder.

`update_durations.txt` is the exception: that one script resolves its output
relative to its own location, so the file appears in `tunevote/processing/`
regardless of where you start it.

Two scripts expect inputs that are not in the repository and must be supplied
first, also in the working directory: `artists.txt` (for
`search_youtube_channels_by_artist_name.py`) and `artists_output(1).txt` (for
`extract_channel_urls_from_video_ids.py`, produced by
`extract_unique_artists_from_dump.py`).

Note that several scripts open their output with mode `w` and overwrite the
previous result without asking — the two SQL exporters and the schema dumper in
particular. Copy anything you want to keep before re-running them.

---

## Security warning

Some scripts contain **hardcoded hosts, usernames and passwords** for MySQL
databases, in plain text, committed to git history. One of them is the password
for a remote, publicly addressable server — and it remains in the file as a
commented-out line, which removes it from execution but not from the repository.
The news watchers likewise hardcode an ntfy topic, which on the public ntfy.sh
server acts as a bearer secret: anyone who knows it can read and post to it.

None of this was changed during the reorganization. Rewriting credentials into
environment variables would silently change which database a script connects to,
and a behaviour change made without testing is worse than a documented risk.

[`SECURITY_NOTES.md`](SECURITY_NOTES.md) lists every affected file with line
numbers and the kind of secret, without reproducing any value. Read it before
sharing this repository, publishing it, or running anything under `database/`.

`.gitignore` covers `.env`, `.env.*`, `.venv/`, `venv/` and `__pycache__/`, so a
local secrets file will not be committed by accident once there is somewhere to
put these values.

---

## Repository history

This repository was reorganized from a flat directory of 48 files with largely
meaningless names (`gangster.py`, `golang.py`, `kuh.sql`, `mika.py`,
`20-scrapper.py`). Three documents record that:

- [`INVENTORY.md`](INVENTORY.md) — what every file was, classified by reading it
- [`MIGRATION_REPORT.md`](MIGRATION_REPORT.md) — old path → new path for all 48
- [`docs/project_history_de.md`](docs/project_history_de.md) — the original
  German engineering journal, kept verbatim, with an English translation in
  [`docs/project_history_en.md`](docs/project_history_en.md)

## License

Released under the [MIT License](LICENSE) © 2026 Olivier Lüthy. You're free to use, modify and distribute this
software, including commercially, as long as the copyright notice and license are included.

## Author

Built by **Olivier Lüthy** — [GitHub](https://github.com/olivierluethy).
