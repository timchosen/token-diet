# Web pages: trafilatura

Do not fetch raw HTML into the conversation. Get the article text only:

```bash
trafilatura -u "https://example.com/article" --markdown > /tmp/page.md && wc -c /tmp/page.md
```

Then read the file, or `rg` it if you need one part. Add `--no-comments` to drop comment threads, `--links` only if you need the links.

Fallback: a built-in web-fetch tool that returns a summary, with a narrow question.

Limit: pages built by JavaScript return little or nothing. If the output is under a few hundred characters, say so and use a browser tool instead.

Settings in `config.json` under `trafilatura`: `links` true: add `--links`. They override the numbers above.
