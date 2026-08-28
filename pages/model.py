"""Publication metadata and canonical chapter discovery."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


EXPECTED_SOURCES = (
    "00-front-matter.md",
    "01-the-screenshot.md",
    "02-the-quiet-migration.md",
    "03-invisible-is-the-new-page-two.md",
    "04-ranked-vs-cited.md",
    "05-compounding-absence.md",
    "06-can-the-machines-even-read-you.md",
    "07-the-six-engines.md",
    "08-extractable-or-invisible.md",
    "09-receipts-beat-claims.md",
    "10-the-founders-visibility-audit.md",
    "11-measure-like-an-operator.md",
    "12-back-matter.md",
)

SLUGS = {
    "00-front-matter.md": "front-matter",
    "12-back-matter.md": "founders-ai-visibility-checklist",
}

PRIMARY_SLUGS = {
    "00-front-matter.md": "",
    "06-can-the-machines-even-read-you.md": "can-the-machines-read-you",
    "12-back-matter.md": "glossary",
}

HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
NUMBERED_TITLE = re.compile(r"^(?:Chapter\s+\d+|Appendix\s+[A-Z]):\s*(.+)$")


@dataclass(frozen=True)
class Publication:
    title: str
    subtitle: str
    author: str
    publisher: str
    canonical_base: str
    repository_base: str
    pages_base: str
    publication_date: str
    version: str


@dataclass(frozen=True)
class Chapter:
    source_name: str
    slug: str
    title: str
    section: str
    ordinal: int
    markdown: str
    primary_url: str


def _require_https(label: str, value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"{label} must be an absolute HTTPS URL")


def load_publication(path: Path) -> Publication:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = tuple(Publication.__dataclass_fields__)
    missing = sorted(field for field in required if not data.get(field))
    if missing:
        raise ValueError(f"missing publication fields: {', '.join(missing)}")
    extras = sorted(set(data) - set(required))
    if extras:
        raise ValueError(f"unknown publication fields: {', '.join(extras)}")

    publication = Publication(**{field: str(data[field]).strip() for field in required})
    _require_https("canonical_base", publication.canonical_base)
    _require_https("repository_base", publication.repository_base)
    _require_https("pages_base", publication.pages_base)
    return publication


def _chapter_title(markdown: str, source_name: str) -> str:
    headings = HEADING.findall(markdown)
    if not headings:
        raise ValueError(f"chapter heading missing: {source_name}")
    for heading in headings:
        match = NUMBERED_TITLE.match(heading)
        if match:
            return match.group(1).strip()
    return headings[0].strip()


def _section(ordinal: int) -> str:
    if ordinal == 0:
        return "Front matter"
    if 1 <= ordinal <= 5:
        return "Part I: The Stakes"
    if 6 <= ordinal <= 10:
        return "Part II: The Fix"
    if ordinal == 11:
        return "The Close"
    return "Appendices"


def _slug(source_name: str) -> str:
    if source_name in SLUGS:
        return SLUGS[source_name]
    return source_name[3:-3]


def _primary_url(source_name: str, slug: str, publication: Publication) -> str:
    primary_slug = PRIMARY_SLUGS.get(source_name, slug)
    if not primary_slug:
        return publication.canonical_base
    return f"{publication.canonical_base}/{primary_slug}"


def discover_chapters(chapters_root: Path, publication: Publication) -> tuple[Chapter, ...]:
    root = chapters_root.resolve()
    if not root.is_dir():
        raise ValueError(f"chapter directory missing: {chapters_root}")

    actual = tuple(sorted(path.name for path in root.glob("[0-9][0-9]-*.md")))
    if actual != EXPECTED_SOURCES:
        missing = sorted(set(EXPECTED_SOURCES) - set(actual))
        extra = sorted(set(actual) - set(EXPECTED_SOURCES))
        raise ValueError(
            "chapter source set mismatch"
            f"; missing={','.join(missing) or 'none'}"
            f"; extra={','.join(extra) or 'none'}"
        )

    chapters: list[Chapter] = []
    seen_slugs: set[str] = set()
    for ordinal, source_name in enumerate(EXPECTED_SOURCES):
        source = root / source_name
        if source.is_symlink() or source.resolve().parent != root:
            raise ValueError(f"chapter path is not a regular in-repository file: {source_name}")
        markdown = source.read_text(encoding="utf-8")
        slug = _slug(source_name)
        if slug in seen_slugs:
            raise ValueError(f"duplicate chapter slug: {slug}")
        seen_slugs.add(slug)
        chapters.append(
            Chapter(
                source_name=source_name,
                slug=slug,
                title=_chapter_title(markdown, source_name),
                section=_section(ordinal),
                ordinal=ordinal,
                markdown=markdown,
                primary_url=_primary_url(source_name, slug, publication),
            )
        )
    return tuple(chapters)
