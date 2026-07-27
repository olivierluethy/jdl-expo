import yt_dlp
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================
# Dateinamen
# =============================
input_file = 'tunevote/data/unique_channels.txt'
available_file = 'tunevote/data/available_channels.txt'
dead_file = 'tunevote/data/dead_channels.txt'

# =============================
# Funktion zum Prüfen eines Channels
# =============================
def check_channel_availability(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url.strip(), download=False)
        if info and (info.get('title') or info.get('entries') is not None):
            return True  # Channel existiert
        return False     # Channel existiert nicht oder ungültig
    except Exception:
        return False

# =============================
# Eingabedatei prüfen
# =============================
if not os.path.exists(input_file):
    print(f"❌ Fehler: Die Datei '{input_file}' wurde nicht gefunden.")
    exit()

with open(input_file, 'r', encoding='utf-8') as f:
    channels = [line.strip() for line in f if line.strip() and not line.startswith('#')]

if not channels:
    print("⚠️ Keine Channels in der Datei gefunden.")
    exit()

# =============================
# Listen vorbereiten
# =============================
available = []
dead = []

print(f"{len(channels)} Channels gefunden – starte Prüfung mit 8 Threads...\n")

# =============================
# Prüfung mit ThreadPoolExecutor
# =============================
with ThreadPoolExecutor(max_workers=8) as executor:
    future_to_url = {executor.submit(check_channel_availability, url): url for url in channels}
    for i, future in enumerate(as_completed(future_to_url), 1):
        url = future_to_url[future]
        try:
            result = future.result()
            if result:
                available.append(url)
                status = "✅ Verfügbar"
            else:
                dead.append(url)
                status = "❌ Nicht verfügbar"
        except Exception as e:
            dead.append(url)
            status = f"❌ Fehler: {e}"

        print(f"[{i}/{len(channels)}] {url}")
        print(f" {status}")
        print("-" * 60)

# =============================
# Ergebnisse speichern (nur neue Dateien erstellen/überschreiben)
# =============================
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    # Verfügbare Channels – nur erstellen, wenn welche vorhanden sind
    if available:
        with open(available_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Verfügbare Channels – Prüfung am {timestamp} ===\n\n")
            f.write("\n".join(available) + "\n")
        print(f"✅ {len(available)} verfügbare Channels in '{available_file}' gespeichert.")
    else:
        # Falls keine verfügbaren, Datei optional löschen oder leer lassen
        if os.path.exists(available_file):
            os.remove(available_file)
        print("ℹ️ Keine verfügbaren Channels → Datei '{available_file}' nicht erstellt/gelöscht.")

    # Nicht verfügbare Channels – nur erstellen, wenn welche vorhanden sind
    if dead:
        with open(dead_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Nicht verfügbare Channels – Prüfung am {timestamp} ===\n\n")
            f.write("\n".join(dead) + "\n")
        print(f"❌ {len(dead)} tote Channels in '{dead_file}' gespeichert.")
    else:
        if os.path.exists(dead_file):
            os.remove(dead_file)
        print("ℹ️ Keine toten Channels → Datei '{dead_file}' nicht erstellt/gelöscht.")

except Exception as e:
    print(f"\n❌ Fehler beim Schreiben der Dateien: {e}")

# =============================
# Zusammenfassung
# =============================
print("\n" + "="*60)
print("Prüfung abgeschlossen!")
print(f"Gesamt: {len(channels)}")
print(f"✅ Verfügbar: {len(available)}")
print(f"❌ Nicht verfügbar: {len(dead)}")
print("="*60)