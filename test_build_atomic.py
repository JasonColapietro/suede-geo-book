#!/usr/bin/env python3
"""Focused regression tests for deterministic, atomic book builds."""

import tempfile
import unittest
import zipfile
import importlib
import multiprocessing
import time
from pathlib import Path
from subprocess import CalledProcessError

import build_epub
import build_pdf


CONTAINER_XML = """<?xml version="1.0"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="EPUB/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""


def run_locked_release_worker(root_value, edition, entered_value, gate_value, wait_for_gate):
    """Spawn-safe helper proving the release lock covers the build itself."""
    release = importlib.import_module("build_release")
    root = Path(root_value)
    entered = Path(entered_value)
    gate = Path(gate_value)

    def stage_epub(base, master, output, run):
        entered.write_text(edition, encoding="utf-8")
        if wait_for_gate:
            deadline = time.monotonic() + 10
            while not gate.exists():
                if time.monotonic() > deadline:
                    raise RuntimeError("release-lock test gate timed out")
                time.sleep(0.01)
        Path(output).write_bytes(edition.encode("utf-8"))

    def stage_pdf(base, master, output, run, render, find_executable):
        Path(output).write_bytes(edition.encode("utf-8"))

    release.build_release(root, epub_builder=stage_epub, pdf_builder=stage_pdf)


def run_locked_pdf_worker(root_value, entered_value):
    """Spawn-safe helper proving standalone PDF publication shares the release lock."""
    root = Path(root_value)
    entered = Path(entered_value)
    valid_qdf = (
        b"<< /CreationDate (D:20260821010101+00'00') "
        b"/ModDate (D:20260821010101+00'00') "
        b"/ID [<0123456789ABCDEF><FEDCBA9876543210>] >>"
    )

    def run(command, check, **kwargs):
        entered.write_text("pdf", encoding="utf-8")
        if command[0] == "pandoc":
            Path(command[command.index("-o") + 1]).write_text("<html></html>", encoding="utf-8")
        elif "--qdf" in command:
            Path(command[-1]).write_bytes(valid_qdf)
        elif "--static-id" in command:
            Path(command[-1]).write_bytes(Path(command[-2]).read_bytes())

    def render(html_path, pdf_path, run):
        Path(pdf_path).write_bytes(b"raw-pdf")

    build_pdf.build_pdf(
        root,
        run=run,
        render=render,
        find_executable=lambda name: "/test/bin/qpdf" if name == "qpdf" else None,
    )


def write_minimal_epub(path, timestamp="2099-01-02T03:04:05Z", mimetype="application/epub+zip", container=CONTAINER_XML, include_opf=True):
    with zipfile.ZipFile(path, "w") as archive:
        def write_member(name, payload):
            info = zipfile.ZipInfo(name, build_epub.ZIP_TIME)
            info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
            archive.writestr(info, payload)

        write_member("mimetype", mimetype)
        if container is not None:
            write_member("META-INF/container.xml", container)
        if include_opf:
            write_member(
                "EPUB/content.opf",
                f'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">'
                f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:test</dc:identifier>'
                f'<meta property="dcterms:modified">{timestamp}</meta></metadata>'
                f'<manifest><item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/></manifest>'
                f'<spine><itemref idref="chapter"/></spine></package>',
            )
            write_member("EPUB/chapter.xhtml", "<html xmlns=\"http://www.w3.org/1999/xhtml\"><body/></html>")


def append_normalized_member(path, name, payload):
    with zipfile.ZipFile(path, "a") as archive:
        info = zipfile.ZipInfo(name, build_epub.ZIP_TIME)
        info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
        archive.writestr(info, payload)


class EpubNormalizationTests(unittest.TestCase):
    def test_normalization_rewrites_timestamp_and_zip_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.epub"
            target = root / "target.epub"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("mimetype", "application/epub+zip")
                archive.writestr(
                    "EPUB/content.opf",
                    '<meta property="dcterms:modified">2099-01-02T03:04:05Z</meta>',
                )

            build_epub.normalize_epub(source, target)

            with zipfile.ZipFile(target) as archive:
                metadata = archive.read("EPUB/content.opf").decode()
                members = archive.infolist()
            self.assertIn(build_epub.EPUB_MODIFIED, metadata)
            self.assertNotIn("2099-01-02T03:04:05Z", metadata)
            self.assertEqual(
                [member.date_time for member in members],
                [build_epub.ZIP_TIME] * len(members),
            )
            self.assertEqual(members[0].filename, "mimetype")
            self.assertEqual(members[0].compress_type, zipfile.ZIP_STORED)

    def test_normalization_rejects_epub_without_package_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.epub"
            target = root / "target.epub"
            with zipfile.ZipFile(source, "w") as archive:
                archive.writestr("mimetype", "application/epub+zip")
                archive.writestr("EPUB/content.opf", "<package />")

            with self.assertRaisesRegex(RuntimeError, "found 0"):
                build_epub.normalize_epub(source, target)

    def test_validation_requires_the_exact_epub_mimetype_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            epub = Path(directory) / "invalid-mimetype.epub"
            write_minimal_epub(epub, timestamp=build_epub.EPUB_MODIFIED, mimetype="not-an-epub")

            with self.assertRaisesRegex(RuntimeError, "mimetype payload"):
                build_epub.validate_epub(epub)

    def test_validation_requires_a_parseable_container_with_an_existing_opf(self):
        cases = {
            "missing container": {"container": None, "message": "required members"},
            "malformed container": {"container": "<container>", "message": "not parseable"},
            "missing package": {
                "container": CONTAINER_XML.replace("EPUB/content.opf", "EPUB/missing.opf"),
                "message": "existing package",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, case in cases.items():
                with self.subTest(name=name):
                    epub = root / f"{name.replace(' ', '-')}.epub"
                    write_minimal_epub(
                        epub,
                        timestamp=build_epub.EPUB_MODIFIED,
                        container=case["container"],
                    )
                    with self.assertRaisesRegex(RuntimeError, case["message"]):
                        build_epub.validate_epub(epub)

            valid = root / "valid.epub"
            write_minimal_epub(valid, timestamp=build_epub.EPUB_MODIFIED)
            build_epub.validate_epub(valid)

    def test_validation_rejects_wrong_container_and_package_structures(self):
        cases = {
            "wrong container root": {
                "container": CONTAINER_XML.replace("<container ", "<definitely-not-a-container ")
                    .replace("</container>", "</definitely-not-a-container>"),
                "message": "invalid container root",
            },
            "unsupported container version": {
                "container": CONTAINER_XML.replace('version="1.0"', 'version="2.0"'),
                "message": "supported version 1.0",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, case in cases.items():
                with self.subTest(name=name):
                    epub = root / f"{name.replace(' ', '-')}.epub"
                    write_minimal_epub(
                        epub,
                        timestamp=build_epub.EPUB_MODIFIED,
                        container=case["container"],
                    )
                    with self.assertRaisesRegex(RuntimeError, case["message"]):
                        build_epub.validate_epub(epub)

            wrong_root = root / "wrong-package-root.epub"
            write_minimal_epub(wrong_root, timestamp=build_epub.EPUB_MODIFIED)
            with zipfile.ZipFile(wrong_root, "w") as archive:
                def write(name, payload):
                    info = zipfile.ZipInfo(name, build_epub.ZIP_TIME)
                    info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
                    archive.writestr(info, payload)
                write("mimetype", "application/epub+zip")
                write("META-INF/container.xml", CONTAINER_XML)
                write(
                    "EPUB/content.opf",
                    f'<not-package><metadata><meta property="dcterms:modified">{build_epub.EPUB_MODIFIED}</meta></metadata><manifest/><spine/></not-package>',
                )
            with self.assertRaisesRegex(RuntimeError, "invalid package root"):
                build_epub.validate_epub(wrong_root)

            missing_spine = root / "missing-spine.epub"
            write_minimal_epub(missing_spine, timestamp=build_epub.EPUB_MODIFIED)
            with zipfile.ZipFile(missing_spine, "w") as archive:
                def write(name, payload):
                    info = zipfile.ZipInfo(name, build_epub.ZIP_TIME)
                    info.compress_type = zipfile.ZIP_STORED if name == "mimetype" else zipfile.ZIP_DEFLATED
                    archive.writestr(info, payload)
                write("mimetype", "application/epub+zip")
                write("META-INF/container.xml", CONTAINER_XML)
                write(
                    "EPUB/content.opf",
                    f'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">'
                    f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:test</dc:identifier>'
                    f'<meta property="dcterms:modified">{build_epub.EPUB_MODIFIED}</meta></metadata>'
                    f'<manifest><item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/></manifest></package>',
                )
            with self.assertRaisesRegex(RuntimeError, "missing required sections: spine"):
                build_epub.validate_epub(missing_spine)

    def test_validation_rejects_duplicate_structural_members(self):
        payloads = {
            "mimetype": "application/epub+zip",
            "META-INF/container.xml": CONTAINER_XML,
            "EPUB/content.opf": (
                f'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">'
                f'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="book-id">urn:test</dc:identifier>'
                f'<meta property="dcterms:modified">{build_epub.EPUB_MODIFIED}</meta></metadata>'
                f'<manifest><item id="chapter" href="chapter.xhtml" media-type="application/xhtml+xml"/></manifest>'
                f'<spine><itemref idref="chapter"/></spine></package>'
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, payload in payloads.items():
                with self.subTest(name=name):
                    epub = root / f"duplicate-{name.replace('/', '-')}.epub"
                    write_minimal_epub(epub, timestamp=build_epub.EPUB_MODIFIED)
                    append_normalized_member(epub, name, payload)
                    with self.assertRaisesRegex(RuntimeError, "duplicate members"):
                        build_epub.validate_epub(epub)


class AtomicEpubBuildTests(unittest.TestCase):
    def make_book(self, root):
        (root / "chapters").mkdir()
        (root / "chapters" / "01-test.md").write_text("# Test\n", encoding="utf-8")
        (root / "epub-book.css").write_text("body {}\n", encoding="utf-8")
        (root / "THE-SCREENSHOT.md").write_bytes(b"last-good-master\n")
        exports = root / "exports"
        exports.mkdir()
        final = exports / "THE-SCREENSHOT.epub"
        final.write_bytes(b"last-good-epub")
        return final

    def test_master_assembly_excludes_hidden_and_unnumbered_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "00-front.md").write_text("# Front\n", encoding="utf-8")
            (chapters / "01-main.md").write_text("# Main\n", encoding="utf-8")
            (chapters / ".draft.md").write_text("# Hidden draft\n", encoding="utf-8")
            (chapters / "notes.md").write_text("# Notes\n", encoding="utf-8")

            master, count = build_epub.assemble_master_text(root)

            self.assertEqual(count, 2)
            self.assertEqual(master, "# Front\n\n# Main\n")

    def test_master_assembly_rejects_a_numbering_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapters = root / "chapters"
            chapters.mkdir()
            (chapters / "00-front.md").write_text("# Front\n", encoding="utf-8")
            (chapters / "02-gap.md").write_text("# Gap\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "continuous numbered sequence"):
                build_epub.assemble_master_text(root)

    def test_failed_pandoc_preserves_last_good_epub(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def fail_pandoc(command, check):
                Path(command[command.index("-o") + 1]).write_bytes(b"partial-epub")
                raise CalledProcessError(1, command)

            with self.assertRaises(CalledProcessError):
                build_epub.build_epub(root, run=fail_pandoc)
            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(final.read_bytes(), b"last-good-epub")

    def test_failed_normalization_preserves_last_good_epub(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def write_epub_without_timestamp(command, check):
                output = Path(command[command.index("-o") + 1])
                with zipfile.ZipFile(output, "w") as archive:
                    archive.writestr("mimetype", "application/epub+zip")
                    archive.writestr("EPUB/content.opf", "<package />")

            with self.assertRaisesRegex(RuntimeError, "found 0"):
                build_epub.build_epub(root, run=write_epub_without_timestamp)
            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(final.read_bytes(), b"last-good-epub")

    def test_successful_build_replaces_epub_only_after_normalization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def write_epub(command, check):
                output = Path(command[command.index("-o") + 1])
                write_minimal_epub(output)

            built = build_epub.build_epub(root, run=write_epub)

            self.assertEqual(built, final)
            with zipfile.ZipFile(final) as archive:
                metadata = archive.read("EPUB/content.opf")
            self.assertIn(build_epub.EPUB_MODIFIED.encode(), metadata)
            self.assertNotEqual(final.read_bytes(), b"last-good-epub")
            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_text(encoding="utf-8"),
                "# Test\n",
            )

    def test_chapter_change_during_build_preserves_the_prior_master_and_epub(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def write_epub_then_change_source(command, check):
                output = Path(command[command.index("-o") + 1])
                write_minimal_epub(output)
                (root / "chapters" / "01-test.md").write_text("# After\n", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "chapter sources changed"):
                build_epub.build_epub(root, run=write_epub_then_change_source)

            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(final.read_bytes(), b"last-good-epub")

    def test_failed_bundle_publication_rolls_master_and_epub_back_together(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def write_epub(command, check):
                output = Path(command[command.index("-o") + 1])
                write_minimal_epub(output)

            failed = False

            def fail_epub_publication_once(source, destination):
                nonlocal failed
                if Path(destination) == final and not failed:
                    failed = True
                    raise OSError("simulated EPUB publication failure")
                return Path(source).replace(destination)

            with self.assertRaisesRegex(OSError, "publication failure"):
                build_epub.build_epub(
                    root,
                    run=write_epub,
                    replace=fail_epub_publication_once,
                )

            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(final.read_bytes(), b"last-good-epub")


class PdfNormalizationTests(unittest.TestCase):
    def test_normalization_rewrites_both_timestamps_and_removes_id(self):
        source = (
            b"<< /CreationDate (D:20990102030405+00'00') "
            b"/ModDate (D:20990102030405+00'00') "
            b"/ID [ <0123456789ABCDEF> <FEDCBA9876543210> ] >>"
        )

        normalized = build_pdf.normalize_pdf_payload(source)

        self.assertEqual(normalized.count(build_pdf.PDF_DATE), 2)
        self.assertNotIn(b"D:20990102030405", normalized)
        self.assertNotIn(b"/ID", normalized)

    def test_normalization_rejects_missing_required_fields(self):
        samples = {
            "CreationDate": (
                b"<< /ModDate (D:20990102030405+00'00') "
                b"/ID [ <01> <02> ] >>"
            ),
            "ModDate": (
                b"<< /CreationDate (D:20990102030405+00'00') "
                b"/ID [ <01> <02> ] >>"
            ),
            "ID": (
                b"<< /CreationDate (D:20990102030405+00'00') "
                b"/ModDate (D:20990102030405+00'00') >>"
            ),
        }
        for field, payload in samples.items():
            with self.subTest(field=field):
                with self.assertRaisesRegex(RuntimeError, field):
                    build_pdf.normalize_pdf_payload(payload)


class AtomicPdfBuildTests(unittest.TestCase):
    VALID_QDF = (
        b"<< /CreationDate (D:20990102030405+00'00') "
        b"/ModDate (D:20990102030405+00'00') "
        b"/ID [ <0123456789ABCDEF> <FEDCBA9876543210> ] >>"
    )

    def make_book(self, root):
        chapters = root / "chapters"
        chapters.mkdir()
        (chapters / "01-test.md").write_text("# Test\n", encoding="utf-8")
        (root / "THE-SCREENSHOT.md").write_text("# Test\n", encoding="utf-8")
        exports = root / "exports"
        exports.mkdir()
        final = exports / "THE-SCREENSHOT.pdf"
        final.write_bytes(b"last-good-pdf")
        return final

    def test_stale_master_is_rejected_before_external_tools_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)
            (root / "THE-SCREENSHOT.md").write_text("# Stale\n", encoding="utf-8")

            def unexpected_run(command, check, **kwargs):
                raise AssertionError(f"external tool ran for stale master: {command}")

            with self.assertRaisesRegex(RuntimeError, "stale"):
                build_pdf.build_pdf(
                    root,
                    run=unexpected_run,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    @staticmethod
    def qpdf_locator(name):
        return "/test/bin/qpdf" if name == "qpdf" else None

    @staticmethod
    def write_raw_pdf(html_path, pdf_path, run):
        Path(pdf_path).write_bytes(b"raw-pdf")

    def test_failed_pandoc_preserves_last_good_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def fail_pandoc(command, check, **kwargs):
                raise CalledProcessError(1, command)

            with self.assertRaises(CalledProcessError):
                build_pdf.build_pdf(
                    root,
                    run=fail_pandoc,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    def test_failed_chromium_preserves_last_good_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def accept_pandoc(command, check, **kwargs):
                return None

            def fail_chromium(html_path, pdf_path, run):
                Path(pdf_path).write_bytes(b"partial-pdf")
                raise RuntimeError("chromium failed")

            with self.assertRaisesRegex(RuntimeError, "chromium failed"):
                build_pdf.build_pdf(
                    root,
                    run=accept_pandoc,
                    render=fail_chromium,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    def test_failed_qpdf_preserves_last_good_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def fail_qpdf(command, check, **kwargs):
                if command[0] == "/test/bin/qpdf":
                    raise CalledProcessError(1, command)

            with self.assertRaises(CalledProcessError):
                build_pdf.build_pdf(
                    root,
                    run=fail_qpdf,
                    render=self.write_raw_pdf,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    def test_failed_normalization_preserves_last_good_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def write_qdf_without_fields(command, check, **kwargs):
                if "--qdf" in command:
                    Path(command[-1]).write_bytes(b"<< /Type /Catalog >>")

            with self.assertRaisesRegex(RuntimeError, "CreationDate"):
                build_pdf.build_pdf(
                    root,
                    run=write_qdf_without_fields,
                    render=self.write_raw_pdf,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    def test_failed_final_qpdf_pass_preserves_last_good_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def fail_final_qpdf_pass(command, check, **kwargs):
                if "--qdf" in command:
                    Path(command[-1]).write_bytes(self.VALID_QDF)
                elif "--static-id" in command:
                    Path(command[-1]).write_bytes(b"partial-normalized-pdf")
                    raise CalledProcessError(1, command)

            with self.assertRaises(CalledProcessError):
                build_pdf.build_pdf(
                    root,
                    run=fail_final_qpdf_pass,
                    render=self.write_raw_pdf,
                    find_executable=self.qpdf_locator,
                )
            self.assertEqual(final.read_bytes(), b"last-good-pdf")

    def test_successful_build_replaces_pdf_only_after_normalization(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            final = self.make_book(root)

            def complete_qpdf_pipeline(command, check, **kwargs):
                if "--qdf" in command:
                    Path(command[-1]).write_bytes(self.VALID_QDF)
                elif "--static-id" in command:
                    Path(command[-1]).write_bytes(Path(command[-2]).read_bytes())

            built = build_pdf.build_pdf(
                root,
                run=complete_qpdf_pipeline,
                render=self.write_raw_pdf,
                find_executable=self.qpdf_locator,
            )

            self.assertEqual(built, final)
            payload = final.read_bytes()
            self.assertEqual(payload.count(build_pdf.PDF_DATE), 2)
            self.assertNotIn(b"/ID", payload)
            self.assertNotEqual(payload, b"last-good-pdf")


class AtomicAllFormatReleaseTests(unittest.TestCase):
    def make_release(self, root):
        chapters = root / "chapters"
        chapters.mkdir()
        (chapters / "01-test.md").write_text("# Current\n", encoding="utf-8")
        (root / "epub-book.css").write_text("body {}\n", encoding="utf-8")
        (root / "THE-SCREENSHOT.md").write_bytes(b"last-good-master\n")
        exports = root / "exports"
        exports.mkdir()
        epub = exports / "THE-SCREENSHOT.epub"
        pdf = exports / "THE-SCREENSHOT.pdf"
        epub.write_bytes(b"last-good-epub")
        pdf.write_bytes(b"last-good-pdf")
        return epub, pdf

    def test_late_pdf_failure_preserves_the_prior_three_file_release(self):
        release = importlib.import_module("build_release")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epub, pdf = self.make_release(root)

            def stage_epub(base, master, output, run):
                Path(output).write_bytes(b"new-normalized-epub")

            def fail_pdf(base, master, output, run, render, find_executable):
                Path(output).write_bytes(b"partial-new-pdf")
                raise RuntimeError("simulated late PDF failure")

            with self.assertRaisesRegex(RuntimeError, "late PDF failure"):
                release.build_release(
                    root,
                    epub_builder=stage_epub,
                    pdf_builder=fail_pdf,
                )

            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(epub.read_bytes(), b"last-good-epub")
            self.assertEqual(pdf.read_bytes(), b"last-good-pdf")

    def test_failed_final_file_publication_rolls_all_formats_back(self):
        release = importlib.import_module("build_release")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epub, pdf = self.make_release(root)

            def stage_epub(base, master, output, run):
                Path(output).write_bytes(b"new-normalized-epub")

            def stage_pdf(base, master, output, run, render, find_executable):
                Path(output).write_bytes(b"new-normalized-pdf")

            failed = False

            def fail_pdf_publication_once(source, destination):
                nonlocal failed
                if Path(destination) == pdf and not failed:
                    failed = True
                    raise OSError("simulated PDF publication failure")
                return Path(source).replace(destination)

            with self.assertRaisesRegex(OSError, "PDF publication failure"):
                release.build_release(
                    root,
                    epub_builder=stage_epub,
                    pdf_builder=stage_pdf,
                    replace=fail_pdf_publication_once,
                )

            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_bytes(),
                b"last-good-master\n",
            )
            self.assertEqual(epub.read_bytes(), b"last-good-epub")
            self.assertEqual(pdf.read_bytes(), b"last-good-pdf")

    def test_rollback_failure_retains_a_durable_complete_last_good_bundle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epub, pdf = self.make_release(root)
            master = root / "THE-SCREENSHOT.md"
            recovery_root = root / ".release-recovery"
            retained = None

            with tempfile.TemporaryDirectory(prefix="ephemeral-stage-") as stage_value:
                stage = Path(stage_value)
                staged_master = stage / "THE-SCREENSHOT.md"
                staged_epub = stage / "THE-SCREENSHOT.epub"
                staged_pdf = stage / "THE-SCREENSHOT.pdf"
                staged_master.write_bytes(b"new-master")
                staged_epub.write_bytes(b"new-epub")
                staged_pdf.write_bytes(b"new-pdf")
                publication_failed = False

                def fail_publish_and_epub_rollback(source, destination):
                    nonlocal publication_failed
                    source = Path(source)
                    destination = Path(destination)
                    if destination == pdf and source == staged_pdf:
                        publication_failed = True
                        raise OSError("simulated PDF publication failure")
                    if (publication_failed and destination == epub
                            and source.name.startswith("restore-")):
                        raise OSError("simulated EPUB rollback failure")
                    return source.replace(destination)

                with self.assertRaisesRegex(RuntimeError, "Last-good backups retained at") as caught:
                    build_epub.publish_artifact_bundle(
                        [
                            ("master", staged_master, master),
                            ("EPUB", staged_epub, epub),
                            ("PDF", staged_pdf, pdf),
                        ],
                        recovery_root=recovery_root,
                        replace=fail_publish_and_epub_rollback,
                        lock_base=root,
                    )
                retained = Path(str(caught.exception).split("retained at ", 1)[1])

            self.assertTrue(retained.is_dir())
            self.assertEqual((retained / "previous-0-THE-SCREENSHOT.md").read_bytes(), b"last-good-master\n")
            self.assertEqual((retained / "previous-1-THE-SCREENSHOT.epub").read_bytes(), b"last-good-epub")
            self.assertEqual((retained / "previous-2-THE-SCREENSHOT.pdf").read_bytes(), b"last-good-pdf")
            self.assertTrue((retained / "manifest.json").is_file())
            self.assertEqual(master.read_bytes(), b"last-good-master\n")
            self.assertEqual(epub.read_bytes(), b"new-epub")
            self.assertEqual(pdf.read_bytes(), b"last-good-pdf")

    def test_cross_process_lock_serializes_the_complete_release_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epub, pdf = self.make_release(root)
            entered_a = root / "entered-a"
            entered_b = root / "entered-b"
            release_a = root / "release-a"
            context = multiprocessing.get_context("spawn")
            first = context.Process(
                target=run_locked_release_worker,
                args=(str(root), "A", str(entered_a), str(release_a), True),
            )
            second = context.Process(
                target=run_locked_release_worker,
                args=(str(root), "B", str(entered_b), str(root / "unused"), False),
            )
            first.start()
            deadline = time.monotonic() + 10
            while not entered_a.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(entered_a.exists(), "first release never entered its locked build")
            second.start()
            time.sleep(0.25)
            self.assertFalse(entered_b.exists(), "second release entered while the first held the lock")
            release_a.write_text("continue", encoding="utf-8")
            first.join(10)
            second.join(10)
            if first.is_alive():
                first.terminate()
            if second.is_alive():
                second.terminate()
            self.assertEqual(first.exitcode, 0)
            self.assertEqual(second.exitcode, 0)
            self.assertTrue(entered_b.exists())
            self.assertEqual(epub.read_bytes(), b"B")
            self.assertEqual(pdf.read_bytes(), b"B")
            self.assertFalse((root / ".release-recovery").exists())

    def test_standalone_pdf_waits_for_an_inflight_all_format_release(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root)
            entered_release = root / "entered-release"
            entered_pdf = root / "entered-pdf"
            release_gate = root / "release-gate"
            context = multiprocessing.get_context("spawn")
            release_process = context.Process(
                target=run_locked_release_worker,
                args=(str(root), "release", str(entered_release), str(release_gate), True),
            )
            pdf_process = context.Process(
                target=run_locked_pdf_worker,
                args=(str(root), str(entered_pdf)),
            )
            release_process.start()
            deadline = time.monotonic() + 10
            while not entered_release.exists() and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(entered_release.exists(), "release never entered its locked build")
            pdf_process.start()
            time.sleep(0.25)
            self.assertFalse(entered_pdf.exists(), "standalone PDF entered while the release held the lock")
            release_gate.write_text("continue", encoding="utf-8")
            release_process.join(10)
            pdf_process.join(10)
            if release_process.is_alive():
                release_process.terminate()
            if pdf_process.is_alive():
                pdf_process.terminate()
            self.assertEqual(release_process.exitcode, 0)
            self.assertEqual(pdf_process.exitcode, 0)
            self.assertTrue(entered_pdf.exists())

    def test_successful_release_publishes_all_three_staged_formats(self):
        release = importlib.import_module("build_release")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            epub, pdf = self.make_release(root)

            def stage_epub(base, master, output, run):
                Path(output).write_bytes(b"new-normalized-epub")

            def stage_pdf(base, master, output, run, render, find_executable):
                Path(output).write_bytes(b"new-normalized-pdf")

            release.build_release(
                root,
                epub_builder=stage_epub,
                pdf_builder=stage_pdf,
            )

            self.assertEqual(
                (root / "THE-SCREENSHOT.md").read_text(encoding="utf-8"),
                "# Current\n",
            )
            self.assertEqual(epub.read_bytes(), b"new-normalized-epub")
            self.assertEqual(pdf.read_bytes(), b"new-normalized-pdf")
            self.assertFalse((root / ".release-recovery").exists())


if __name__ == "__main__":
    unittest.main()
