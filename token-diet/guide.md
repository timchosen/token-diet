# Token diet guide

The rule: never read the big original. Run it through a tool on this computer and read only what comes out.

For the job in front of you, find its row. If that tool has `"on": true` in `config.json`, read its file and follow it. Read only that one file. If the tool is off, work the normal way for that job.

| You are about to… | Tool id | Read |
|---|---|---|
| Read a web page | trafilatura | `tools/trafilatura.md` |
| Read a JSON or API reply | jq | `tools/jq.md` |
| Find something in files | ripgrep | `tools/ripgrep.md` |
| Answer a question about a CSV, Parquet or spreadsheet | duckdb | `tools/duckdb.md` |
| Read a PDF or Office file | docling | `tools/docling.md` |
| Check a page you have already read | pagediff | `tools/pagediff.md` |
| Run a command with long output | rtk | `tools/rtk.md` |
| Write a script that calls something that can fail | tenacity | `tools/tenacity.md` |
| Write a script that uses JSON from an API or a model | pydantic | `tools/pydantic.md` |

- Tool missing (`command -v <tool>` fails): read `install.md`, show the user the line for this system and ask before running it. Until then use the fallback in the tool's file.
- User wants to change settings: run `python3 settings.py` from this folder in the background (`py` on Windows) and give them the address it prints. For a plain "off" or "full" you may set `"mode"` in `config.json` yourself; for "full" also set every tool's `on` to true.
- Print counts and sizes before contents, cap everything you print, and keep big intermediate results in temp files.
- If the task truly needs the whole document, read it and say why.
