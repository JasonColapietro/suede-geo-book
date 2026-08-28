"""Escaped HTML templates for the public-source edition."""

from __future__ import annotations

import html
import json
from collections.abc import Sequence

from pages import content
from pages.model import Chapter, Publication


PROJECT_PATH = "/suede-geo-book"


def _e(value: str) -> str:
    return html.escape(value, quote=True)


def _json_ld(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def _site_graph(publication: Publication, page_url: str, page_name: str) -> dict[str, object]:
    person_id = "https://suedeai.ai/founder#person"
    book_id = f"{publication.canonical_base}#book"
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{publication.pages_base}/#website",
                "url": f"{publication.pages_base}/",
                "name": f"{publication.title} public source edition",
                "author": {"@id": person_id},
                "hasPart": {"@id": book_id},
            },
            {
                "@type": "WebPage",
                "@id": f"{page_url}#webpage",
                "url": page_url,
                "name": page_name,
                "isPartOf": {"@id": f"{publication.pages_base}/#website"},
                "about": {"@id": book_id},
            },
            {
                "@type": "Book",
                "@id": book_id,
                "name": publication.title,
                "alternateName": publication.subtitle,
                "url": publication.canonical_base,
                "sameAs": publication.repository_base,
                "author": {"@id": person_id},
                "publisher": {"@type": "Organization", "name": publication.publisher},
                "inLanguage": "en-US",
            },
            {
                "@type": "Person",
                "@id": person_id,
                "name": publication.author,
                "alternateName": "Johnny Suede",
                "url": "https://suedeai.ai/founder",
                "sameAs": [
                    "https://github.com/JasonColapietro",
                    "https://www.linkedin.com/in/jasoncolapietro",
                ],
            },
        ],
    }


def _document(
    publication: Publication,
    *,
    title: str,
    description: str,
    canonical: str,
    body: str,
    body_class: str,
    robots: str | None = None,
    graph: dict[str, object] | None = None,
) -> str:
    robots_meta = f'\n  <meta name="robots" content="{_e(robots)}">' if robots else ""
    schema = graph or _site_graph(publication, canonical, title)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_e(title)}</title>
  <meta name="description" content="{_e(description)}">{robots_meta}
  <link rel="canonical" href="{_e(canonical)}">
  <link rel="stylesheet" href="{PROJECT_PATH}/assets/book.css">
  <script type="application/ld+json">{_json_ld(schema)}</script>
</head>
<body class="{_e(body_class)}">
  <a class="skip-link" href="#content">Skip to the book</a>
  <header class="site-head">
    <a class="wordmark" href="{PROJECT_PATH}/">{_e(publication.title)}</a>
    <nav aria-label="Primary">
      <a href="{PROJECT_PATH}/read/">Read</a>
      <a href="{PROJECT_PATH}/about/">About</a>
      <a href="{PROJECT_PATH}/downloads/">Formats</a>
      <a href="{_e(publication.repository_base)}">Source</a>
    </nav>
  </header>
  {body}
  <footer class="site-foot">
    <p>{_e(publication.author)} / {_e(publication.publisher)}</p>
    <p><a href="{_e(publication.canonical_base)}">Primary edition</a> · <a href="https://seo.suedeai.ai/#contact">SEO and GEO practice</a></p>
  </footer>
  <script src="{PROJECT_PATH}/assets/book.js" defer></script>
</body>
</html>
"""


def render_home(publication: Publication, chapters: Sequence[Chapter]) -> str:
    chapter_links = "".join(
        f'<li><span>{chapter.ordinal:02d}</span><a href="{PROJECT_PATH}/read/{_e(chapter.slug)}/">{_e(chapter.title)}</a></li>'
        for chapter in chapters
        if 1 <= chapter.ordinal <= 11
    )
    body = f"""
  <main id="content">
    <section class="hero">
      <div class="capture-strip" aria-label="Publication record">
        <span>CAPTURE 01</span><span>{_e(publication.publication_date)}</span><span>PUBLIC SOURCE</span>
      </div>
      <p class="kicker">{_e(content.HOME_KICKER)}</p>
      <h1>{_e(publication.title)}</h1>
      <p class="subtitle">{_e(publication.subtitle)}</p>
      <p class="thesis">{_e(content.HOME_THESIS)}</p>
      <div class="actions">
        <a class="button primary" href="{_e(publication.canonical_base)}">Read the primary edition</a>
        <a class="button" href="{_e(publication.repository_base)}">Browse the source</a>
      </div>
    </section>
    <section class="proof-layout" aria-labelledby="field-manual-title">
      <div class="proof-copy">
        <p class="section-label">THE FIELD MANUAL</p>
        <h2 id="field-manual-title">The answer is already in the room.</h2>
        <p>{_e(content.HOME_INTRO)}</p>
        <p>{_e(content.SOURCE_NOTE)}</p>
      </div>
      <ol class="chapter-ledger">{chapter_links}</ol>
    </section>
    <section class="service-band" aria-labelledby="service-title">
      <p class="section-label">THE PRACTICE BEHIND THE BOOK</p>
      <h2 id="service-title">{_e(content.SERVICE_HEADING)}</h2>
      <p>{_e(content.SERVICE_COPY)}</p>
      <a class="text-link" href="https://seo.suedeai.ai/#contact">Ask about SEO and GEO</a>
    </section>
    <section class="evidence-note" aria-labelledby="evidence-title">
      <p class="section-label">EVIDENCE BOUNDARY</p>
      <h2 id="evidence-title">A dated answer, not a permanent verdict</h2>
      <p>{_e(content.EVIDENCE_NOTE)}</p>
    </section>
  </main>"""
    return _document(
        publication,
        title=f"{publication.title} | Public source edition",
        description=content.HOME_THESIS,
        canonical=f"{publication.pages_base}/",
        body=body,
        body_class="home",
    )


def render_read_index(publication: Publication, chapters: Sequence[Chapter]) -> str:
    items = "".join(
        f'<li><span>{chapter.ordinal:02d}</span><div><small>{_e(chapter.section)}</small><a href="{PROJECT_PATH}/read/{_e(chapter.slug)}/">{_e(chapter.title)}</a></div></li>'
        for chapter in chapters
    )
    body = f"""
  <main id="content" class="index-sheet">
    <p class="section-label">PUBLIC READING MIRROR</p>
    <h1>Read {_e(publication.title)}</h1>
    <p>This mirror is provided for public reading and source inspection. The indexed edition lives on <a href="{_e(publication.canonical_base)}">Suede SEO</a>.</p>
    <ol class="reading-index">{items}</ol>
  </main>"""
    return _document(
        publication,
        title=f"Read {publication.title}",
        description=f"Public reading mirror for {publication.title} by {publication.author}.",
        canonical=f"{publication.pages_base}/read/",
        robots="noindex,follow",
        body=body,
        body_class="read-index",
    )


def render_chapter(
    publication: Publication,
    chapter: Chapter,
    fragment: str,
    previous: Chapter | None,
    following: Chapter | None,
) -> str:
    prev_link = (
        f'<a rel="prev" href="{PROJECT_PATH}/read/{_e(previous.slug)}/">Previous: {_e(previous.title)}</a>'
        if previous
        else "<span></span>"
    )
    next_link = (
        f'<a rel="next" href="{PROJECT_PATH}/read/{_e(following.slug)}/">Next: {_e(following.title)}</a>'
        if following
        else "<span></span>"
    )
    body = f"""
  <main id="content" class="reader-grid">
    <aside class="reader-stamp" aria-label="Chapter record">
      <span>CAPTURE {chapter.ordinal:02d}</span>
      <span>{_e(chapter.section)}</span>
      <a href="{_e(chapter.primary_url)}">Primary edition</a>
    </aside>
    <article class="reading-sheet">
      <p class="section-label">{_e(chapter.section)}</p>
      <h1>{_e(chapter.title)}</h1>
      <p class="mirror-note">This public mirror is not indexed. Read the <a href="{_e(chapter.primary_url)}">primary chapter on Suede SEO</a>.</p>
      <div class="chapter-body">{fragment}</div>
      <nav class="chapter-pager" aria-label="Chapter">{prev_link}{next_link}</nav>
    </article>
  </main>"""
    graph = _site_graph(publication, chapter.primary_url, chapter.title)
    graph["@graph"].append(
        {
            "@type": "Chapter",
            "@id": f"{chapter.primary_url}#chapter",
            "name": chapter.title,
            "url": chapter.primary_url,
            "isPartOf": {"@id": f"{publication.canonical_base}#book"},
            "position": chapter.ordinal,
        }
    )
    return _document(
        publication,
        title=f"{chapter.title} | {publication.title}",
        description=f"{chapter.title}, from {publication.title} by {publication.author}.",
        canonical=chapter.primary_url,
        robots="noindex,follow",
        body=body,
        body_class="chapter",
        graph=graph,
    )


def render_about(publication: Publication) -> str:
    body = f"""
  <main id="content" class="about-sheet">
    <p class="section-label">AUTHOR AND PUBLICATION</p>
    <h1>About {_e(publication.title)}</h1>
    <p>{_e(content.ABOUT_COPY)}</p>
    <p>{_e(content.ABOUT_SOURCE)}</p>
    <dl class="publication-record">
      <div><dt>Author</dt><dd>{_e(publication.author)}</dd></div>
      <div><dt>Publisher</dt><dd>{_e(publication.publisher)}</dd></div>
      <div><dt>Version</dt><dd>{_e(publication.version)}</dd></div>
      <div><dt>Published</dt><dd>{_e(publication.publication_date)}</dd></div>
    </dl>
  </main>"""
    return _document(
        publication,
        title=f"About {publication.title}",
        description=f"Author, publisher, source, and evidence record for {publication.title}.",
        canonical=f"{publication.pages_base}/about/",
        body=body,
        body_class="about",
    )


def render_downloads(publication: Publication) -> str:
    body = f"""
  <main id="content" class="downloads-sheet">
    <p class="section-label">VERSION {_e(publication.version)}</p>
    <h1>Take the book offline</h1>
    <p>The PDF and EPUB come from the same chapter source as the primary web edition.</p>
    <div class="format-list">
      <a class="format" href="{PROJECT_PATH}/downloads/THE-SCREENSHOT.pdf"><b>PDF</b><span>Print and fixed-layout reading</span></a>
      <a class="format" href="{PROJECT_PATH}/downloads/THE-SCREENSHOT.epub"><b>EPUB</b><span>Reflowable book-reader format</span></a>
    </div>
  </main>"""
    return _document(
        publication,
        title=f"Download {publication.title}",
        description=f"Download {publication.title} by {publication.author} as PDF or EPUB.",
        canonical=f"{publication.pages_base}/downloads/",
        robots="noindex,follow",
        body=body,
        body_class="downloads",
    )


def render_404(publication: Publication) -> str:
    body = f"""
  <main id="content" class="error-sheet">
    <p class="section-label">MISSING CAPTURE</p>
    <h1>This page is not in the record.</h1>
    <p>Return to the <a href="{PROJECT_PATH}/">public source edition</a> or read the <a href="{_e(publication.canonical_base)}">primary book</a>.</p>
  </main>"""
    return _document(
        publication,
        title=f"Page not found | {publication.title}",
        description="The requested book page was not found.",
        canonical=f"{publication.pages_base}/404.html",
        robots="noindex,follow",
        body=body,
        body_class="error",
    )
