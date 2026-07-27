# Migration Report

Reorganization of a flat, 48-file repository into a domain-structured one.

**Baseline:** commit `ca9d139` — *chore(repo): baseline snapshot before reorganization*
**Result:** commit `edbe4e8`

Every move and rename was performed with `git mv` and committed separately from
any content change, so `git log --follow` traces each file back through its
rename to its original history.

---

## 1. Summary

| | Count |
|---|---:|
| Files before (repository root) | **48** |
| Non-empty files before | **44** |
| Files moved or renamed | **42** |
| Files left in place | **2** (`.gitignore`, `requirements.txt`) |
| Empty files deleted | **4** |
| Non-empty files deleted | **0** |
| New documentation files authored | **9** |
| Files after | **53** |

The arithmetic: **48 − 4 + 9 = 53**.

Non-empty count is unchanged: **44 before, 44 after** (the 42 moved files plus
the 2 that stayed). Every one of those 44 appears exactly once in the mapping
table below.

`venv/` (1,412 files) is excluded throughout. It is a generated virtual
environment, is listed in `.gitignore`, and was never tracked by git.

---

## 2. Full mapping table

### tunevote/scrapers/ — 13 files

| Old path | New path |
|---|---|
| `get-channel.py` | `tunevote/scrapers/resolve_channel_handle_to_uploads_playlist.py` |
| `get-info-from-channel.py` | `tunevote/scrapers/fetch_channel_id_from_url.py` |
| `get-individual.py` | `tunevote/scrapers/print_uploads_playlist_for_channel.py` |
| `get-playlist.py` | `tunevote/scrapers/print_uploads_playlist_for_channel_uc8gxc2f.py` |
| `get-playlists.py` | `tunevote/scrapers/resolve_channel_list_to_uploads_playlists.py` |
| `get-channels.py` | `tunevote/scrapers/search_youtube_channels_by_artist_name.py` |
| `get-creators.py` | `tunevote/scrapers/extract_channel_urls_from_video_ids.py` |
| `get-videos.py` | `tunevote/scrapers/generate_video_insert_statements.py` |
| `youtube_artist_image_graber_wikipedia.py` | `tunevote/scrapers/generate_video_insert_statements_duplicate.py` |
| `get-videos-from-playlist.py` | `tunevote/scrapers/export_playlist_videos_to_sql.py` |
| `get-videos-from-channelList.py` | `tunevote/scrapers/export_channel_list_videos_to_sql.py` |
| `check_channels.py` | `tunevote/scrapers/check_channel_availability.py` |
| `get-genre.py` | `tunevote/scrapers/fetch_song_genre_musicbrainz.py` |

### tunevote/processing/ — 4 files

| Old path | New path |
|---|---|
| `youtube_duration_fixer.py` | `tunevote/processing/generate_duration_update_statements.py` |
| `check-duplikate-playlist.py` | `tunevote/processing/deduplicate_channel_list.py` |
| `illiterate-playlist-from-channels.py` | `tunevote/processing/convert_channel_urls_to_playlist_urls.py` |
| `insert-shorter.py` | `tunevote/processing/extract_unique_artists_from_dump.py` |

### tunevote/data/ and tunevote/frontend/ — 4 files

| Old path | New path |
|---|---|
| `unique_channels.txt` | `tunevote/data/unique_channels.txt` |
| `processed_channels.txt` | `tunevote/data/processed_channels.txt` |
| `processed_videos.txt` | `tunevote/data/processed_videos.txt` |
| `main.jsx` | `tunevote/frontend/session_page.jsx` |

### rss/ — 6 files

| Old path | New path |
|---|---|
| `20-scrapper.py` | `rss/scrapers/watch_swiss_news_rss_feeds.py` |
| `msn-parser.py` | `rss/scrapers/watch_msn_news_headlines.py` |
| `mika.py` | `rss/scrapers/watch_msn_news_with_keywords.py` |
| `golang.py` | `rss/scrapers/watch_msn_news_multi_query.py` |
| `sms-test.py` | `rss/notifications/send_test_notification_ntfy.py` |
| `seen_articles.json` | `rss/data/seen_articles.json` |

### cv/ — 8 files

| Old path | New path |
|---|---|
| `html_to_pdf.py` | `cv/scripts/convert_resume_html_to_pdf.py` |
| `olivier_luethy_cv_en.html` | `cv/templates/olivier_luethy_cv_en.html` |
| `resume_de.html` | `cv/templates/olivier_luethy_cv_de_2026-06-04.html` |
| `olivier_luethy_cv_de.html` | `cv/templates/olivier_luethy_cv_de_2026-07-13.html` |
| `Olivier Lüthy - CV - DE.pdf` | `cv/output/olivier_luethy_cv_de_2026-06-03.pdf` |
| `resume.pdf` | `cv/output/olivier_luethy_cv_2026-06-04.pdf` |
| `olivier_luethy_cv.pdf` | `cv/output/olivier_luethy_cv_2026-06-15.pdf` |
| `olivier_luethy_cv_de.pdf` | `cv/output/olivier_luethy_cv_de_2026-07-13.pdf` |

### database/ — 6 files

| Old path | New path |
|---|---|
| `readDB_schema.py` | `database/schema_inspection/export_mysql_schema_to_sql.py` |
| `sql.py` | `database/parsers/import_sql_dump_into_mysql.py` |
| `insert.sql` | `database/dumps/tunevote_artists_and_videos_insert.sql` |
| `gulp.sql` | `database/dumps/youtube_video_cache_insert.sql` |
| `kuh.sql` | `database/dumps/tunevote_phpmyadmin_full_dump.sql` |
| `struktur.sql` | `database/dumps/tunevote_schema_structure.sql` |

### docs/ — 1 file

| Old path | New path |
|---|---|
| `readme.md` | `docs/project_history_de.md` |

### Left in place — 2 files

| Path | What changed |
|---|---|
| `requirements.txt` | Rewritten: five missing packages added, comments explaining each |
| `.gitignore` | Extended with `.env`, `.env.*`, `.venv/`; comments translated to English |

**42 moved + 2 in place + 4 deleted = 48.**

---

## 3. Deleted files

Four files were deleted. **All four were exactly 0 bytes.** Each was verified
with `stat` immediately before removal, and each hashed to
`d41d8cd98f00b204e9800998ecf8427e` — the MD5 of the empty string, which is proof
of emptiness rather than merely of blank-looking content.

| File | Size | MD5 | Note |
|---|---:|---|---|
| `gangster.py` | 0 B | `d41d8cd9…` | Never written |
| `reddit_glimpsh.py` | 0 B | `d41d8cd9…` | Never written; the name suggests an intended Reddit scraper |
| `top_songs_with_duration.txt` | 0 B | `d41d8cd9…` | Never written |
| `unique_inserts.txt` | 0 B | `d41d8cd9…` | Never written |

**No file with any content was deleted.** Files with only comments, only a
docstring, only imports or a single line of code were all kept, as were both
halves of every duplicate pair.

All four remain recoverable from git history at `ca9d139`.

---

## 4. Files placed in `_unsorted/`

**None.** `_unsorted/` was never created, because all 48 files could be
classified confidently after reading them. The two cases that were genuinely
ambiguous were resolved by asking rather than by parking:

| File | Ambiguity | Resolution |
|---|---|---|
| `main.jsx` | React application source, not a data script, and the repository has no `package.json` or build setup | Placed in `tunevote/frontend/` — it is TuneVote code and drives YouTube playback |
| `get-genre.py` | Queries MusicBrainz, not YouTube | Placed in `tunevote/scrapers/` — it belongs to the same music-metadata effort; noted in its header that it targets a different service |

`data/` at the repository root was also not created: every data file belonged to
one of the four domains, so a domain-neutral folder would have stood empty.

---

## 5. Files whose purpose could not be determined

**None.** Every file's purpose was established by reading it. Two points are
worth flagging even though they are not unknowns:

- **`tunevote/scrapers/print_uploads_playlist_for_channel_uc8gxc2f.py`** — the
  purpose is clear, but nothing distinguishes it from
  `print_uploads_playlist_for_channel.py` except a hardcoded channel ID. Rather
  than invent a difference, the channel ID is in the file name and the header
  states the duplication outright.
- **`tunevote/scrapers/generate_video_insert_statements_duplicate.py`** — a
  byte-identical copy of `generate_video_insert_statements.py` (MD5
  `d6fe0dde0ec4a160ea38f71059e6763e`). Kept because the no-deletion rule takes
  precedence over deduplication; the name and header say plainly that it is a
  duplicate.

Two more redundancies were found and left intact:

- `database/dumps/youtube_video_cache_insert.sql` holds the same payload as the
  string literal embedded inside
  `tunevote/processing/extract_unique_artists_from_dump.py`.
- `cv/output/olivier_luethy_cv_de_2026-06-03.pdf` and
  `cv/output/olivier_luethy_cv_2026-06-04.pdf` are both 325,466 bytes but are
  **not** identical files.

---

## 6. Content changes

### 6.1 Path references (commit `fa2dc35`)

Scripts are run from the repository root, so relative paths broke when files
moved. 25 path string literals were updated across 15 files. The diff is exactly
25 insertions and 25 deletions — every change is a one-for-one line replacement,
and no logic line was touched. All 25 Python scripts compile.

Two categories were repointed:

**Files that actually moved:**

| Old literal | New literal |
|---|---|
| `unique_channels.txt` | `tunevote/data/unique_channels.txt` |
| `processed_channels.txt` | `tunevote/data/processed_channels.txt` |
| `processed_videos.txt` | `tunevote/data/processed_videos.txt` |
| `seen_articles.json` | `rss/data/seen_articles.json` |
| `insert.sql` | `database/dumps/tunevote_artists_and_videos_insert.sql` |
| `struktur.sql` | `database/dumps/tunevote_schema_structure.sql` |

**Sibling files that were never in the repository** but are read or written
alongside the ones above. These were repointed to the matching `data/` folder so
outputs land with their inputs instead of scattering into the repository root:
`unique_playlists.txt`, `available_channels.txt`, `dead_channels.txt`,
`artists.txt`, `artists_output.txt`, `artists_output(1).txt`,
`update_durations.txt`. This is a judgment call and is flagged here explicitly —
it changes where those files appear, though not what any script does.

One path is resolved script-relative rather than against the working directory:
`generate_duration_update_statements.py` builds its output path from
`os.path.dirname(__file__)`, so its literal became `../data/update_durations.txt`
to keep that mechanism intact.

### 6.2 Documentation (commit `a99a990`)

- A standard header was added to all **26** source files (25 Python scripts and
  `session_page.jsx`), inserted after any shebang and encoding declaration so
  both keep working.
- **337 + 24 = 361** German comments, docstrings and console messages were
  translated to English.
- `cv/scripts/convert_resume_html_to_pdf.py` already had a module docstring. It
  was replaced by the standard header, with its "Why Playwright/Chromium?"
  rationale folded into the Notes section rather than dropped.

No logic was changed anywhere. All 25 Python scripts compile after the edits.

### 6.3 Deliberately *not* translated

| Location | Text | Why |
|---|---|---|
| `rss/scrapers/watch_msn_news_*.py` | Keywords `betrug`, `luzerner`, `uhren-armbändern`, `helvetus` | Search terms, i.e. data. Translating them would stop the watchers matching. |
| `rss/scrapers/watch_swiss_news_rss_feeds.py` | `SUCHWOERTER` list | Same reason. |
| `tunevote/frontend/session_page.jsx` | German UI strings and `alert()` text | User-facing application content. Translating them would change the app's interface language. Only the file's **comments** were translated. |
| `database/schema_inspection/export_mysql_schema_to_sql.py` line 65 | `f.write(f"-- Struktur für Tabelle …")` | This string becomes a comment in the *generated* `.sql` output. Translating it would make regenerated files differ byte-for-byte from the committed dump. |
| `docs/project_history_de.md` | The whole document | Kept verbatim as the original record. The English version is a separate file. |

---

## 7. New files authored

Nine files, none of which replaces or removes anything:

| File | Purpose |
|---|---|
| `README.md` | Central overview, folder map, full script index, per-OS setup, data policy, security warning |
| `INVENTORY.md` | Pre-migration inventory: every file with size, extension and a content-based classification |
| `MIGRATION_REPORT.md` | This document |
| `SECURITY_NOTES.md` | Every hardcoded credential by file and line, no values reproduced |
| `tunevote/README.md` | Domain README with the pipeline diagram |
| `rss/README.md` | Domain README |
| `cv/README.md` | Domain README |
| `database/README.md` | Domain README |
| `docs/project_history_en.md` | English translation of the German journal |

---

## 8. Credentials

Reported, never changed. See [`SECURITY_NOTES.md`](SECURITY_NOTES.md) for the
full listing with line numbers.

- `database/schema_inspection/export_mysql_schema_to_sql.py` — MySQL host, user,
  password and database, plus a **commented-out remote host and password** that
  remain in plain text.
- `database/parsers/import_sql_dump_into_mysql.py` — MySQL host, user, password
  and database.
- Five files under `rss/` — a shared ntfy topic, which functions as a bearer
  secret on the public ntfy.sh server.

`.gitignore` gained `.env`, `.env.*` and `.venv/`. **No tracked file is covered
by the new `.gitignore`** — verified with `git ls-files | git check-ignore --stdin`,
which returned nothing.

---

## 9. Pre-existing working-tree state

The working tree was not clean at the start. Rather than proceed over it, the
state was captured as the baseline commit `ca9d139` after confirming with the
repository owner:

- **44 files** had permission-mode changes only (`100644 → 100755`), no content
  change.
- **`readDB_schema.py`** had an uncommitted edit switching the target database
  from a remote host to `127.0.0.1`/`easycontactforms`, with the old host and
  password commented out. Preserved exactly as found.
- **`struktur.sql`** had been **deleted from disk** but was still present in
  `HEAD`. On the owner's instruction it was restored with `git checkout` before
  the baseline commit, and then migrated normally to
  `database/dumps/tunevote_schema_structure.sql`. Without this, 339 lines of
  schema covering all 20 TuneVote tables would have been lost.
- Two untracked files (`olivier_luethy_cv_de.html`, `olivier_luethy_cv_de.pdf`)
  were added to the baseline and migrated normally.

A repository-local git identity was configured (`git config user.email`, not
`--global`) because none was set and no commit was possible without one.

---

## 10. Final verification

| Check | Result |
|---|---|
| Non-empty files before == after | **44 == 44** ✅ |
| Every original file appears exactly once in the mapping | **48/48** ✅ |
| Files deleted that were not empty | **0** ✅ |
| All moves recorded as pure renames | **42/42 at `R100`** ✅ |
| Data, dump and output files byte-identical after moving | **15/15** ✅ |
| Python scripts compile after all edits | **25/25** ✅ |
| Tracked files newly covered by `.gitignore` | **0** ✅ |
| German comments remaining in source | **0** ✅ |

The rename check was run against commit `295b5d6` — the end of the move
sequence, before any content was edited — where `git diff --name-status -M100%`
reports every single change as `R100`, meaning identical content under a new
path. Later commits add headers, which lowers git's similarity score, so
rename detection against `HEAD` alone understates what happened; the commit-by-commit
history is the accurate record.

Byte-identity of the 15 data files was verified by comparing
`git show ca9d139:<old path>` against the MD5 of each file at its new location.

Total data preserved across `tunevote/data`, `database/dumps`, `cv/output`,
`cv/templates` and `rss/data`: **48 MB**.
