from collections import Counter

# Datei einlesen
filename = "unique_playlists.txt"  # Passe den Dateinamen an
with open(filename, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

# Zähle, wie oft jeder Link vorkommt
link_counts = Counter(lines)

# Berechne die Gesamtanzahl der Duplikate
# (Jeder Link, der mehr als einmal vorkommt, zählt die "extra" Vorkommen)
total_duplicates = sum(count - 1 for count in link_counts.values() if count > 1)

print(f"Anzahl der Duplikate: {total_duplicates}")
