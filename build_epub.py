#!/usr/bin/env python3
"""Assemble chapters/*.md into THE-SCREENSHOT.md and build the EPUB via pandoc.
Pattern borrowed from the-signal-chain-book's pipeline, single edition."""
import glob
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
AUTHOR = "Jason Colapietro"
PUBLISHER = "Johnny Suede Press"
DATE = "2026"
TITLE = "THE SCREENSHOT"
SUBTITLE = "Why AI Recommends Your Competitors, and How to Fix It"
MASTER = os.path.join(BASE, "THE-SCREENSHOT.md")
EPUB = os.path.join(BASE, "exports", "THE-SCREENSHOT.epub")

chapters = sorted(glob.glob(os.path.join(BASE, "chapters", "*.md")))
assert chapters, "no chapters found"
parts = []
for path in chapters:
    with open(path, encoding="utf-8") as f:
        parts.append(f.read().strip())
with open(MASTER, "w", encoding="utf-8") as f:
    f.write("\n\n".join(parts) + "\n")
print(f"assembled {len(chapters)} files -> {MASTER}")

os.makedirs(os.path.join(BASE, "exports"), exist_ok=True)
cmd = [
    "pandoc", MASTER,
    "-o", EPUB,
    "--from", "markdown",
    "--toc", "--toc-depth=1",
    "--split-level=1",
    "--css", os.path.join(BASE, "epub-book.css"),
    "--metadata", f"title={TITLE}",
    "--metadata", f"subtitle={SUBTITLE}",
    "--metadata", f"author={AUTHOR}",
    "--metadata", f"publisher={PUBLISHER}",
    "--metadata", f"date={DATE}",
    "--metadata", "lang=en-US",
]
subprocess.run(cmd, check=True)
size = os.path.getsize(EPUB)
print(f"built {EPUB} ({size/1024:.0f} KB)")
