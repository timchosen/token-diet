#!/usr/bin/env python3
"""Token diet settings page.

Run:   python3 settings.py            opens the page in your browser
       python3 settings.py --no-open  only prints the address
       python3 settings.py --check    runs the self-check and exits
Saves to config.json next to this file. Standard library only.
"""
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from pathlib import Path

CONFIG = Path(__file__).parent / "config.json"
MODES = ("off", "lite", "full", "custom")

# id: (job, what the tool does, part of Lite?, options)
# option: (label, default) for a switch, (label, default, min, max) for a number
TOOLS = {
    "trafilatura": ("Web pages", "trafilatura keeps the article and drops menus, ads and page code.", True,
                    {"links": ("Keep links in the text", False)}),
    "jq": ("JSON and API replies", "jq keeps only the fields the task needs.", True,
           {"max_rows": ("Most rows to print", 50, 1, 1000)}),
    "ripgrep": ("Searching files", "ripgrep returns the matching lines, not the files.", True,
                {"context": ("Lines shown around each match", 2, 0, 10),
                 "max_matches": ("Most matches to print", 40, 1, 500)}),
    "duckdb": ("Spreadsheets and data files", "DuckDB answers a question about the file; the file is never read.", True,
               {"limit": ("Most rows in an answer", 20, 1, 1000)}),
    "docling": ("PDFs and Office files", "Docling converts the file to clean text once, then only parts are read.", False,
                {"ocr": ("Read scanned pages (much slower)", False)}),
    "pagediff": ("Pages already read", "Keeps a copy of each page and reads only what changed.", False,
                 {"max_lines": ("Most changed lines to print", 200, 10, 2000)}),
    "rtk": ("Long command output", "RTK keeps the key lines of a command's output.", False, {}),
    "tenacity": ("Calls that sometimes fail", "Tenacity retries inside the script, so the job is not started over.", False,
                 {"attempts": ("Tries before giving up", 3, 1, 10)}),
    "pydantic": ("Checking structured output", "Pydantic reports only the wrong fields, so only those are fixed.", False, {}),
}


def default(mode="full"):
    return {"mode": mode, "tools": {
        k: {"on": mode == "full" or (mode == "lite" and t[2]), **{o: d[1] for o, d in t[3].items()}}
        for k, t in TOOLS.items()}}


def clean(raw):
    """Rebuild a config from known keys only. Unknown keys are dropped, bad values reset, numbers clamped."""
    raw = raw if isinstance(raw, dict) else {}
    src = raw.get("tools") if isinstance(raw.get("tools"), dict) else {}
    out = default()
    if raw.get("mode") in MODES:
        out["mode"] = raw["mode"]
    for k, t in TOOLS.items():
        got = src.get(k) if isinstance(src.get(k), dict) else {}
        if isinstance(got.get("on"), bool):
            out["tools"][k]["on"] = got["on"]
        for o, d in t[3].items():
            v = got.get(o)
            if len(d) == 2:
                if isinstance(v, bool):
                    out["tools"][k][o] = v
            elif isinstance(v, int) and not isinstance(v, bool):
                out["tools"][k][o] = max(d[2], min(d[3], v))
    return out


def load():
    try:
        return clean(json.loads(CONFIG.read_text()))
    except (OSError, ValueError):
        return default()


def schema():
    return [{"id": k, "job": t[0], "desc": t[1], "lite": t[2],
             "opts": [{"id": o, "label": d[0], "min": d[2], "max": d[3]} if len(d) == 4 else {"id": o, "label": d[0]}
                      for o, d in t[3].items()]} for k, t in TOOLS.items()]


def check():
    assert default("lite")["tools"]["jq"]["on"] and not default("lite")["tools"]["rtk"]["on"]
    assert all(t["on"] for t in default("full")["tools"].values())
    c = clean({"mode": "nope", "junk": 1, "tools": {"jq": {"on": False, "max_rows": 99999, "x": 1},
                                                    "tenacity": {"attempts": "3"}, "docling": {"ocr": 1}}})
    assert c["mode"] == "full" and "junk" not in c
    assert c["tools"]["jq"] == {"on": False, "max_rows": 1000}
    assert c["tools"]["tenacity"]["attempts"] == 3 and c["tools"]["docling"]["ocr"] is False
    assert clean("not a dict") == default() and clean(default("off")) == default("off")
    print("self-check passed")


PAGE = r"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Token diet settings</title>
<style>
:root{color-scheme:light dark;--bg:#f5f4ef;--card:#fff;--ink:#1c1b18;--mute:#63625c;--line:#dcdad2;--acc:#17603f;--on:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#151513;--card:#1e1e1b;--ink:#eceae4;--mute:#a3a29b;--line:#35342f;--acc:#62c794;--on:#10251a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:640px;margin:0 auto;padding:40px 16px 72px}
h1{font-size:1.6rem;margin:0 0 4px;letter-spacing:-.01em}
p{margin:0}.mute{color:var(--mute)}
fieldset{border:0;padding:0;margin:28px 0 8px}
legend{font-weight:600;padding:0;margin-bottom:8px}
.seg{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid var(--line);border-radius:10px;overflow:hidden;background:var(--card)}
.seg label{text-align:center;padding:12px 8px;cursor:pointer;font-weight:600;border-left:1px solid var(--line)}
.seg label:first-of-type{border-left:0}
.seg input{position:absolute;opacity:0}
.seg input:checked+label{background:var(--acc);color:var(--on)}
.seg input:focus-visible+label{outline:3px solid var(--ink);outline-offset:-3px}
#modehelp{min-height:3em;margin-top:10px}
details{margin-top:24px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
summary{padding:14px 16px;font-weight:600;cursor:pointer}
.tool{border-top:1px solid var(--line);padding:14px 16px}
.tool>label{display:flex;gap:12px;align-items:flex-start;cursor:pointer}
.tool input[type=checkbox]{width:20px;height:20px;margin:2px 0 0;accent-color:var(--acc);flex:none}
.tool b{display:block}.tool small{color:var(--mute);font-size:.9rem}
.opts{margin:10px 0 0 32px;display:grid;gap:8px}
.opts label{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:.95rem}
.opts input[type=number]{width:88px;padding:6px 8px;font:inherit;color:inherit;background:var(--bg);border:1px solid var(--line);border-radius:6px}
.tool.is-off .opts{display:none}
footer{display:flex;justify-content:space-between;align-items:center;margin-top:24px;gap:12px}
button{font:inherit;font-weight:600;padding:10px 18px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink);cursor:pointer}
</style>
<main>
<h1>Token diet</h1>
<p class="mute">Choose how much the assistant runs big inputs through local tools before reading them. Changes save as you make them and apply from the assistant's next task.</p>
<fieldset><legend>Mode</legend>
<div class="seg" id="seg"></div>
<p class="mute" id="modehelp" aria-live="polite"></p>
</fieldset>
<details id="adv"><summary>Advanced: each tool</summary><div id="tools"></div></details>
<footer><span class="mute" id="status" role="status"></span><button id="done" type="button">Done</button></footer>
</main>
<script>
const HELP={off:"Off. The assistant works the normal way and none of these tools are used.",
lite:"Lite. Only the four biggest savers: web pages, JSON replies, file search and spreadsheets.",
full:"Full. All nine tools are used whenever they fit the job.",
custom:"Custom. You have chosen the tools yourself under Advanced."};
let cfg,tools;const $=id=>document.getElementById(id);
async function save(){
  let ok=false;
  try{const r=await fetch("/api",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(cfg)});
    ok=r.ok;if(ok)cfg=await r.json();}catch(e){}
  $("status").textContent=ok?"Saved":"Could not save. Is settings.py still running?";
}
function draw(){
  $("seg").innerHTML=["off","lite","full"].map(m=>`<input type="radio" name="mode" id="m-${m}" value="${m}" ${cfg.mode===m?"checked":""}><label for="m-${m}">${m[0].toUpperCase()+m.slice(1)}</label>`).join("");
  $("modehelp").textContent=HELP[cfg.mode];
  const off=cfg.mode==="off";
  $("tools").innerHTML=tools.map(t=>{const c=cfg.tools[t.id];
    const opts=t.opts.map(o=>"min" in o
      ?`<label>${o.label}<input type="number" data-t="${t.id}" data-o="${o.id}" min="${o.min}" max="${o.max}" value="${c[o.id]}"></label>`
      :`<label>${o.label}<input type="checkbox" data-t="${t.id}" data-o="${o.id}" ${c[o.id]?"checked":""}></label>`).join("");
    return `<div class="tool ${c.on&&!off?"":"is-off"}"><label><input type="checkbox" data-t="${t.id}" ${c.on&&!off?"checked":""}><span><b>${t.job}</b><small>${t.desc}</small></span></label>${opts?`<div class="opts">${opts}</div>`:""}</div>`;}).join("");
}
$("seg").addEventListener("change",e=>{cfg.mode=e.target.value;
  if(cfg.mode!=="off")tools.forEach(t=>cfg.tools[t.id].on=cfg.mode==="full"||t.lite);
  draw();$("m-"+cfg.mode).focus();save();});
$("tools").addEventListener("change",e=>{const {t,o}=e.target.dataset,c=cfg.tools[t];
  if(!o){c.on=e.target.checked;
    // Switching one tool while Off starts from nothing on, so only that tool is used.
    if(cfg.mode==="off")tools.forEach(x=>{if(x.id!==t)cfg.tools[x.id].on=false});
    cfg.mode="custom";draw();document.querySelector(`#tools input[data-t="${t}"]:not([data-o])`).focus();}
  else if(e.target.type==="checkbox")c[o]=e.target.checked;
  else{const n=parseInt(e.target.value,10);if(!Number.isNaN(n))c[o]=n;}
  save().then(()=>{if(o&&e.target.type==="number")e.target.value=cfg.tools[t][o];});});
$("done").addEventListener("click",async()=>{
  try{await fetch("/quit",{method:"POST",headers:{"Content-Type":"application/json"},body:"{}"});}catch(e){}
  document.querySelector("main").innerHTML="<h1>Settings saved</h1><p class='mute'>You can close this tab.</p>";});
fetch("/api").then(r=>r.json()).then(r=>{cfg=r.config;tools=r.tools;if(cfg.mode==="custom")$("adv").open=true;draw();});
</script>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def host_ok(self):
        # A page on another site that points its own name at 127.0.0.1 arrives with that name here.
        port = self.server.server_address[1]
        return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

    def reply(self, code, body="{}", ctype="application/json"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.host_ok():
            return self.reply(403)
        if self.path == "/":
            return self.reply(200, PAGE, "text/html")
        if self.path == "/api":
            return self.reply(200, json.dumps({"config": load(), "tools": schema()}))
        self.reply(404)

    def do_POST(self):
        # Requiring a JSON content type means another website cannot post here: the browser
        # would first ask permission with a preflight request, which this server never grants.
        if not self.host_ok() or self.headers.get("Content-Type") != "application/json":
            return self.reply(403)
        if self.path == "/quit":
            self.reply(200)
            return threading.Thread(target=self.server.shutdown).start()
        if self.path != "/api":
            return self.reply(404)
        try:
            size = int(self.headers.get("Content-Length") or 0)
            if not 0 < size <= 65536:
                return self.reply(413)
            cfg = clean(json.loads(self.rfile.read(size)))
        except ValueError:
            return self.reply(400)
        CONFIG.write_text(json.dumps(cfg, separators=(",", ":")) + "\n")  # one line: the assistant reads it on every use
        self.reply(200, json.dumps(cfg))


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
        sys.exit()
    # Plain TCPServer: HTTPServer looks up the machine's network name on start, which can hang for a long time.
    server = TCPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Token diet settings: {url}\nPress Done on the page or Ctrl-C here to stop.", flush=True)
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
