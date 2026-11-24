# Pages you have already read: send only the change

Keep the cleaned copy trafilatura made (see `trafilatura.md`) and compare the next fetch against it. Read the diff, never the page again.

```bash
mkdir -p ~/.cache/token-diet
f=~/.cache/token-diet/$(printf %s "$URL" | shasum | cut -c1-16).md
trafilatura -u "$URL" --markdown > "$f.new"
[ -f "$f" ] && diff -u "$f" "$f.new" | head -200 || echo "first snapshot saved"
mv "$f.new" "$f"
```

An empty diff means nothing changed: say that and stop.

For a page the user wants watched all the time (prices, jobs, a competitor's page), use changedetection.io, which checks on a schedule and keeps the history. If one is running, list watches with `curl -s -H "x-api-key: $CDIO_KEY" "$CDIO_URL/api/v1/watch"` and read a watch's snapshots from `/api/v1/watch/<uuid>/history`, then diff the last two as above. Do not start one without asking; it is a server that keeps running.

Settings in `config.json` under `pagediff`: `max_lines` is the `head` cap on the diff. They override the numbers above.
