# The Screenshot

**Why AI Recommends Your Competitors, and How to Fix It**

Jason Colapietro's field manual for finding out what answer engines say about your market, repairing the sources behind those answers, and measuring the result.

[Read the primary edition](https://seo.suedeai.ai/book) · [Open the public source edition](https://jasoncolapietro.github.io/suede-geo-book/) · [Download PDF or EPUB](https://jasoncolapietro.github.io/suede-geo-book/downloads/)

## What the book covers

The Screenshot treats SEO and GEO as one evidence problem. Search visibility, retrieval, citation, brand mention, and recommendation are related, but they are not interchangeable. The book shows how to capture a dated baseline, inspect the inputs an answer engine can reach, and make changes you can verify.

The eleven-chapter field guide moves through three questions:

1. **What changed?** Buyers now ask systems for a shortlist instead of reviewing ten blue links.
2. **Why do some companies get named?** Engines need accessible, extractable, corroborated evidence.
3. **What can you do this week?** Run the audit, repair the sources, and compare new answers with the baseline.

## Editions

- **Primary indexed edition:** [seo.suedeai.ai/book](https://seo.suedeai.ai/book)
- **Public source edition:** [jasoncolapietro.github.io/suede-geo-book](https://jasoncolapietro.github.io/suede-geo-book/)
- **Source manuscript:** `chapters/`
- **Assembled manuscript:** `THE-SCREENSHOT.md`
- **Reader files:** `exports/THE-SCREENSHOT.pdf` and `exports/THE-SCREENSHOT.epub`

The chapter mirrors on GitHub Pages are crawlable but not indexed. Their canonical links point to Suede SEO, keeping one primary search edition while preserving public access to the source.

## Build the reading edition

The GitHub Pages build needs Python 3, Pandoc, and no runtime package install:

```bash
python3 pages/build.py --output _site --pandoc pandoc
python3 tools/audit_public_copy.py _site
```

Build all book formats after editing a chapter:

```bash
python3 build_release.py
```

That command stages and validates the assembled Markdown, EPUB, and PDF before it replaces the existing release files. The focused EPUB and PDF builders remain available for local development.

## Evidence boundary

Every captured answer is a point-in-time observation, not a permanent verdict. This project makes no ranking or citation guarantee and uses no invented performance claims. It keeps crawler access, retrieval, citation, mention, recommendation, and factual accuracy separate.

## Rights and citation

The manuscript and compiled book are copyright Jason Colapietro. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for the content terms and [CITATION.cff](CITATION.cff) for citation metadata. The bundled typefaces retain their original OFL notices under `pages/assets/fonts/`.

Published by Johnny Suede Press. The SEO and GEO practice behind the book lives at [Suede SEO](https://seo.suedeai.ai/).
