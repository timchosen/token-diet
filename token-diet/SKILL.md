---
name: token-diet
description: Cut token use by running big inputs through a local tool first and reading only the small result. Use before fetching a web page, reading an API or JSON reply, searching files, answering a question about a CSV/spreadsheet, reading a PDF, re-checking a page for changes, running a command with long output, or writing a script that calls a flaky API or parses model/API output. Also use when the user says "token diet", "save tokens", "cut usage", or complains about hitting usage limits.
---

Read `config.json` in this folder (missing: every tool is on).

- `"mode":"off"`: stop. Read nothing else here and work the normal way.
- Anything else: read `guide.md` in this folder and follow it.

To change settings: in Claude Code the user has a Token diet row above the prompt and the `/token-diet-settings` panel. Anywhere else, run `python3 settings.py` from this folder (`py` on Windows).
