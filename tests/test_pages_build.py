import json
import tempfile
import unittest
from pathlib import Path

from pages.build import build_site


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

    def test_rejects_unsafe_rendered_fragment(self):
        def unsafe_renderer(_: str) -> str:
            return '<p onclick="steal()">Unsafe</p><script>steal()</script>'

        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "unsafe rendered HTML"):
                build_site(ROOT, Path(directory) / "site", renderer=unsafe_renderer)


if __name__ == "__main__":
    unittest.main()
