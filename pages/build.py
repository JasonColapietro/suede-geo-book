#!/usr/bin/env python3
"""Build the deterministic GitHub Pages edition of The Screenshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pages.model import Chapter, discover_chapters, load_publication
from pages.templates import (
    render_404,
    render_about,
    render_chapter,
    render_downloads,
    render_home,
    render_read_index,
)


UNSAFE_FRAGMENT = re.compile(
    r"(?is)<\s*(?:script|iframe|object|embed)\b|\bjavascript\s*:|\bon[a-z]+\s*="
)


@dataclass(frozen=True)
class BuildResult:
    output: Path
    routes: tuple[str, ...]
    digest: str


def render_markdown(markdown: str, pandoc: str = "pandoc") -> str:
    result = subprocess.run(
        [
            pandoc,
            "--from=gfm-raw_html",
            "--to=html5",
            "--wrap=none",
            "--shift-heading-level-by=1",
        ],
        input=markdown,
        text=True,
        check=True,
        capture_output=True,
    )
    return result.stdout.strip()


def _validate_fragment(fragment: str, source_name: str) -> None:
    if UNSAFE_FRAGMENT.search(fragment):
        raise ValueError(f"unsafe rendered HTML: {source_name}")


def _write_text(root: Path, relative: str, text: str) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def _copy_artifact(source: Path, target: Path) -> None:
    if not source.is_file() or source.stat().st_size == 0:
        raise ValueError(f"release artifact missing or empty: {source.name}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        data = path.read_bytes()
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _publish_directory(stage: Path, output: Path) -> None:
    backup = output.with_name(f".{output.name}.previous")
    if backup.exists():
        shutil.rmtree(backup)
    if output.exists():
        os.replace(output, backup)
    try:
        os.replace(stage, output)
    except Exception:
        if backup.exists() and not output.exists():
            os.replace(backup, output)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def _manifest(chapters: tuple[Chapter, ...], publication_version: str) -> dict[str, object]:
    return {
        "version": publication_version,
        "chapters": [
            {
                "ordinal": chapter.ordinal,
                "slug": chapter.slug,
                "title": chapter.title,
                "source": f"chapters/{chapter.source_name}",
                "route": f"/read/{chapter.slug}/",
                "primary_url": chapter.primary_url,
                "sha256": hashlib.sha256(chapter.markdown.encode("utf-8")).hexdigest(),
            }
            for chapter in chapters
        ],
    }


def build_site(
    repo_root: Path,
    output: Path,
    renderer: Callable[[str], str] | None = None,
) -> BuildResult:
    repo_root = repo_root.resolve()
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    publication = load_publication(repo_root / "pages/publication.json")
    chapters = discover_chapters(repo_root / "chapters", publication)
    render = renderer or render_markdown
    stage = Path(tempfile.mkdtemp(prefix=f".{output.name}.stage-", dir=output.parent))
    routes: list[str] = ["/", "/about/", "/downloads/", "/read/"]

    try:
        _write_text(stage, "index.html", render_home(publication, chapters))
        _write_text(stage, "about/index.html", render_about(publication))
        _write_text(stage, "downloads/index.html", render_downloads(publication))
        _write_text(stage, "read/index.html", render_read_index(publication, chapters))
        _write_text(stage, "404.html", render_404(publication))

        for index, chapter in enumerate(chapters):
            fragment = render(chapter.markdown)
            _validate_fragment(fragment, chapter.source_name)
            previous = chapters[index - 1] if index else None
            following = chapters[index + 1] if index + 1 < len(chapters) else None
            _write_text(
                stage,
                f"read/{chapter.slug}/index.html",
                render_chapter(publication, chapter, fragment, previous, following),
            )
            routes.append(f"/read/{chapter.slug}/")

        _copy_artifact(
            repo_root / "exports/THE-SCREENSHOT.pdf",
            stage / "downloads/THE-SCREENSHOT.pdf",
        )
        _copy_artifact(
            repo_root / "exports/THE-SCREENSHOT.epub",
            stage / "downloads/THE-SCREENSHOT.epub",
        )

        assets = repo_root / "pages/assets"
        if assets.is_dir():
            shutil.copytree(assets, stage / "assets", dirs_exist_ok=True)

        sitemap_urls = [f"{publication.pages_base}/", f"{publication.pages_base}/about/"]
        sitemap = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{url}</loc></url>\n" for url in sitemap_urls)
            + "</urlset>\n"
        )
        _write_text(stage, "sitemap.xml", sitemap)
        _write_text(stage, "robots.txt", "User-agent: *\nAllow: /\n")
        _write_text(
            stage,
            "book-manifest.json",
            json.dumps(_manifest(chapters, publication.version), indent=2, ensure_ascii=False)
            + "\n",
        )
        _write_text(stage, ".nojekyll", "")

        expected = [
            "index.html",
            "about/index.html",
            "downloads/index.html",
            "read/index.html",
            "404.html",
            "sitemap.xml",
            "robots.txt",
            "book-manifest.json",
        ] + [f"read/{chapter.slug}/index.html" for chapter in chapters]
        missing = [relative for relative in expected if not (stage / relative).is_file()]
        if missing:
            raise RuntimeError(f"generated site incomplete: {', '.join(missing)}")

        digest = _tree_digest(stage)
        _publish_directory(stage, output)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise

    routes.append("/404.html")
    return BuildResult(output=output, routes=tuple(routes), digest=digest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="_site", help="site output directory")
    parser.add_argument("--pandoc", default="pandoc", help="Pandoc executable")
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    output = Path(args.output)
    if not output.is_absolute():
        output = repo_root / output
    result = build_site(
        repo_root,
        output,
        renderer=lambda markdown: render_markdown(markdown, args.pandoc),
    )
    print(f"built {len(result.routes)} routes -> {result.output}")
    print(f"digest {result.digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
