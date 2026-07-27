import requests
import datetime

NTFY_TOPIC = "derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"
URL = f"https://ntfy.sh/{NTFY_TOPIC}"

inhalt = (
    "Das ist der verbesserte Test\n"
    f"Zeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    "Sollte sofort in der ntfy-App erscheinen - wenn ja = alles gut!"
)

try:
    r = requests.post(
        URL,
        data=inhalt.encode("utf-8"),
        headers={
            "Title": "TEST - ntfy laeuft",
            "Priority": "high",
            "Tags": "test"
        },
        timeout=10
    )
    
    print(f"Status: {r.status_code}")
    if r.status_code in (200, 201):
        print("Nachricht wurde gesendet")
        print("Topic:", NTFY_TOPIC)
        print("Pruefe bitte die ntfy-App")
    else:
        print("Server-Antwort:")
        print(r.text)

except Exception as e:
    print("FEHLER:", type(e).__name__)
    print(str(e))