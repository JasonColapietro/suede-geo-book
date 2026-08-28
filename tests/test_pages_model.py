import json
import shutil
import tempfile
import unittest
from pathlib import Path

from pages.model import discover_chapters, load_publication


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SOURCES = tuple(f"{number:02d}-{name}.md" for number, name in (
    (0, "front-matter"),
    (1, "the-screenshot"),
    (2, "the-quiet-migration"),
    (3, "invisible-is-the-new-page-two"),
    (4, "ranked-vs-cited"),
    (5, "compounding-absence"),
    (6, "can-the-machines-even-read-you"),
    (7, "the-six-engines"),
    (8, "extractable-or-invisible"),
    (9, "receipts-beat-claims"),
    (10, "the-founders-visibility-audit"),
    (11, "measure-like-an-operator"),
    (12, "back-matter"),
))


class PagesModelTests(unittest.TestCase):
    def setUp(self):
        self.publication = load_publication(ROOT / "pages/publication.json")

    def test_loads_stable_publication_metadata(self):
        self.assertEqual(self.publication.title, "The Screenshot")
        self.assertEqual(self.publication.author, "Jason Colapietro")
        self.assertEqual(self.publication.version, "1.0.0")
        self.assertEqual(
            self.publication.pages_base,
            "https://jasoncolapietro.github.io/suede-geo-book",
        )

    def test_rejects_missing_publication_field(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "publication.json"
            data = json.loads((ROOT / "pages/publication.json").read_text(encoding="utf-8"))
            del data["publisher"]
            target.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing publication fields: publisher"):
                load_publication(target)

    def test_discovers_the_exact_numbered_source_set(self):
        chapters = discover_chapters(ROOT / "chapters", self.publication)

        self.assertEqual(len(chapters), 13)
        self.assertEqual(tuple(chapter.source_name for chapter in chapters), EXPECTED_SOURCES)
        self.assertEqual(len({chapter.slug for chapter in chapters}), 13)
        self.assertEqual(chapters[0].slug, "front-matter")
        self.assertEqual(chapters[1].slug, "the-screenshot")
        self.assertEqual(chapters[-1].slug, "founders-ai-visibility-checklist")
        self.assertEqual(chapters[6].title, "Can the Machines Even Read You?")
        self.assertEqual(chapters[-1].title, "The Founder's AI Visibility Checklist")

    def test_maps_primary_edition_routes_explicitly(self):
        chapters = discover_chapters(ROOT / "chapters", self.publication)
        by_source = {chapter.source_name: chapter for chapter in chapters}

        self.assertEqual(by_source["00-front-matter.md"].primary_url, "https://seo.suedeai.ai/book")
        self.assertEqual(
            by_source["06-can-the-machines-even-read-you.md"].primary_url,
            "https://seo.suedeai.ai/book/can-the-machines-read-you",
        )
        self.assertEqual(
            by_source["12-back-matter.md"].primary_url,
            "https://seo.suedeai.ai/book/glossary",
        )

    def test_missing_numbered_source_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "chapters", root / "chapters")
            (root / "chapters/07-the-six-engines.md").unlink()

            with self.assertRaisesRegex(ValueError, "chapter source set mismatch"):
                discover_chapters(root / "chapters", self.publication)

    def test_extra_numbered_source_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / "chapters", root / "chapters")
            (root / "chapters/13-surprise.md").write_text("# Surprise\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "chapter source set mismatch"):
                discover_chapters(root / "chapters", self.publication)


if __name__ == "__main__":
    unittest.main()
