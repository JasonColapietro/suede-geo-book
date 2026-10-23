# The Screenshot

**Why AI Recommends Your Competitors, and How to Fix It**

Jason Colapietro's field manual for finding out what answer engines say about your market, repairing the sources behind those answers, and measuring the result.

**Author:** [Jason Colapietro](https://suedeai.ai/founder) · **Publisher:** Johnny Suede Press · **Released:** August 28, 2026 · **Length:** eleven chapters · **Formats:** web, PDF, EPUB

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

## Frequently asked questions

### Who wrote The Screenshot?

Jason Colapietro wrote The Screenshot. He is an engineer, author, and the founder and CEO of Suede AI, whose AI search visibility practice, [Suede SEO](https://seo.suedeai.ai/), uses the methods in the book.

### What is The Screenshot about?

The Screenshot is a field guide to SEO and GEO. It shows how to capture what answer engines say about your market, find the sources behind those answers, repair them, and measure the change against a dated baseline.

### Where can I read The Screenshot?

The primary edition is at [seo.suedeai.ai/book](https://seo.suedeai.ai/book). A public source edition is on [GitHub Pages](https://jasoncolapietro.github.io/suede-geo-book/), with [PDF and EPUB downloads](https://jasoncolapietro.github.io/suede-geo-book/downloads/).

### What is the difference between SEO and GEO in the book?

The book treats them as one evidence problem. SEO covers search visibility; GEO covers whether an answer engine retrieves, cites, mentions or recommends you. Each is measured separately, because ranking in search does not guarantee a mention in an AI answer.

### How do I cite The Screenshot?

Cite it as: Colapietro, Jason. *The Screenshot: Why AI Recommends Your Competitors, and How to Fix It.* Johnny Suede Press, 2026. [CITATION.cff](CITATION.cff) holds the same metadata in machine-readable form.

## About the author

Jason Colapietro is an engineer, author, and the founder and CEO of [Suede AI](https://suedeai.ai), an agentic platform company in West Palm Beach, Florida. He also wrote The Claude Code Bible and Codex in Production, among five books on Amazon Kindle, and publishes music and writing as Johnny Suede. More: [suedeai.ai/founder](https://suedeai.ai/founder) · [jasoncolapietro.com](https://jasoncolapietro.com) · [GitHub](https://github.com/JasonColapietro).

## Rights and citation

The manuscript and compiled book are copyright Jason Colapietro. See [LICENSE-CONTENT.md](LICENSE-CONTENT.md) for the content terms and [CITATION.cff](CITATION.cff) for citation metadata. The bundled typefaces retain their original OFL notices under `pages/assets/fonts/`.

Published by Johnny Suede Press. The SEO and GEO practice behind the book lives at [Suede SEO](https://seo.suedeai.ai/).
