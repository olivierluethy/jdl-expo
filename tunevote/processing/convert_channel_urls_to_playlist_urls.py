INPUT_FILE = "tunevote/data/unique_channels.txt"
OUTPUT_FILE = "tunevote/data/unique_playlists.txt"

with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
     open(OUTPUT_FILE, "a", encoding="utf-8") as outfile:

    for line in infile:
        line = line.strip()
        if not line:
            continue

        # Erwartetes Format:
        # https://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxx
        if "/channel/" not in line:
            continue

        channel_id = line.split("/channel/")[-1]

        # UC -> UU
        if channel_id.startswith("UC"):
            playlist_id = "UU" + channel_id[2:]
        else:
            # Falls unerwartetes Format
            continue

        playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        outfile.write(playlist_url + "\n")
