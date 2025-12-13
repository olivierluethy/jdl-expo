import musicbrainzngs

musicbrainzngs.set_useragent("GenreDetectorApp", "1.0")

# Beispiel: Songtitel + Artist als Suchtext
query = "Rick Astley Never Gonna Give You Up"

result = musicbrainzngs.search_recordings(query=query, limit=1)

if result['recording-list']:
    rec = result['recording-list'][0]
    print("Recording:", rec["title"])
    print("Artist:", rec["artist-credit"][0]["artist"]["name"])
    print("Tags (Genres):", rec.get("tag-list", "Keine Tags"))
else:
    print("Keine Treffer bei MusicBrainz.")