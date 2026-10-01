import json
import re
import tempfile
import unittest
from pathlib import Path

from pages.build import build_site
from tools.audit_public_copy import audit_copy


ROOT = Path(__file__).resolve().parents[1]


def fake_renderer(markdown: str) -> str:
    first_line = next((line for line in markdown.splitlines() if line.strip()), "Empty")
    return f"<p>{first_line.replace('&', '&amp;').replace('<', '&lt;')}</p>"


class PagesBuildTests(unittest.TestCase):
    def test_build_separates_indexable_and_mirror_routes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = build_site(ROOT, output, renderer=fake_renderer)
            home = (result.output / "index.html").read_text(encoding="utf-8")
            chapter = (result.output / "read/the-screenshot/index.html").read_text(
                encoding="utf-8"
            )
            sitemap = (result.output / "sitemap.xml").read_text(encoding="utf-8")

        self.assertIn(
            '<link rel="canonical" href="https://jasoncolapietro.github.io/suede-geo-book/">',
            home,
        )
        self.assertNotIn('name="robots" content="noindex', home)
        self.assertIn('<meta name="robots" content="noindex,follow">', chapter)
        self.assertIn(
            '<link rel="canonical" href="https://seo.suedeai.ai/book/the-screenshot">',
            chapter,
        )
        self.assertNotIn("/read/the-screenshot/", sitemap)
        self.assertIn("https://jasoncolapietro.github.io/suede-geo-book/about/", sitemap)

    def test_build_writes_every_public_route_and_download(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = build_site(ROOT, output, renderer=fake_renderer)

            self.assertEqual(len(result.routes), 18)
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "about/index.html").is_file())
            self.assertTrue((output / "downloads/index.html").is_file())
            self.assertTrue((output / "downloads/THE-SCREENSHOT.pdf").is_file())
            self.assertTrue((output / "downloads/THE-SCREENSHOT.epub").is_file())
            self.assertTrue((output / "read/index.html").is_file())
            self.assertTrue((output / "read/front-matter/index.html").is_file())
            self.assertTrue(
                (output / "read/founders-ai-visibility-checklist/index.html").is_file()
            )
            self.assertTrue((output / "404.html").is_file())

    def test_same_input_produces_same_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = build_site(ROOT, root / "one", renderer=fake_renderer)
            second = build_site(ROOT, root / "two", renderer=fake_renderer)

        self.assertEqual(first.digest, second.digest)

    def test_manifest_contains_no_private_filesystem_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            manifest_text = (output / "book-manifest.json").read_text(encoding="utf-8")
            manifest = json.loads(manifest_text)

        self.assertNotIn(str(ROOT), manifest_text)
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(len(manifest["chapters"]), 13)
        self.assertEqual(manifest["chapters"][1]["source"], "chapters/01-the-screenshot.md")

    def test_robots_allows_mirror_crawl_for_page_level_noindex(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            robots = (output / "robots.txt").read_text(encoding="utf-8")

        self.assertEqual(robots, "User-agent: *\nAllow: /\n")
        self.assertNotIn("Disallow", robots)

    def test_every_page_carries_share_tags_author_and_privacy_links(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            pages = {
                "": output / "index.html",
                "about/": output / "about/index.html",
                "read/": output / "read/index.html",
                "downloads/": output / "downloads/index.html",
                "read/the-screenshot/": output / "read/the-screenshot/index.html",
            }
            texts = {route: path.read_text(encoding="utf-8") for route, path in pages.items()}

        base = "https://jasoncolapietro.github.io/suede-geo-book/"
        image = f"{base}assets/og-cover.png"
        for route, text in texts.items():
            with self.subTest(route=route):
                self.assertIn(f'<meta property="og:url" content="{base}{route}">', text)
                self.assertIn(f'<meta property="og:image" content="{image}">', text)
                self.assertIn('<meta property="og:image:width" content="1200">', text)
                self.assertIn('<meta property="og:image:height" content="630">', text)
                self.assertIn('<meta property="og:site_name" content="The Screenshot">', text)
                self.assertIn('property="og:title"', text)
                self.assertIn('property="og:description"', text)
                self.assertIn('property="og:image:alt"', text)
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', text)
                self.assertIn('<meta name="twitter:creator" content="@johnnysuede">', text)
                self.assertIn(f'<meta name="twitter:image" content="{image}">', text)
                self.assertIn('<a href="https://suedeai.ai/privacy">Privacy</a>', text)
                self.assertIn(
                    '<a href="https://jasoncolapietro.com/" rel="author">Jason Colapietro</a>',
                    text,
                )

        self.assertIn('<meta property="og:type" content="book">', texts[""])
        self.assertIn('<meta property="og:type" content="article">', texts["read/the-screenshot/"])
        self.assertIn('<meta property="og:type" content="website">', texts["about/"])
        self.assertIn('<p class="byline">By <a href="https://jasoncolapietro.com/"', texts[""])
        self.assertNotIn('name="robots"', texts[""])
        self.assertNotIn('name="robots"', texts["about/"])
        for route in ("read/", "downloads/", "read/the-screenshot/"):
            self.assertIn('<meta name="robots" content="noindex,follow">', texts[route])

    def test_person_schema_matches_the_canonical_entity(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            home = (output / "index.html").read_text(encoding="utf-8")

        raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', home).group(1)
        graph = json.loads(raw)["@graph"]
        person = next(node for node in graph if node["@type"] == "Person")
        book = next(node for node in graph if node["@type"] == "Book")
        self.assertEqual(
            person,
            {
                "@type": "Person",
                "@id": "https://suedeai.ai/founder#person",
                "name": "Jason Colapietro",
                "alternateName": "Johnny Suede",
                "url": "https://jasoncolapietro.com/",
                "jobTitle": "Founder and CEO, Suede AI",
                "worksFor": [
                    {"@id": "https://suedeai.ai/#organization"},
                    {"@id": "https://jcinvestmentgroup.ventures/#organization"},
                ],
                "sameAs": [
                    "https://www.wikidata.org/wiki/Q140235755",
                    "https://www.linkedin.com/in/jasoncolapietro",
                    "https://github.com/JasonColapietro",
                    "https://x.com/johnnysuede",
                    "https://www.youtube.com/@johnnysuede",
                    "https://www.crunchbase.com/person/jason-colapietro-d83e",
                    "https://www.amazon.com/stores/author/B0H3DPP75K",
                    "https://apps.apple.com/us/developer/jason-colapietro/id1895958699",
                    "https://jasoncolapietro.substack.com/",
                ],
            },
        )
        self.assertEqual(book["datePublished"], "2026-08-28")
        self.assertEqual(book["version"], "1.0.0")

    def test_share_cover_is_a_1200_by_630_png(self):
        cover = (ROOT / "pages/assets/og-cover.png").read_bytes()
        self.assertEqual(cover[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(int.from_bytes(cover[16:20], "big"), 1200)
        self.assertEqual(int.from_bytes(cover[20:24], "big"), 630)

    def test_rejects_unsafe_rendered_fragment(self):
        def unsafe_renderer(_: str) -> str:
            return '<p onclick="steal()">Unsafe</p><script>steal()</script>'

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "unsafe rendered HTML"):
                build_site(ROOT, Path(directory) / "site", renderer=unsafe_renderer)

    def test_generated_site_has_no_external_runtime_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            pages = list(output.rglob("*.html"))

            for page in pages:
                text = page.read_text(encoding="utf-8")
                self.assertIsNone(
                    re.search(
                        r'(?:src|href)="https?://[^\"]+\.(?:js|css|woff2?|ttf)',
                        text,
                    ),
                    page,
                )

    def test_generated_site_has_no_machine_residue(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build_site(ROOT, output, renderer=fake_renderer)
            findings = audit_copy([ROOT / "pages/content.py", *output.rglob("*.html")])

        self.assertEqual(findings, [])

    def test_visual_assets_are_local_licensed_and_accessible(self):
        css = (ROOT / "pages/assets/book.css").read_text(encoding="utf-8")
        javascript = (ROOT / "pages/assets/book.js").read_text(encoding="utf-8")
        fonts = ROOT / "pages/assets/fonts"

        self.assertIn("@font-face", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("@media print", css)
        self.assertNotIn("linear-gradient", css)
        self.assertNotIn("radial-gradient", css)
        self.assertNotIn("fetch(", javascript)
        self.assertNotIn("localStorage", javascript)
        for name in (
            "BarlowCondensed-SemiBold.ttf",
            "SourceSerif4-Variable.ttf",
            "IBMPlexMono-Regular.ttf",
            "OFL-Barlow.txt",
            "OFL-Source-Serif-4.txt",
            "OFL-IBM-Plex.txt",
            "SHA256SUMS",
        ):
            self.assertTrue((fonts / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
