"""
send_test_notification_ntfy.py — send one test push notification through ntfy.

Description:
    A connectivity check for the notification channel that every watcher in this
    project depends on. It builds a short message stamped with the current local
    time and posts it to the shared ntfy topic with a title, high priority and a
    tag, then prints the HTTP status code returned by the server. Status 200 or
    201 means the message was accepted and should appear in the ntfy app within
    seconds; any other status has the server's response body printed so the cause
    is visible. Network and other exceptions are caught and reported by type.

Requirements:
    - Python 3.x
    - Packages: requests
    - External services: ntfy.sh
    - Environment variables / credentials needed: none — the ntfy topic is
      hardcoded and acts as a shared secret, see SECURITY_NOTES.md

Inputs:
    The NTFY_TOPIC constant in this file. No command-line arguments are parsed.

Outputs:
    One push notification to the configured ntfy topic; status lines on stdout.
    No files are written.

Usage:
    # from the repository root, with the virtual environment activated
    python rss/notifications/send_test_notification_ntfy.py

Notes:
    Despite the original file name, sms-test.py, this sends no SMS — ntfy is a
    push notification service. Run it once before starting a watcher to confirm
    the topic works. Anyone who knows the topic name can read the notifications
    or post to it, so treat it as a secret.
"""

import requests
import datetime

NTFY_TOPIC = "derek-sparen-spalter-alert-xyz-gradunal-k3f9x2p7q-k3f9x2p7q"
URL = f"https://ntfy.sh/{NTFY_TOPIC}"

inhalt = (
    "This is the improved test\n"
    f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    "It should appear in the ntfy app immediately - if it does, everything works."
)

try:
    r = requests.post(
        URL,
        data=inhalt.encode("utf-8"),
        headers={
            "Title": "TEST - ntfy is running",
            "Priority": "high",
            "Tags": "test"
        },
        timeout=10
    )
    
    print(f"Status: {r.status_code}")
    if r.status_code in (200, 201):
        print("Message sent")
        print("Topic:", NTFY_TOPIC)
        print("Please check the ntfy app")
    else:
        print("Server response:")
        print(r.text)

except Exception as e:
    print("ERROR:", type(e).__name__)
    print(str(e))