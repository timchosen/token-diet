# Installing the tools

Read this only when a tool that is switched on is missing. Nothing here needs Homebrew, and on macOS and Linux only the `apt`/`dnf` lines need an administrator password.

## How to install one

1. Find the system: `uname -s` prints `Darwin` (macOS) or `Linux`; on Windows `uname` is missing or prints `MINGW`/`MSYS`, and `$env:OS` is `Windows_NT`.
2. Pick the first line in the tool's row whose installer exists (`command -v brew`, `uv`, `winget`, `apt`, `dnf`).
3. Show the user that exact line and ask before running it. Never install silently.
4. Check it worked with `command -v <tool>`. If the shell cannot find it, the folder is not on PATH: `~/.local/bin` on macOS and Linux; on Windows open a new terminal.
5. If the user says no, or the install fails, use the fallback in SKILL.md and carry on.

## Step zero on a bare machine: uv

`uv` installs into the user's own folder, needs no admin rights and brings its own Python. Five of the nine tools install through it on every system.

| System | Command |
|---|---|
| macOS, Linux | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Windows (PowerShell) | `irm https://astral.sh/uv/install.ps1 \| iex` |

## The tools

| Tool | Any system, with uv | macOS with Homebrew | macOS without Homebrew | Linux | Windows |
|---|---|---|---|---|---|
| trafilatura | `uv tool install trafilatura` | same | same | same | same |
| Docling | `uv tool install docling` | same | same | same | same |
| DuckDB | `uv tool install duckdb-cli` | `brew install duckdb` | `curl https://install.duckdb.org \| sh` | `curl https://install.duckdb.org \| sh` | `winget install DuckDB.cli` |
| changedetection.io | `uv tool install changedetection.io` | same | same | same, or Docker | same, or Docker |
| Tenacity, Pydantic | no install: `uv run --with tenacity --with pydantic script.py` | same | same | same | same |
| jq | none | `brew install jq` | see below | `sudo apt install jq` or `sudo dnf install jq` | `winget install jqlang.jq` |
| ripgrep | none | `brew install ripgrep` | see below | `sudo apt install ripgrep` or `sudo dnf install ripgrep` | `winget install BurntSushi.ripgrep.MSVC` |
| RTK | none | `brew install rtk` | `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh \| sh` | same script | `winget install rtk-ai.rtk` |

Without uv, `pipx install <name>` or `python3 -m pip install --user <name>` does the same job for the first four rows.

### jq on macOS without Homebrew (or Linux without admin rights)

jq is one file. Download it into the user's own folder:

```bash
mkdir -p ~/.local/bin && curl -L -o ~/.local/bin/jq "https://github.com/jqlang/jq/releases/latest/download/jq-$(uname -s | sed 's/Darwin/macos/;s/Linux/linux/')-$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')" && chmod +x ~/.local/bin/jq
```

### ripgrep on macOS without Homebrew (or Linux without admin rights)

In Claude Code nothing is needed: the built-in Grep tool is ripgrep. Elsewhere, download the build for the machine from https://github.com/BurntSushi/ripgrep/releases/latest (`aarch64-apple-darwin` for Apple silicon, `x86_64-apple-darwin` for Intel, `x86_64-unknown-linux-musl` for Linux), unpack it and move `rg` into `~/.local/bin`. The file name contains the version number, so read it from the release page first. Until then `grep -rn` is the fallback.

### RTK

After installing, run `rtk gain`. It must show a savings summary. "command not found" or an unrelated tool means a different project with the same name was installed; remove it and use the lines above. `rtk init -g` switches on automatic use in Claude Code; it changes the user's global settings, so ask first.

## What has been tested

On macOS with Homebrew: ripgrep, jq, DuckDB, RTK (Homebrew), trafilatura and Docling (uv). The install scripts and download addresses for the other systems were checked to exist on 2026-11-23 but were not run. The Windows and Linux lines come from each project's own instructions.
