# The Screenshot

*Why AI Recommends Your Competitors, and How to Fix It* is a founder-facing GEO and AI-visibility book by Jason Colapietro, published by Johnny Suede Press. It is the fourth published book in the current author canon. Every chapter is free at seo.suedeai.ai, with the packaged PDF and EPUB available from the same site.

## Build

Use the all-format release command for every real rebuild:

```bash
python3 build_release.py
```

It stages the current master, EPUB and PDF, validates and normalizes both
binaries, then publishes all three together. If any build or publication step
fails, the prior three-file release stays intact. A cross-process lock covers
the source snapshot through publication. If rollback itself fails, durable
last-good copies remain under `.release-recovery/` and the error reports the
exact recovery directory.

The standalone builders remain available for focused development:

```bash
python3 build_epub.py   # publishes a coherent master and EPUB pair
python3 build_pdf.py    # locks the repository and requires a current master
```

The standalone commands are not the release path. Both require the same
Pandoc, Playwright Chromium and qpdf tools used by `build_release.py`.

## Layout

- `chapters/`: 00 front matter, 01-05 Part I, 06-10 Part II, 11 close, and 12 back matter
- `THE-SCREENSHOT.md`: assembled master, generated from the sorted chapter files
- `exports/`: built EPUB and PDF

The public offer is the retainer practice at https://seo.suedeai.ai. The old Suede Scan fixed-price ladder is retired and must not be restored during a rebuild. The free crawler-access check remains at https://optimize.suedeai.ai.

Evidence rules: point-in-time disclosures, no outcome guarantees, no invented statistics, and clear separation between crawler access, retrieval, citation, brand mention, recommendation and factual accuracy.
