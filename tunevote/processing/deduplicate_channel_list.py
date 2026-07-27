"""
deduplicate_channel_list.py — remove duplicate channel URLs from the channel list, in place.

Description:
    Housekeeping for the channel list, which grows by appending and therefore
    accumulates repeats. It reads every non-blank line of the file, counts how
    often each one occurs, and rebuilds the list keeping only the first
    occurrence of each URL. Insertion order is preserved by relying on the
    ordering guarantee of a dict. The file is then overwritten with the cleaned
    list and the number of removed duplicates and remaining unique entries is
    printed.

Requirements:
    - Python 3.x
    - Packages: none beyond the standard library
    - External services: none
    - Environment variables / credentials needed: none

Inputs:
    tunevote/data/unique_channels.txt — one channel URL per line

Outputs:
    tunevote/data/unique_channels.txt — overwritten in place with unique lines
    Two summary lines on stdout.

Usage:
    # from the repository root, with the virtual environment activated
    python tunevote/processing/deduplicate_channel_list.py

Notes:
    This rewrites its input file destructively and keeps no backup, so copy the
    file first if the original ordering or the duplicate count matters.
    Comparison is exact and case-sensitive: the same channel reachable through
    both an @handle URL and a /channel/UC… URL counts as two distinct entries.
"""

from collections import Counter

filename = "tunevote/data/unique_channels.txt"  # Adjust the file name if needed

# Read the file, dropping blank lines
with open(filename, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# Count how often each URL occurs
link_counts = Counter(lines)

# Work out how many entries will be removed
total_duplicates = sum(count - 1 for count in link_counts.values() if count > 1)

# Build the unique list; dict preserves insertion order
unique_lines = list(dict.fromkeys(lines))

# Overwrite the file with the cleaned content
with open(filename, "w", encoding="utf-8") as f:
    for line in unique_lines:
        f.write(line + "\n")

print(f"Duplicates removed: {total_duplicates}")
print(f"Unique entries remaining: {len(unique_lines)}")
