# Project History — How the YouTube Pipeline Came About

> This is an English translation of [`project_history_de.md`](project_history_de.md),
> which is the original German text written by the repository owner and kept
> verbatim. It is an informal engineering journal, not a specification: it
> records what was tried, what failed and why the code looks the way it does.
> The translation follows the original closely and smooths the phrasing only
> where a literal rendering would be unclear. Where the original is ambiguous,
> the translation stays ambiguous rather than inventing a meaning.

## What this repository is for

This repository is the working base for the scripts used for **TuneVote**,
specifically for processing YouTube video data. The whole approach is built
around *avoiding* the YouTube Data API, whose quota limits made it impractical
and unreliable for this purpose.

## First attempt: scraping through the browser

The first attempt at collecting the data used
[YouTube AutoScript](https://github.com/BaskLash/youtube_autoscript), which
works by pulling data off the ordinary YouTube website through the browser
developer tools.

In fact, before any of the channels were collected systematically, an
[older version of youtube_autoscript](https://github.com/BaskLash/youtube_autoscript/blob/4cf17def58099f538881cb5a7e15d78db930b3ad/main.js)
had already been repurposed to scrape a large number of videos per YouTube
channel. That yielded 30–40k video songs.

What was still missing was the **artist**. TuneVote was meant to show artist
statistics as well as songs — if a particular song is voted for often, the home
page should surface the artist too, not just the track. But the artist had never
been captured as a separate entity, which in hindsight was a significant design
mistake.

## Recovering artists without re-scraping everything

Re-visiting every YouTube channel individually was not an option; the existing
material had to be reused. So the entire `youtube_video_cache` table was
exported, with the intention of having Python extract all the YouTube channels
from it. Doing that video by video would have taken an enormous amount of time.

The insight was this: per creator there are typically 30, 100, perhaps even 500
videos by that same creator. So the question became whether the video titles
share something that points back to the creator. A well-known pattern is
`Artist - Song Title`, or `Artist, Song Title`. There were enough of these
title conventions to build a consolidation on: keep as much music as possible
from a single creator out of the lookup, while guaranteeing at least one song
per creator remains.

That reduced the list from **29,364 rows down to a little over 9,000** — a
considerable shrinking of the insert list. From there, the goal was to determine
the channel creator for each remaining insert (that is, per video link), obtain
its channel ID, and then block redundancy on channel IDs so no creator could
appear twice. The result is a deduplicated set of all creators.

### Advantages of this approach

- A great many videos of a YouTube channel — particularly its most popular
  ones — can be pulled in very little time, and all the required data comes off
  the frontend quickly.

### Serious drawbacks

- For roughly 300 to 1,000 individual artists, each artist channel would have to
  be opened on YouTube by hand: go to the videos, sort by popularity, scroll far
  enough down (for a very popular artist, down to below a million views), and
  then capture everything in that range.
- Not all of an artist's videos get captured.
- The manual preparation needed just to run the script is absurd.

## Second attempt: Selenium

The next approach was to try Selenium, letting Python drive the browser and
perform those steps automatically.

That has drawbacks too:

- It burns a lot of resources that could be saved.
- As many steps as possible have to be thought through far in advance, which
  makes it a very laborious process to set up.
- It uses a great deal of RAM and CPU.

## Third attempt: yt-dlp

Then came `yt_dlp`, the most powerful Python library for this — thoroughly
reliable for scraping YouTube video channels.

Fetching the videos of a channel was extremely fast. But the video durations
were missing, and something else only became apparent at the end: when
everything was pulled from the `/videos` URL area, the **newest** videos on the
channel were never included — always the somewhat older ones — even though no
filter was restricting the extraction of the newest videos.

## The UC → UU trick

The decisive discovery, pointed out via ChatGPT, is that a channel ID can be
read out of a YouTube channel. The channel ID identifies the channel, and for a
music channel the URL is built like this:

```
https://www.youtube.com/channel/UC0C-w0YjGpqDXGB8IHb662A
```

The channel ID sits directly in the URL. The interesting part: take the ID —
`UC0C-w0YjGpqDXGB8IHb662A` — take its first two characters `UC`, and replace the
`C` with a `U`. That gives `UU`, and therefore
`UU0C-w0YjGpqDXGB8IHb662A`. Put that into a playlist link:

```
https://www.youtube.com/playlist?list=UU0C-w0YjGpqDXGB8IHb662A
```

and you land on a playlist page you could never reach from the artist's channel
page. What makes it special is that **all** of the artist's videos are there at
once. Scraping that page with `yt_dlp` returns exactly as many videos as the
playlist shows — everything really is fetched from that playlist page, and the
extraction is relatively quick.

The one problem is that durations are not handled along the way. To get them,
every single video has to be queried separately through the library so the
duration can be pulled out of its metadata.

Doing that separate query every time takes much, much longer, because the script
runs it once per extracted video from the artist's playlist. That is thoroughly
resource-damaging and simply took far too long.

## Fourth attempt: ytInitialData over HTTP

The next thing tried was fetching and evaluating the JSON object called
`ytInitialData` through separate HTTP requests using `httpx` and `asyncio`. The
argument for it was that this object supposedly contains a JSON from which all
the videos rendered in the frontend can be read. The description was that
YouTube loads this JSON for the frontend and builds the whole frontend from it.
That sounded odd — why do it that way rather than simply fetching from the
database?

The appeal was that Python can fire HTTP requests per artist very quickly, with
small instructions corresponding to button clicks for filtering, so as to get
the more popular videos and store fewer songs per artist while keeping the most
popular ones. That would be the fastest route, and it would also get to the
bottom of the duration problem, since the frontend always shows the duration on
the video — logically enough, so you know how long a video is before watching it.

But extracting, processing and preserving the content from that JSON turned out
to be impossible. At first the script could not issue correct requests at all,
because Google judged them as not coming from a human. One workaround that did
work was to open an incognito browser window, go to YouTube, copy the cookie
named `SOCS` out of the developer tools, and use it in the request handler — a
deception making it look like a real human was behind the request, on the
strength of that cookie's validity.

Then the next unforeseeable problem appeared. The JSON with all its contents
could never be fetched and processed properly: there was no known way to do it,
public write-ups and forums offered no usable starting point, and even the most
current approaches — from 2023–2024 — did not hold up, because YouTube's HTML
context appears to have changed heavily again. That seems to be exactly why it
was not possible to draw correct conclusions when harvesting data from this
JSON.

The stranger part became clear on looking into the JSON directly. Given how many
videos the channel loads, it looked about as expected — but searching for
concrete videos, for example the very first one, its title could not be found
anywhere, and neither could several others. That seemed indefensible, and so
this route was given less weight.

## Where it landed

What remained was to keep believing in `yt_dlp` and to speed it up by increasing
the number of threads. After settling on as many as **30 threads**, the script
pulled a genuinely large number of YouTube videos off a channel playlist very
fast. Watching it work made a deeply impressive impression.

---

## How this maps onto the code

The scripts in this repository are the sediment of the story above:

| Stage in the story | Where it lives now |
|---|---|
| The `UC` → `UU` discovery | `tunevote/scrapers/fetch_channel_id_from_url.py`, `resolve_channel_handle_to_uploads_playlist.py`, `print_uploads_playlist_for_channel*.py` |
| Doing that conversion in bulk | `tunevote/scrapers/resolve_channel_list_to_uploads_playlists.py`, `tunevote/processing/convert_channel_urls_to_playlist_urls.py` |
| The 29,364 → ~9,000 reduction by title pattern | `tunevote/processing/extract_unique_artists_from_dump.py` |
| Recovering the channel per video | `tunevote/scrapers/extract_channel_urls_from_video_ids.py` |
| The 30-thread export | `tunevote/scrapers/export_playlist_videos_to_sql.py` |
| The 10-thread, Shorts-proof export | `tunevote/scrapers/export_channel_list_videos_to_sql.py` |
| The missing-durations repair | `tunevote/processing/generate_duration_update_statements.py` |
| Artist images from Wikipedia | `tunevote/scrapers/generate_video_insert_statements.py` and both SQL exporters |

The Selenium and `ytInitialData` attempts left no code behind — they were
abandoned before producing anything that was kept.
