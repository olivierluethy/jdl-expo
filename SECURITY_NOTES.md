# Security Notes

This file records every hardcoded credential and secret found in the repository.

**No secret value is reproduced here** — only the file, the line number and the
kind of secret. To see a value, open the file itself.

**None of these were changed.** They were deliberately left exactly as they are.
Moving them into environment variables or a `.env` file would change which
database a script connects to and which notification topic it posts to, and a
silent behaviour change is a worse outcome than a documented risk. Acting on
what follows is a decision for the repository owner, not something this
reorganization made on their behalf.

---

## 1. MySQL credentials

### `database/schema_inspection/export_mysql_schema_to_sql.py`

| Line | Secret |
|---:|---|
| 44 | MySQL host — commented out (`localhost`) |
| 45 | MySQL host — commented out, a public IPv4 address of a remote server |
| 46 | MySQL host — active |
| 47 | MySQL port — active, not sensitive |
| 48 | MySQL username — active |
| 49 | MySQL password — **commented out, still in plain text** |
| 50 | MySQL password — active, plain text |
| 51 | MySQL database name — commented out |
| 52 | MySQL database name — active |

The commented-out lines are the important part: this file contains a **32-character
password for a remote, publicly addressable MySQL server**, alongside that
server's IP address, username and database name. Commenting a line out removes
it from execution, not from the file, and it is committed to git history.

### `database/parsers/import_sql_dump_into_mysql.py`

| Line | Secret |
|---:|---|
| 43 | MySQL host — a loopback address |
| 44 | MySQL port — not sensitive |
| 45 | MySQL username |
| 46 | MySQL password, plain text |
| 47 | MySQL database name |

This one targets a local database, so the exposure is smaller — unless the same
password is reused elsewhere.

## 2. ntfy topics

An ntfy topic name is a bearer secret: on the public `ntfy.sh` server, anyone who
knows the topic can both **read every notification sent to it and post to it**.
There is no separate authentication. The same topic is shared by all five
scripts below.

| File | Line | Secret |
|---|---:|---|
| `rss/scrapers/watch_swiss_news_rss_feeds.py` | 52 | ntfy topic name |
| `rss/scrapers/watch_msn_news_headlines.py` | 49 | ntfy topic, embedded in a full URL |
| `rss/scrapers/watch_msn_news_with_keywords.py` | 52 | ntfy topic, embedded in a full URL |
| `rss/scrapers/watch_msn_news_multi_query.py` | 53 | ntfy topic, embedded in a full URL |
| `rss/notifications/send_test_notification_ntfy.py` | 41 | ntfy topic name |

The topic is a long random-looking string, which makes it hard to guess but does
not make it a credential in any real sense — it is committed in plain text.

## 3. Not a credential, but worth knowing

| File | Line | Note |
|---|---:|---|
| `tunevote/frontend/session_page.jsx` | 48 | The production API and socket host is hardcoded rather than configured, so pointing the frontend at another environment means editing the source. Not a secret. |

## 4. What is *not* covered

- `database/dumps/` holds real exported data, including a phpMyAdmin dump with a
  `users` table. It was not inspected for personal data, password hashes or
  session tokens. If those dumps ever leave this machine, review them first.
- Git history retains every value above, including the ones now commented out.
  Rotating a credential does not remove it from history; that needs a history
  rewrite, which is out of scope here.

## 5. If you want to act on this

None of the following was done, and none of it should be done without testing:

1. Rotate the remote MySQL password. It is in plain text in a committed file and
   should be assumed compromised.
2. Restrict that MySQL server so it does not accept connections from anywhere.
3. Move the connection parameters into environment variables, then verify each
   script still reaches the database it is supposed to reach.
4. Regenerate the ntfy topic and update all five scripts together.
5. `.gitignore` now covers `.env`, so a local secrets file will not be committed
   by accident once you have somewhere to put these values.
