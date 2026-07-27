# Repository Inventory

Snapshot taken before any reorganization, at commit `ca9d139`
(*chore(repo): baseline snapshot before reorganization*).

**Scope:** 48 files in the repository root. The `venv/` directory (1412 files) is a
generated Python virtual environment; it is listed in `.gitignore`, is not tracked by
git, and is therefore **not** part of this inventory and will not be moved.

**Classification method:** every text and code file was read in full (large data files
were sampled at head/tail plus structural greps). Classification reflects what the code
actually does, not what the file is named — the existing names are almost all
misleading.

---

## Summary

| Metric | Count |
|---|---|
| Files in repository root | 48 |
| Non-empty files | 44 |
| Empty files (0 bytes) | 4 |
| Python scripts | 27 |
| SQL files | 4 |
| Text data files | 6 |
| HTML files | 3 |
| PDF files | 4 |
| Other (JSON, JSX, Markdown, dotfile) | 4 |
| Total size on disk | ~55 MB |

---

## A. YouTube / TuneVote — data acquisition

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `get-channel.py` | 1 128 B | .py | Resolves one hardcoded `@handle` URL to its channel ID via yt-dlp, then derives and prints the uploads-playlist URL (`UC…` → `UU…`). |
| `get-info-from-channel.py` | 1 198 B | .py | Prints the channel ID for one hardcoded channel URL via yt-dlp. Carries a long German comment explaining the `UC`→`UU` uploads-playlist trick. |
| `get-individual.py` | 1 070 B | .py | Channel URL → uploads-playlist URL via yt-dlp, with a regex fallback that recovers the `UC…` ID from the URL itself. Hardcoded channel `UCkajFamD9odK1vtdXMhEUcg`. |
| `get-playlist.py` | 1 070 B | .py | **Logically identical to `get-individual.py`**; differs only in the hardcoded channel (`UC8gxc2fYnL1tHPOXHXyI6sQ`). |
| `get-playlists.py` | 3 261 B | .py | Batch version of the above: reads `unique_channels.txt`, resolves each to an uploads playlist with a 10-thread pool, appends to `unique_playlists.txt`, and tracks completed channels in `processed_channels.txt` so runs are resumable. Handles Ctrl-C by flushing results. |
| `get-channels.py` | 5 103 B | .py | Reads artist names *or* URLs from `artists.txt`, resolves each to a YouTube channel URL (`ytsearch1:<name> official artist channel` for names), deduplicates against `unique_channels.txt`, appends new ones. Also carries an unused browser-console JS snippet in a leading string literal that scrapes a "similar artists" list from a music site. |
| `get-creators.py` | 4 549 B | .py | Reads `artists_output(1).txt` (SQL-tuple-shaped text), regex-extracts video IDs, looks up each video's `channel_url` via yt-dlp, and appends newly seen channels to `unique_channels.txt`. Resumable via `processed_videos.txt`; rate-limits with randomized sleeps; rewrites the input file to drop processed rows. |
| `get-videos.py` | 5 616 B | .py | Walks hardcoded playlists, derives the artist from the uploader, fetches an artist image from the Wikipedia API, and prints `INSERT IGNORE` statements for `artists` and `youtube_video_cache` to **stdout**. |
| `youtube_artist_image_graber_wikipedia.py` | 5 616 B | .py | **Byte-identical duplicate of `get-videos.py`** (same MD5 `d6fe0dde…`). |
| `get-videos-from-playlist.py` | 11 877 B | .py | Three-phase pipeline for one hardcoded playlist: flat-collect video URLs, then fetch details + Wikipedia images across 30 threads, then write `insert.sql`. Filters Premium and sub-60-second videos; normalizes names with `unidecode`; also records `channel_id`. |
| `get-videos-from-channelList.py` | 8 611 B | .py | Same idea driven by `unique_channels.txt` instead of one playlist: converts each channel to its uploads playlist, collects videos, applies a stricter Shorts filter (`!is_short` plus a `/shorts/` URL check), caches Wikipedia lookups, shows tqdm progress, and writes `insert.sql`. |
| `check_channels.py` | 4 125 B | .py | Probes every URL in `unique_channels.txt` with yt-dlp across 8 threads and splits them into `available_channels.txt` / `dead_channels.txt`, each stamped with a run timestamp. |
| `get-genre.py` | 517 B | .py | MusicBrainz (not YouTube) lookup: searches one hardcoded recording and prints its title, artist and genre tags. A small standalone experiment. |

## B. YouTube / TuneVote — data processing

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `youtube_duration_fixer.py` | 2 700 B | .py | Backfill tool: regex-extracts video IDs from an inline string, fetches each duration via yt-dlp, and writes `UPDATE youtube_video_cache SET duration = …` statements to an auto-incremented `update_durations*.txt`. Documented (in German) as the fix for durations that were scraped empty when a music badge covered the runtime. |
| `check-duplikate-playlist.py` | 772 B | .py | Deduplicates `unique_channels.txt` **in place**, preserving order, and reports how many duplicates were dropped. |
| `illiterate-playlist-from-channels.py` | 791 B | .py | Pure string transform, no network: reads `unique_channels.txt`, rewrites each `/channel/UC…` URL to its `UU…` uploads-playlist URL, appends to `unique_playlists.txt`. |
| `insert-shorter.py` | 5 721 859 B | .py | ~90 lines of code preceded by a **5.7 MB SQL dump embedded in a string literal** (29 374 lines). Parses the dump's tuples with a verbose regex (no `eval`), infers the artist from the `Artist - Title` naming pattern (Unicode-normalized so en/em dashes match), keeps one row per artist, and writes `artists_output.txt` with automatic filename incrementing. This is the "29 364 rows down to ~9 000" reduction described in the old readme. |

## C. YouTube / TuneVote — data files (outputs, keep)

| File | Size | Lines | What it holds |
|---|---:|---:|---|
| `unique_channels.txt` | 19 892 B | 348 | Deduplicated YouTube channel URLs — the working input set for most scrapers. |
| `processed_channels.txt` | 70 737 B | 1 241 | Resume log: channels already converted to uploads playlists. |
| `processed_videos.txt` | 113 688 B | 9 463 | Resume log: video IDs already looked up by `get-creators.py`. |
| `top_songs_with_duration.txt` | **0 B** | 0 | **Empty.** |
| `unique_inserts.txt` | **0 B** | 0 | **Empty.** |

## D. Non-YouTube scraping (news / RSS watchers)

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `20-scrapper.py` | 6 861 B | .py | Polls ~40 Swiss news RSS feeds (20 Minuten, Blick, Luzerner Zeitung, NZZ, Tages-Anzeiger) every 240 s with `feedparser`, case-insensitively matches the titles of the 15 newest entries against `helvetus` / `stralium`, and pushes hits to an ntfy topic. Also sends a low-priority "no hits" heartbeat each cycle. |
| `msn-parser.py` | 1 832 B | .py | Scrapes one Bing News result page (`site:msn.com`) with BeautifulSoup every 300 s, matches `betrug` in the headline, notifies via ntfy, and persists seen headlines in `seen_articles.json`. |
| `mika.py` | 3 307 B | .py | Evolution of `msn-parser.py`: one search URL, a configurable `KEYWORDS` list, and it now **downloads each article body** and matches keywords against the full text as well as the title. |
| `golang.py` | 3 855 B | .py | Most complete version of the same watcher: **six** Bing search URLs, keyword list, full-article matching, pretty-printed seen-file. Nothing whatsoever to do with the Go language. |
| `sms-test.py` | 918 B | .py | One-shot connectivity check that posts a timestamped test message to the ntfy topic used by all watchers above and prints the HTTP status. Sends no SMS. |
| `seen_articles.json` | 145 B | .json | Deduplication state for the MSN watchers: two seen headlines. |
| `reddit_glimpsh.py` | **0 B** | .py | **Empty.** |

## E. CV / resume tooling

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `html_to_pdf.py` | 9 626 B | .py | The only already-documented script in the repo. Renders an HTML file to PDF through Playwright/Chromium: waits for network idle and font readiness, injects print-fidelity CSS (exact colour adjust, animations frozen), reads `@page` margins out of the stylesheet, and prints A4 at 2× device scale. Full argparse CLI (`--output`, `--scale`, `--no-background`, `--timeout`). |
| `olivier_luethy_cv_en.html` | 56 635 B | .html | CV source, `<html lang="en">`. |
| `resume_de.html` | 56 691 B | .html | CV source, `<html lang="de">`. |
| `olivier_luethy_cv_de.html` | 57 948 B | .html | CV source, `<html lang="de">`, the largest and newest German variant. |
| `Olivier Lüthy - CV - DE.pdf` | 325 466 B | .pdf | Rendered CV, created 2026-06-03. Name contains spaces and a non-ASCII character. |
| `resume.pdf` | 325 466 B | .pdf | Rendered CV, created 2026-06-04. Same byte size as the file above but **not** identical. |
| `olivier_luethy_cv.pdf` | 323 263 B | .pdf | Rendered CV, created 2026-06-15. |
| `olivier_luethy_cv_de.pdf` | 359 074 B | .pdf | Rendered CV, created 2026-07-13 — the newest output. |

## F. Database

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `readDB_schema.py` | 783 B | .py | Connects to MySQL, runs `SHOW TABLES`, then `SHOW CREATE TABLE` for each, and writes the result to `struktur.sql`. Currently pointed at `127.0.0.1` / `easycontactforms`; the previous remote host and its password remain in the file as comments. Contains hardcoded credentials. |
| `sql.py` | 538 B | .py | Streams `insert.sql` line by line, skipping comments and blanks, accumulating text until a line ends in `;`, and executing each statement against MySQL with autocommit on. Contains hardcoded credentials. |
| `insert.sql` | 42 427 270 B | .sql | 113 296 lines. Generated by the scrapers: `START TRANSACTION`, `INSERT IGNORE` into `artists` and `youtube_video_cache`, `COMMIT`. |
| `gulp.sql` | 5 719 301 B | .sql | 29 363 lines. A single bare `INSERT INTO youtube_video_cache … VALUES` dump — the same payload embedded inside `insert-shorter.py`. |
| `kuh.sql` | 300 180 B | .sql | 2 043 lines. A proper phpMyAdmin dump (schema + data) of an early TuneVote database: `users`, `sessions`, `queue_items`, `session_participants`, `playback_sync`, `guest_users`, `youtube_video_cache`, `session_recommendations*`. |
| `struktur.sql` | 16 196 B | .sql | 339 lines. Schema-only output of `readDB_schema.py`: 20 `CREATE TABLE` statements covering the full TuneVote model (`artists`, `badges`, `votes`, `voting_rounds`, `shouts`, `knex_migrations`, …). |

## G. Frontend

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `main.jsx` | 44 930 B | .jsx | A single large React component (`SessionPage`) for the TuneVote web app: react-router params, an axios client against `https://api.tunevote.com`, a socket.io realtime connection, a QR code for joining, YouTube player controls, a voting queue, pause handling and AI song suggestions. It is application source, not a data script, and the repository contains no JS build setup, `package.json` or other frontend files. |

## H. Project meta

| File | Size | Ext | What it actually does |
|---|---:|---|---|
| `readme.md` | 11 293 B | .md | German-language engineering journal, not installation docs. Records why the YouTube Data API was abandoned, the browser-DevTools scraping phase, the artist-extraction insight, the Selenium detour, the move to yt-dlp, and the `UC`→`UU` uploads-playlist discovery. Contains genuine project history that exists nowhere else. Its setup section hardcodes a `/home/random_user/…` path. |
| `requirements.txt` | 30 B | .txt | Four bare names: `tqdm`, `yt-dlp`, `requests`, `unidecode`. Missing `mysql-connector-python`, `beautifulsoup4`, `feedparser`, `playwright`, `musicbrainzngs`. No trailing newline. |
| `.gitignore` | 171 B | — | German comments. Ignores `venv/`, `__pycache__/`, `*.pyc`, `.vscode/`, `.idea/`, `*.swp`, `.DS_Store`. Does **not** ignore `.env` or `.venv/`. |

---

## Empty files (0 bytes)

These four are the only files that qualify for deletion under the "empty files" rule.
All four are genuinely 0 bytes, not merely blank-looking — MD5 `d41d8cd98f00b204e9800998ecf8427e`,
the hash of the empty string.

| File | Size | Note |
|---|---:|---|
| `gangster.py` | 0 B | Never written. |
| `reddit_glimpsh.py` | 0 B | Never written. Name suggests an intended Reddit scraper. |
| `top_songs_with_duration.txt` | 0 B | Never written. |
| `unique_inserts.txt` | 0 B | Never written. |

## Duplicate content

| Files | Relationship |
|---|---|
| `get-videos.py` ⇄ `youtube_artist_image_graber_wikipedia.py` | Byte-identical (MD5 `d6fe0dde0ec4a160ea38f71059e6763e`). Both are non-empty, so **both are kept** — the no-deletion rule takes precedence over deduplication. |
| `get-individual.py` ⇄ `get-playlist.py` | Not byte-identical, but logically identical: same code, different hardcoded channel ID. Both kept. |
| `gulp.sql` ⇄ the string literal inside `insert-shorter.py` | The same `youtube_video_cache` dump, stored twice. Both kept. |

## Credentials found (values deliberately not reproduced here)

| File | Line | Type |
|---|---:|---|
| `readDB_schema.py` | 7, 9, 11, 13 | MySQL host, user, password, database |
| `readDB_schema.py` | 6, 10, 12 | Commented-out remote MySQL host, password and database |
| `sql.py` | 4, 6, 7, 8 | MySQL host, user, password, database |
| `20-scrapper.py` | 11 | ntfy topic (acts as a shared secret) |
| `msn-parser.py` | 7 | ntfy topic |
| `mika.py` | 11 | ntfy topic |
| `golang.py` | 11 | ntfy topic |
| `sms-test.py` | 4 | ntfy topic |

These are recorded here and in `SECURITY_NOTES.md`. They are **not** altered, moved to
environment variables, or removed, because that would change runtime behaviour.
