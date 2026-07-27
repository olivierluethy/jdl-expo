# tunevote/

Everything YouTube-related for the **TuneVote** project: the scripts that pull
video and channel data off YouTube, the scripts that transform that data into
SQL, the data files they produce, and the one frontend component that consumes
the result.

The whole pipeline deliberately avoids the YouTube Data API and works through
`yt-dlp` instead, because the API's quota limits made it impractical. The
central trick everything is built on is that a channel ID beginning with `UC`
becomes that channel's *uploads playlist* ID when the leading `UC` is replaced by
`UU` — and that playlist contains every public upload, which the `/videos` page
does not reliably show. See [`../docs/project_history_en.md`](../docs/project_history_en.md)
for how this was arrived at.

## Typical pipeline

```
artist names / URLs
        │
        ▼  scrapers/search_youtube_channels_by_artist_name.py
data/unique_channels.txt
        │
        ├─▶ processing/deduplicate_channel_list.py      (clean it up)
        ├─▶ scrapers/check_channel_availability.py      (drop dead channels)
        │
        ▼  scrapers/resolve_channel_list_to_uploads_playlists.py
unique_playlists.txt          (written to the working directory)
        │
        ▼  scrapers/export_channel_list_videos_to_sql.py
../database/dumps/tunevote_artists_and_videos_insert.sql
        │
        ▼  ../database/parsers/import_sql_dump_into_mysql.py
   MySQL: artists + youtube_video_cache
```

## scrapers/ — fetching data from YouTube

| Script | Purpose |
|---|---|
| `search_youtube_channels_by_artist_name.py` | Resolve artist names or URLs to channel URLs |
| `resolve_channel_list_to_uploads_playlists.py` | Batch-convert a channel list to uploads playlists, resumable |
| `resolve_channel_handle_to_uploads_playlist.py` | One `@handle` → channel ID + uploads playlist |
| `fetch_channel_id_from_url.py` | Print the channel ID for one channel URL |
| `print_uploads_playlist_for_channel.py` | One channel URL → uploads playlist URL |
| `print_uploads_playlist_for_channel_uc8gxc2f.py` | Same code, different hardcoded channel — see "Duplicates" below |
| `extract_channel_urls_from_video_ids.py` | Work backwards from video IDs to their channels |
| `export_channel_list_videos_to_sql.py` | Every video of every listed channel → one SQL file |
| `export_playlist_videos_to_sql.py` | One playlist → one SQL file, 30 threads |
| `generate_video_insert_statements.py` | Playlist → SQL INSERTs on stdout, with Wikipedia artist images |
| `generate_video_insert_statements_duplicate.py` | Byte-identical copy of the above — see "Duplicates" |
| `check_channel_availability.py` | Split the channel list into reachable and dead |
| `fetch_song_genre_musicbrainz.py` | Genre tags from MusicBrainz — the one non-YouTube script here |

## processing/ — transforming what was scraped

| Script | Purpose |
|---|---|
| `extract_unique_artists_from_dump.py` | Reduce a video dump to one row per artist (the 29,364 → ~9,000 step) |
| `generate_duration_update_statements.py` | Build SQL UPDATEs that backfill missing durations |
| `deduplicate_channel_list.py` | Remove duplicate URLs from the channel list, in place |
| `convert_channel_urls_to_playlist_urls.py` | Offline `UC` → `UU` conversion, no network needed |

## data/ — outputs, do not delete

| File | Contents |
|---|---|
| `unique_channels.txt` | 348 deduplicated channel URLs — the working input for most scrapers |
| `processed_channels.txt` | 1,241 channels already converted to uploads playlists (resume log) |
| `processed_videos.txt` | 9,463 video IDs already looked up (resume log) |

These are **results of long scraping runs**, not scratch files. The two resume
logs are what let an interrupted run continue instead of starting over; deleting
them means re-doing hours of work.

Only the three committed files above live in this folder. Several scripts also
produce uncommitted files, and those land in the **current working directory**
rather than here — the repository root, if you follow the run-from-root
convention: `unique_playlists.txt`, `available_channels.txt`,
`dead_channels.txt` and `artists_output.txt`. Those paths were deliberately left
as the original author wrote them, so the scripts behave exactly as they always
did; move the results into this folder yourself if you want them filed here.

`update_durations.txt` is the one exception: `generate_duration_update_statements.py`
resolves its output relative to its own file, so it appears in
`tunevote/processing/` no matter where you start it.

Two scripts expect an input that is **not** in the repository and must be
supplied first, also in the working directory: `artists.txt` (for
`search_youtube_channels_by_artist_name.py`) and `artists_output(1).txt` (for
`extract_channel_urls_from_video_ids.py`, which is produced by
`extract_unique_artists_from_dump.py`).

## frontend/

`session_page.jsx` is the React component for a live TuneVote listening session.
It is application source rather than a script: there is no `package.json` or
build setup in this repository, so it cannot be run from here. It lives under
`tunevote/` because it is TuneVote code and drives YouTube playback.

## Duplicates

Two pairs of files here contain the same logic:

- `generate_video_insert_statements.py` and
  `generate_video_insert_statements_duplicate.py` are **byte-identical**.
- `print_uploads_playlist_for_channel.py` and
  `print_uploads_playlist_for_channel_uc8gxc2f.py` differ only in the hardcoded
  channel ID, which is why that ID is in the second file's name.

Both duplicates were kept because the reorganization was not allowed to delete
any file that has content. Nothing depends on either copy, so removing them is
safe once you have confirmed they are still identical.

## Running

All paths inside these scripts are relative to the **repository root**, so run
them from there:

```bash
python tunevote/scrapers/export_channel_list_videos_to_sql.py
```

Most target URLs are hardcoded near the top of each file rather than passed as
arguments; edit the constant to point somewhere else.
