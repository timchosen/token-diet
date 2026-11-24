# PDFs and Office files: Docling

Convert once to Markdown on disk, then search or read the part you need.

```bash
docling report.pdf --to md --image-export-mode placeholder --no-ocr --output /tmp/docling > /tmp/docling.log 2>&1; wc -c /tmp/docling/report.md
rg -n "termination|liability" /tmp/docling/report.md
```

Always pass `--image-export-mode placeholder`: without it every picture is embedded as text and the file is about 20 times bigger (583 KB against 29 KB on a 9-page paper). Send docling's own log to a file; it is long. Drop `--no-ocr` only for a scanned PDF, when the output comes back nearly empty; OCR is much slower.

Tables come out as Markdown tables. The first run downloads models and is slow; say so.

Fallback: `pdftotext -layout report.pdf /tmp/report.txt`, or the harness's own PDF reader with a page range.

Settings in `config.json` under `docling`: `ocr` true: leave out `--no-ocr`. They override the numbers above.
