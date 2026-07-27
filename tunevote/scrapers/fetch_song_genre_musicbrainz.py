"""
fetch_song_genre_musicbrainz.py — look up a recording's artist and genre tags on MusicBrainz.

Description:
    A small standalone experiment in enriching the song catalogue with genre
    information from a source other than YouTube. It registers a user agent with
    the MusicBrainz client library, searches the recording database for a single
    hardcoded "artist + title" query string, and prints the title, the credited
    artist and the tag list of the first match. MusicBrainz tags are
    community-supplied, so they act as a rough genre signal rather than an
    authoritative classification.

Requirements:
    - Python 3.x
    - Packages: musicbrainzngs
    - External services: musicbrainz.org (no API key, but a user agent is required)
    - Environment variables / credentials needed: none

Inputs:
    The query variable inside this file. No command-line arguments are parsed.

Outputs:
    Three lines on stdout, or a "no match" message. No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/scrapers/fetch_song_genre_musicbrainz.py

Notes:
    This script targets MusicBrainz rather than YouTube, but it belongs to the
    same music-metadata effort and so lives with the other TuneVote scrapers.
    It is exploratory: nothing else in the repository consumes its output, and
    it is not wired into the SQL generation pipeline. MusicBrainz asks clients to
    stay under roughly one request per second, so add throttling before running
    it over a real catalogue. Many recordings carry no tags at all.
"""

import musicbrainzngs

musicbrainzngs.set_useragent("GenreDetectorApp", "1.0")

# Example search text: song title plus artist
query = "Rick Astley Never Gonna Give You Up"

result = musicbrainzngs.search_recordings(query=query, limit=1)

if result['recording-list']:
    rec = result['recording-list'][0]
    print("Recording:", rec["title"])
    print("Artist:", rec["artist-credit"][0]["artist"]["name"])
    print("Tags (Genres):", rec.get("tag-list", "No tags"))
else:
    print("No matches on MusicBrainz.")