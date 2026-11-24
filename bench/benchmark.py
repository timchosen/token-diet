#!/usr/bin/env python3
"""Measure what token-diet saves on five fixed, public jobs.

Each job downloads a public input, measures it raw, runs the tool the skill
would use, and measures the tool's output. Prints a Markdown table.

    python3 bench/benchmark.py              sizes in bytes, tokens estimated as bytes / 4
    python3 bench/benchmark.py --tokens     also real Claude token counts (needs `pip install anthropic`
                                            and an Anthropic credential; counting is free)
    python3 bench/benchmark.py --check      self-check, no network

Standard library only, apart from the tools being measured (trafilatura, jq,
ripgrep, duckdb, rtk, git) and the optional `anthropic` package. A job whose
tool is missing is skipped and named.

"Raw" is the input as a naive read would take it. Agents often do better than
that by default (Claude Code's web fetch summarizes pages, its file reader stops
at a size limit), so treat "raw" as the worst case, not as what every agent does.
"""
import math
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

UA = "token-diet-benchmark (https://github.com/timchosen/token-diet)"
MODEL = "claude-opus-5-5"
# Requests above this are not sent for counting; the count is estimated instead.
COUNT_LIMIT = 3_000_000
RIPGREP_TAG = "14.1.1"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def run(argv, stdin: bytes | None = None, cwd=None) -> bytes:
    env = {k: v for k, v in os.environ.items() if k != "AI_AGENT"}  # duckdb changes its output when this is set
    return subprocess.run(argv, input=stdin, cwd=cwd, env=env, capture_output=True, check=True, timeout=600).stdout


def job_web(tmp: Path):
    raw = fetch("https://en.wikipedia.org/wiki/Costco")
    return raw, run(["trafilatura", "--markdown"], stdin=raw)


def job_jq(tmp: Path):
    raw = fetch("https://api.github.com/repos/BurntSushi/ripgrep")
    return raw, run(["jq", "-c", "{name, stars: .stargazers_count, language}"], stdin=raw)


def job_ripgrep(tmp: Path):
    archive = tmp / "rg.tar.gz"
    archive.write_bytes(fetch(f"https://codeload.github.com/BurntSushi/ripgrep/tar.gz/refs/tags/{RIPGREP_TAG}"))
    with tarfile.open(archive) as t:
        t.extractall(tmp / "src", filter="data")  # refuses links and paths that leave the folder
    root = next((tmp / "src").iterdir()) / "crates"
    files = run(["rg", "-l", "fn search", str(root)]).decode().split()
    raw = b"".join(Path(f).read_bytes() for f in files)
    return raw, run(["rg", "-n", "fn search", str(root)])


def job_duckdb(tmp: Path):
    csv = tmp / "airports.csv"
    csv.write_bytes(fetch("https://davidmegginson.github.io/ourairports-data/airports.csv"))
    query = (f"SELECT iso_country, count(*) AS n FROM '{csv}' WHERE type='large_airport' "
             "GROUP BY 1 ORDER BY n DESC LIMIT 5")
    return csv.read_bytes(), run(["duckdb", "-csv", "-c", query])


def job_rtk(tmp: Path):
    repo = tmp / "repo"
    run(["git", "clone", "-q", "--filter=blob:none", "--depth", "30", "--no-checkout",
         "https://github.com/BurntSushi/ripgrep", str(repo)])
    return run(["git", "log", "-30"], cwd=repo), run(["rtk", "git", "log", "-30"], cwd=repo)


JOBS = [
    ("Wikipedia page on Costco", "trafilatura", job_web),
    ("GitHub API reply, three fields wanted", "jq", job_jq),
    (f'Search ripgrep {RIPGREP_TAG} source for "fn search"', "rg", job_ripgrep),
    ('86k-row airports CSV, "which countries have the most large airports"', "duckdb", job_duckdb),
    ("`git log -30` of the ripgrep repository", "rtk", job_rtk),
]


def saved(raw: int, out: int) -> str:
    """Percent saved, rounded down so the table never overstates."""
    if raw <= 0:
        return "n/a"
    pct = 100 * (1 - out / raw)
    if pct >= 99:
        return f"{math.floor(pct * 100) / 100:.2f}%"
    return f"{math.floor(pct)}%"


def counter():
    try:
        import anthropic
    except ImportError:
        sys.exit("--tokens needs the anthropic package: pip install anthropic")
    client = anthropic.Anthropic()

    def count(data: bytes):
        if len(data) > COUNT_LIMIT:
            return None
        text = data.decode("utf-8", errors="replace")
        try:
            return client.messages.count_tokens(model=MODEL, messages=[{"role": "user", "content": text}]).input_tokens
        except anthropic.APIError as e:
            print(f"  token count failed ({type(e).__name__}); estimating instead", file=sys.stderr)
            return None

    return count


def tokens(n_bytes: int, counted):
    return f"{counted:,}" if counted is not None else f"~{n_bytes // 4:,}"


def main():
    if "--check" in sys.argv:
        assert saved(1_264_671, 112_566) == "91%"
        assert saved(5961, 50) == "99.16%"
        assert saved(12_763_057, 420) == "99.99%"
        assert saved(7079, 3244) == "54%"
        assert saved(0, 0) == "n/a"
        assert tokens(4000, None) == "~1,000" and tokens(4000, 812) == "812"
        print("self-check passed")
        return

    count = counter() if "--tokens" in sys.argv else None
    rows, total_raw, total_out, skipped = [], 0, 0, []
    with tempfile.TemporaryDirectory(prefix="token-diet-bench-") as d:
        for name, tool, fn in JOBS:
            if shutil.which(tool) is None:
                skipped.append(f"{name} ({tool} not installed)")
                continue
            print(f"running: {name}", file=sys.stderr)
            try:
                raw, out = fn(Path(d))
            except (OSError, subprocess.SubprocessError, ValueError) as e:
                skipped.append(f"{name} (failed: {type(e).__name__}: {e})")
                continue
            total_raw += len(raw)
            total_out += len(out)
            cells = [name, tool, f"{len(raw):,}", f"{len(out):,}", saved(len(raw), len(out))]
            if count:
                cells[2:4] = [tokens(len(raw), count(raw)), tokens(len(out), count(out))]
            rows.append(cells)

    unit = f"tokens ({MODEL}; ~ = estimated as bytes / 4)" if count else "bytes"
    print(f"\n| Job | Tool | Raw {unit} | Through the tool | Saved |\n|---|---|---|---|---|")
    for cells in rows:
        print("| " + " | ".join(cells) + " |")
    if rows:
        print(f"\nAll {len(rows)} jobs together: {total_raw:,} bytes to {total_out:,} bytes, "
              f"{saved(total_raw, total_out)} saved (about {total_raw // 4:,} to {total_out // 4:,} tokens at bytes / 4).")
    for s in skipped:
        print(f"Skipped: {s}")


if __name__ == "__main__":
    main()
