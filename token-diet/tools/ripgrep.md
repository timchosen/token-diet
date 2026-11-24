# Searching files: ripgrep

Search, then read only the matching lines. Do not open whole files to look for something.

```bash
rg -n "pattern" path/                # matching lines with line numbers
rg -l "pattern" path/                # only file names
rg -c "pattern" path/                # only counts
rg -n -C2 "pattern" -g '*.ts' path/  # two lines of context, one file type
```

If the harness has its own search tool built on ripgrep (Claude Code's Grep is), use that; it is the same thing. After a match, read a line range around it, not the file.

Settings in `config.json` under `ripgrep`: `context` is the `-C` value; `max_matches` caps the matches printed. They override the numbers above.
