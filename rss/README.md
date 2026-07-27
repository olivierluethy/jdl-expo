# rss/

All scraping in this repository that is **not** YouTube-related. In practice
that means news monitoring: four long-running watchers that poll news sources for
a handful of keywords and push an alert when something new turns up.

The keywords they look for (`helvetus`, `stralium`, `betrug`, `luzerner`,
`uhren-armbändern`) suggest these were built to track coverage of a specific
Swiss company. They are unrelated to TuneVote and share no code with it.

All four deliver alerts through [ntfy](https://ntfy.sh), a push notification
service — notifications arrive in the ntfy phone app.

## scrapers/

| Script | Source | Matches on | Notes |
|---|---|---|---|
| `watch_swiss_news_rss_feeds.py` | ~40 RSS feeds: 20 Minuten, Blick, Luzerner Zeitung, NZZ, Tages-Anzeiger | Headline only | Polls every 240 s; also sends a "no hits" heartbeat each cycle |
| `watch_msn_news_headlines.py` | One Bing News search restricted to msn.com | Headline only | The earliest and simplest version |
| `watch_msn_news_with_keywords.py` | One Bing News search | Headline **and** full article text | Downloads each unseen article |
| `watch_msn_news_multi_query.py` | **Six** Bing News searches | Headline **and** full article text | The most complete version — prefer this one |

The three MSN watchers are successive generations of the same idea, and all
three share the same state file. **Run only one at a time**, or they will
overwrite each other's `seen_articles.json`.

None of them terminates on its own; stop them with Ctrl-C.

## notifications/

| Script | Purpose |
|---|---|
| `send_test_notification_ntfy.py` | Send a single test push to confirm the ntfy topic works |

Run this once before starting a watcher. Despite its original name
(`sms-test.py`) it sends no SMS.

## data/

| File | Contents |
|---|---|
| `seen_articles.json` | Headlines already reported, so the same article is not alerted twice |

This is state, not scratch — delete it and the watchers will re-alert on
articles you have already seen. It is rewritten whenever a new match is found.

## A note on fragility

The MSN watchers parse Bing's result page by selecting `a.title`. That markup is
undocumented and Bing changes it without notice. When it changes, the watchers
**fail silently**: no results, no error, no alerts. If a watcher has been quiet
for a suspiciously long time, check the selector before assuming there is
nothing to report. The RSS watcher does not have this problem, since RSS is a
stable published format — which is the main reason it is the more dependable of
the two approaches.

## Security

The ntfy topic name is hardcoded in all five scripts. On the public ntfy.sh
server a topic name is effectively a password: anyone who knows it can read
every notification sent to it and post to it. See
[`../SECURITY_NOTES.md`](../SECURITY_NOTES.md).

## Running

Paths are relative to the **repository root**:

```bash
python rss/notifications/send_test_notification_ntfy.py   # check the channel first
python rss/scrapers/watch_msn_news_multi_query.py         # then start a watcher
```
