# The Screenshot

*Why AI Recommends Your Competitors, and How to Fix It* — a founder-facing GEO / AI-visibility ebook by Jason Colapietro (Johnny Suede Press). Marketing asset for Suede Scan: every chapter funnels to the free check at audit.suedeai.ai and the paid ladder at scan.suedeai.ai.

## Build

```bash
python3 build_epub.py   # assembles chapters/*.md -> THE-SCREENSHOT.md -> exports/THE-SCREENSHOT.epub (requires pandoc)
```

## Layout

- `chapters/` — 00 front matter, 01-05 Part I (the stakes), 06-10 Part II (the fix), 11 close, 12 back matter (checklist, glossary, offer page)
- `THE-SCREENSHOT.md` — assembled master (generated)
- `exports/` — built EPUB

Sources: suede-geo (Suede Scan spec, operations, launch campaign), suede-ai-seo, suede-seo-audit, suede-visibility-grader. Evidence rules carried over verbatim: point-in-time disclaimers everywhere, no outcome guarantees, no invented statistics.
