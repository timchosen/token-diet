# token-diet

**99.2% fewer tokens across five real jobs: about 3.5 million down to about 29,400.**

Coding agents burn tokens reading things they don't need: full web pages when they only want the article, entire CSVs for one aggregate, whole API replies for three fields, noisy command output, and PDFs full of base64 images.

token-diet is a skill that stops that. Before the agent reads a big input, it runs the input through a free local tool and only reads the small result. In single-run tests on one Mac this cut roughly 3.5 million tokens down to about 29,400 — **99.2% fewer tokens** across five real jobs. It is written for Claude Code and as a standard `SKILL.md` folder for Grok and any other agent that can follow one (tested in Claude Code).

A settings panel (Off / Lite / Full) lives above the Claude Code message box so you can turn the whole thing off or keep only the biggest savers.

## What it uses

| Job | Tool | What the agent reads |
|---|---|---|
| Read a web page | [trafilatura](https://github.com/adbar/trafilatura) | the article text, not the HTML |
| Read a JSON or API reply | [jq](https://github.com/jqlang/jq) | only the fields the task needs |
| Search files | [ripgrep](https://github.com/BurntSushi/ripgrep) | matching lines, not files |
| Question about a CSV, Parquet or spreadsheet | [DuckDB](https://github.com/duckdb/duckdb) | the query result |
| Read a PDF or Office file | [Docling](https://github.com/docling-project/docling) | clean Markdown (no base64 images), then only the parts needed |
| Re-check a page already read | saved copy + `diff`, or [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | only what changed |
| Command with long output | [RTK](https://github.com/rtk-ai/rtk) | the key lines |
| Script that calls a flaky service | [Tenacity](https://github.com/jd/tenacity) | nothing: the retry happens inside the script |
| Script that uses structured output | [Pydantic](https://github.com/pydantic/pydantic) | only the fields that failed |

## Savings

**99.2% fewer tokens across five real jobs: about 3.5 million down to about 29,400.**

| Job | Raw | Through the tool | Saved |
|---|---|---|---|
| Wikipedia page on Costco (trafilatura) | 1,264,671 bytes | 112,566 | 91% |
| GitHub API reply, three fields wanted (jq) | 5,961 | 50 | 99% |
| Search 6 source files for one word (ripgrep) | 47,120 | 1,487 | 97% |
| 86,383-row airports CSV, "which countries have the most large airports" (DuckDB) | 12,763,057 | 420 | 99.99% |
| `git log -30` (RTK) | 7,079 | 3,244 | 54% |

Docling: the skill's flags make a 9-page PDF's Markdown 95% smaller than Docling's defaults (583,815 → 29,046 bytes) because the defaults embed every image as text.

Single runs on one Mac. Tokens estimated as bytes ÷ 4. The overall figure is dominated by the spreadsheet — your saving depends on what you feed the agent. If you rarely hand it web pages, data files or PDFs, expect much less.

## What the skill itself costs

The skill is split so only the part needed is loaded:

- **Off**: ~290 tokens each time it triggers (short settings check, then stop).
- **On**: ~960 tokens for a job (short guide + the one tool file in use).

## Install

You need git and Python 3. Nothing else is required up front: when a tool is missing the agent shows the install line for your system and asks before running it.

**macOS / Linux**

```bash
git clone https://github.com/timchosen/token-diet && cp -R token-diet/token-diet token-diet/token-diet-panel ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/timchosen/token-diet; Copy-Item -Recurse token-diet\token-diet, token-diet\token-diet-panel "$env:USERPROFILE\.claude\skills\"
```

Start a new Claude Code session. You should see a "Token diet" row above the message box.

For Grok, Cursor, or any other agent that reads `SKILL.md` folders, copy only the `token-diet` folder into that agent's skills directory.

Per-system install lines for the nine tools live in [`token-diet/install.md`](token-diet/install.md).

## Settings

| Mode | What is used |
|---|---|
| Off | Nothing. Normal behaviour. |
| Lite | trafilatura, jq, ripgrep, DuckDB (the four biggest savers) |
| Full | All nine (default) |
| Custom | Whatever you switched on |

Three ways to change settings (all write the same `config.json`):

- **Claude Code:** Off / Lite / Full buttons + Tune panel (or `/token-diet-settings`).
- **Browser:** `python3 ~/.claude/skills/token-diet/settings.py` (127.0.0.1 only, standard library).
- **By hand:** edit `config.json`.

## Limits

- Tested on macOS. Linux / Windows install lines come from each project's docs.
- The skill is instructions; an agent can ignore them.
- Panel works in Claude Code; other agents use the browser page.
- For tiny inputs the skill overhead can exceed the savings.

## License

MIT. The nine tools are separate projects under their own licenses.
