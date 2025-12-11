#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
#-- Imports ---
# Dieses Skript extrahiert die Channel-ID von YouTube-Kanälen anhand ihrer URLs.
# Es wird die Bibliothek yt_dlp verwendet, um die Kanalinformationen abzurufen.
# Benötigte Bibliothek: yt_dlp (installierbar via pip)
# pip install yt_dlp
#--- Kanal-ID extrahieren ---
# Das Ziel ist es, die Channel-ID von YouTube-Kanälen zu extrahieren, um so über einen kleineren Trick eine ganze Playlist der Videos eines Kanals zu erhalten. Die Channel-ID wird benötigt, um die Playlist-URL im Format "UU" zu erstellen (z.B. "UU" + Channel-ID).
# So lassen sich wirklich alle Videos von einem Kanal extrahieren, weil vorher mittels dem vorherigen Approach mit nur dem Kanalnamen, hat es zwar funktioniert, aber die neusten Videos wurden nicht immer alle erfasst. Mit der Channel-ID klappt es zuverlässig.

from yt_dlp import YoutubeDL

url = "https://www.youtube.com/@KSI"  # oder https://www.youtube.com/c/ChannelName

ydl_opts = {}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    channel_id = info.get("channel_id")
    print("Channel-ID:", channel_id)
