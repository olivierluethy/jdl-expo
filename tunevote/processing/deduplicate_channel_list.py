from collections import Counter

filename = "tunevote/data/unique_channels.txt"  # Passe den Dateinamen an

# Datei einlesen
with open(filename, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip()]

# Zähle Vorkommen
link_counts = Counter(lines)

# Anzahl der entfernten Duplikate berechnen
total_duplicates = sum(count - 1 for count in link_counts.values() if count > 1)

# Einmalige Inhalte erzeugen (Reihenfolge bleibt erhalten)
unique_lines = list(dict.fromkeys(lines))

# Datei mit bereinigtem Inhalt überschreiben
with open(filename, "w", encoding="utf-8") as f:
    for line in unique_lines:
        f.write(line + "\n")

print(f"Anzahl der entfernten Duplikate: {total_duplicates}")
print(f"Anzahl eindeutiger Einträge: {len(unique_lines)}")
