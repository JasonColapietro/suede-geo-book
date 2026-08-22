#!/usr/bin/env python3
"""Build the PDF edition: assembled markdown -> pandoc standalone HTML -> Chromium print-to-PDF.
No LaTeX on this machine, so the PDF is printed from styled HTML via Playwright's chromium.
The standalone command fails if THE-SCREENSHOT.md does not match current chapters.
Use build_release.py for a real all-format release."""
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from build_epub import assemble_master_text, release_lock

BASE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(BASE, "THE-SCREENSHOT.md")
HTML = os.path.join(BASE, "exports", "THE-SCREENSHOT.pdf.html")
PDF = os.path.join(BASE, "exports", "THE-SCREENSHOT.pdf")
PDF_DATE = b"D:20260821000000+00'00'"

PRINT_CSS = """
@page { size: 6in 9in; margin: 0.75in 0.7in; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; background:#f7f2e8; }
body { color:#2a2118; font:11pt/1.55 Georgia, "Times New Roman", serif;
  margin:0; max-width:none; }
h1 { font:700 20pt/1.15 Georgia, serif; color:#2a2118; border-top:1.5pt solid #8c2f22;
  padding-top:14pt; margin:0 0 10pt; page-break-before:always; break-before:page; }
h1:first-of-type { page-break-before:avoid; break-before:avoid; border-top:none; padding-top:0; }
h2 { font:italic 600 13.5pt/1.25 Georgia, serif; color:#8c2f22; margin:16pt 0 6pt; break-after:avoid; }
h3, h4 { color:#8c2f22; text-transform:uppercase; letter-spacing:.08em; font-size:9.5pt; margin:12pt 0 4pt; break-after:avoid; }
p { margin:0 0 8pt; orphans:3; widows:3; }
blockquote { border-left:2.5pt solid #8c2f22; margin:10pt 0; padding:2pt 0 2pt 12pt;
  color:#b06a24; font-style:italic; }
blockquote p { margin:0 0 4pt; }
ul, ol { margin:0 0 8pt; padding-left:18pt; }
li { margin-bottom:3pt; }
strong { font-weight:700; color:#2a2118; }
em { font-style:italic; }
hr { border:0; border-top:0.75pt solid rgba(42,33,24,.35); margin:14pt 0; }
a { color:#8c2f22; text-decoration:none; }
code { font:9.5pt "Courier New", monospace; background:#efe6d2; padding:0 2pt; }
header#title-block-header { text-align:center; padding:2.2in 0 0; page-break-after:always; break-after:page; }
header#title-block-header h1.title { border:0; padding:0; margin:0; font-size:30pt; letter-spacing:.02em; page-break-before:avoid; break-before:avoid; }
header#title-block-header p.subtitle { font-style:italic; color:#8c2f22; font-size:13pt; margin:10pt 0 0; }
header#title-block-header p.author { font-weight:700; margin:26pt 0 0; font-size:12pt; }
header#title-block-header p.date { color:#b06a24; margin:6pt 0 0; font-size:10pt; }
"""


def normalize_pdf_payload(payload):
    """Normalize volatile PDF fields and reject unexpected qpdf output."""
    payload, creation_count = re.subn(
        rb"/CreationDate \(D:[^)]+\)",
        b"/CreationDate (" + PDF_DATE + b")",
        payload,
    )
    payload, modified_count = re.subn(
        rb"/ModDate \(D:[^)]+\)",
        b"/ModDate (" + PDF_DATE + b")",
        payload,
    )
    payload, identifier_count = re.subn(
        rb"\s*/ID\s*\[\s*<[^>]+>\s*<[^>]+>\s*\]",
        b"",
        payload,
    )
    counts = {
        "CreationDate": creation_count,
        "ModDate": modified_count,
        "ID": identifier_count,
    }
    missing = [name for name, count in counts.items() if count == 0]
    if missing:
        raise RuntimeError(
            "PDF normalization did not find required fields: " + ", ".join(missing)
        )
    return payload


def render_pdf_with_chromium(html_path, pdf_path, run=subprocess.run):
    """Render one HTML file to PDF through the installed Playwright Chromium."""
    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path).resolve()
    js_path = html_path.parent / "print.cjs"
    print_js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto({json.dumps(html_path.as_uri())}, {{ waitUntil: 'networkidle' }});
  await page.pdf({{ path: {json.dumps(str(pdf_path))}, preferCSSPageSize: true, printBackground: true }});
  await browser.close();
}})().catch((e) => {{ console.error(e); process.exit(1); }});
"""
    js_path.write_text(print_js, encoding="utf-8")
    env = dict(os.environ)
    node_paths = [env.get("NODE_PATH"), os.path.expanduser("~/.npm-global/lib/node_modules")]
    env["NODE_PATH"] = os.pathsep.join(value for value in node_paths if value)
    run(["node", str(js_path)], check=True, env=env)


def verify_master_is_current(base, master):
    """Fail closed unless the master exactly matches current chapter sources."""
    base = Path(base)
    master = Path(master)
    expected, _ = assemble_master_text(base)
    if not master.is_file() or master.read_text(encoding="utf-8") != expected:
        raise RuntimeError(
            "THE-SCREENSHOT.md is stale; run python3 build_release.py before building PDF"
        )


def build_pdf_artifact(
    base,
    master,
    output,
    run=subprocess.run,
    render=render_pdf_with_chromium,
    find_executable=shutil.which,
):
    """Build one validated PDF at a staged output path."""
    base = Path(base)
    master = Path(master)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    qpdf = find_executable("qpdf")
    if not qpdf:
        raise RuntimeError("qpdf is required to normalize deterministic PDF output")

    with tempfile.TemporaryDirectory(prefix=".pdf-artifact-", dir=output.parent) as directory:
        scratch = Path(directory)
        css_path = scratch / "print.css"
        html_path = scratch / "THE-SCREENSHOT.pdf.html"
        raw_pdf = scratch / "THE-SCREENSHOT.raw.pdf"
        qdf = scratch / "THE-SCREENSHOT.qdf.pdf"
        normalized_pdf = scratch / "THE-SCREENSHOT.normalized.pdf"
        css_path.write_text(PRINT_CSS, encoding="utf-8")

        run([
            "pandoc", str(master),
            "-o", str(html_path),
            "--standalone",
            "--from", "markdown",
            "--css", "print.css",
            "--metadata", "title=THE SCREENSHOT",
            "--metadata", "subtitle=Why AI Recommends Your Competitors, and How to Fix It",
            "--metadata", "author=Jason Colapietro",
            "--metadata", "date=Johnny Suede Press · 2026",
            "--metadata", "lang=en-US",
        ], check=True)
        render(html_path, raw_pdf, run=run)
        run(
            [qpdf, "--qdf", "--object-streams=disable", str(raw_pdf), str(qdf)],
            check=True,
        )
        qdf.write_bytes(normalize_pdf_payload(qdf.read_bytes()))
        run([qpdf, "--static-id", str(qdf), str(normalized_pdf)], check=True)
        if not normalized_pdf.is_file():
            raise RuntimeError("qpdf completed without producing a normalized PDF")
        run([qpdf, "--check", str(normalized_pdf)], check=True)
        os.replace(normalized_pdf, output)

    return output


def build_pdf(
    base=BASE,
    run=subprocess.run,
    render=render_pdf_with_chromium,
    find_executable=shutil.which,
):
    """Build a standalone PDF only from a verified-current master."""
    base = Path(base)
    master = base / "THE-SCREENSHOT.md"
    with release_lock(base):
        exports = base / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        pdf = exports / "THE-SCREENSHOT.pdf"
        verify_master_is_current(base, master)

        with tempfile.TemporaryDirectory(prefix=".pdf-publish-", dir=exports) as directory:
            staged_pdf = Path(directory) / "THE-SCREENSHOT.pdf"
            build_pdf_artifact(
                base,
                master,
                staged_pdf,
                run=run,
                render=render,
                find_executable=find_executable,
            )
            verify_master_is_current(base, master)
            os.replace(staged_pdf, pdf)

    print(f"built {pdf} ({pdf.stat().st_size/1024:.0f} KB)")
    return pdf


if __name__ == "__main__":
    build_pdf()
