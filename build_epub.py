#!/usr/bin/env python3
"""Assemble chapters/*.md into THE-SCREENSHOT.md and build the EPUB via pandoc.
Pattern borrowed from the-signal-chain-book's pipeline, single edition."""
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
import fcntl
import hashlib
import json
from contextlib import contextmanager, nullcontext
from pathlib import Path, PurePosixPath

BASE = os.path.dirname(os.path.abspath(__file__))
AUTHOR = "Jason Colapietro"
PUBLISHER = "Johnny Suede Press"
DATE = "2026"
TITLE = "THE SCREENSHOT"
SUBTITLE = "Why AI Recommends Your Competitors, and How to Fix It"
MASTER = os.path.join(BASE, "THE-SCREENSHOT.md")
EPUB = os.path.join(BASE, "exports", "THE-SCREENSHOT.epub")
IDENTIFIER = "https://seo.suedeai.ai/book"
EPUB_MODIFIED = "2026-08-21T00:00:00Z"
ZIP_TIME = (2026, 8, 21, 0, 0, 0)
CHAPTER_NAME = re.compile(r"^(\d{2})-[a-z0-9][a-z0-9-]*\.md$")
CONTAINER_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:container"
OPF_NAMESPACE = "http://www.idpf.org/2007/opf"
DC_NAMESPACE = "http://purl.org/dc/elements/1.1/"


@contextmanager
def release_lock(base):
    """Serialize a complete source snapshot, build, validation, and publication."""
    identity = str(Path(base).resolve()).encode("utf-8")
    lock_root = Path(tempfile.gettempdir()) / "suede-geo-book-release-locks"
    lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = lock_root / f"{hashlib.sha256(identity).hexdigest()}.lock"
    with lock_path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield lock_path
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def assemble_master_text(base=BASE):
    """Return the deterministic master text assembled from current chapters."""
    base = Path(base)
    chapters = []
    for path in (base / "chapters").iterdir():
        match = CHAPTER_NAME.fullmatch(path.name)
        if path.is_file() and match:
            chapters.append((int(match.group(1)), path))
    chapters.sort(key=lambda item: (item[0], item[1].name))
    if not chapters:
        raise RuntimeError("no chapters found")
    numbers = [number for number, _ in chapters]
    first_number = numbers[0]
    if first_number not in {0, 1} or numbers != list(range(first_number, first_number + len(chapters))):
        raise RuntimeError(
            "chapter filenames must use one continuous numbered sequence starting at 00 or 01"
        )
    parts = [path.read_text(encoding="utf-8").strip() for _, path in chapters]
    return "\n\n".join(parts) + "\n", len(chapters)


def assemble_master(base=BASE, destination=None):
    """Assemble chapter sources into a selected destination."""
    base = Path(base)
    text, chapter_count = assemble_master_text(base)
    master = Path(destination) if destination else base / "THE-SCREENSHOT.md"
    master.write_text(text, encoding="utf-8")
    return master, chapter_count


def normalize_epub(source_path, target_path):
    """Write a deterministic EPUB and fail if its package timestamp is absent."""
    replacement_count = 0
    with zipfile.ZipFile(source_path, "r") as source, zipfile.ZipFile(target_path, "w") as target:
        for member in source.infolist():
            payload = source.read(member)
            if member.filename == "EPUB/content.opf":
                payload, count = re.subn(
                    rb'<meta property="dcterms:modified">[^<]+</meta>',
                    f'<meta property="dcterms:modified">{EPUB_MODIFIED}</meta>'.encode(),
                    payload,
                )
                replacement_count += count
            info = zipfile.ZipInfo(member.filename, ZIP_TIME)
            info.create_system = 3
            info.external_attr = 0o644 << 16
            info.compress_type = (
                zipfile.ZIP_STORED
                if member.filename == "mimetype"
                else zipfile.ZIP_DEFLATED
            )
            target.writestr(info, payload)
    if replacement_count != 1:
        raise RuntimeError(
            "EPUB normalization expected exactly one dcterms:modified timestamp; "
            f"found {replacement_count}"
        )


def validate_epub(epub_path):
    """Validate normalized EPUB structure and deterministic metadata."""
    with zipfile.ZipFile(epub_path, "r") as archive:
        corrupt_member = archive.testzip()
        if corrupt_member:
            raise RuntimeError(f"EPUB contains a corrupt member: {corrupt_member}")
        members = archive.infolist()
        names = [member.filename for member in members]
        duplicate_names = sorted({name for name in names if names.count(name) > 1})
        if duplicate_names:
            raise RuntimeError("EPUB contains duplicate members: " + ", ".join(duplicate_names))
        required = {"mimetype", "META-INF/container.xml"}
        missing = sorted(required.difference(names))
        if missing:
            raise RuntimeError("EPUB is missing required members: " + ", ".join(missing))
        if members[0].filename != "mimetype" or members[0].compress_type != zipfile.ZIP_STORED:
            raise RuntimeError("EPUB mimetype must be the first uncompressed member")
        if archive.read(members[0]) != b"application/epub+zip":
            raise RuntimeError("EPUB mimetype payload must be exactly application/epub+zip")
        unexpected_times = [member.filename for member in members if member.date_time != ZIP_TIME]
        if unexpected_times:
            raise RuntimeError("EPUB member timestamps were not normalized")
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
        except ET.ParseError as error:
            raise RuntimeError(f"EPUB container.xml is not parseable: {error}") from error
        if container.tag != f"{{{CONTAINER_NAMESPACE}}}container":
            raise RuntimeError("EPUB container.xml has an invalid container root")
        if container.attrib.get("version") != "1.0":
            raise RuntimeError("EPUB container.xml must declare supported version 1.0")
        rootfiles_element = container.find(f"{{{CONTAINER_NAMESPACE}}}rootfiles")
        if rootfiles_element is None:
            raise RuntimeError("EPUB container.xml has no rootfiles element")
        rootfiles = [
            element.attrib.get("full-path", "").strip()
            for element in rootfiles_element.findall(f"{{{CONTAINER_NAMESPACE}}}rootfile")
            if element.tag == f"{{{CONTAINER_NAMESPACE}}}rootfile"
            and element.attrib.get("media-type") == "application/oebps-package+xml"
        ]
        rootfiles = [path for path in rootfiles if path]
        if not rootfiles:
            raise RuntimeError("EPUB container.xml has no package rootfile")
        package_path = rootfiles[0]
        package_parts = PurePosixPath(package_path).parts
        if package_path.startswith("/") or ".." in package_parts or package_path not in names:
            raise RuntimeError("EPUB container rootfile does not point to an existing package")
        metadata = archive.read(package_path)
        try:
            package = ET.fromstring(metadata)
        except ET.ParseError as error:
            raise RuntimeError(f"EPUB package document is not parseable: {error}") from error
        if package.tag != f"{{{OPF_NAMESPACE}}}package":
            raise RuntimeError("EPUB package document has an invalid package root")
        if package.attrib.get("version") != "3.0":
            raise RuntimeError("EPUB package document must declare supported version 3.0")
        package_sections = {
            element.tag.rsplit("}", 1)[-1]: element
            for element in list(package)
            if element.tag.startswith(f"{{{OPF_NAMESPACE}}}")
        }
        missing_sections = sorted({"metadata", "manifest", "spine"}.difference(package_sections))
        if missing_sections:
            raise RuntimeError(
                "EPUB package document is missing required sections: "
                + ", ".join(missing_sections)
            )
        identifier_id = package.attrib.get("unique-identifier", "").strip()
        identifier = package_sections["metadata"].find(
            f"{{{DC_NAMESPACE}}}identifier[@id='{identifier_id}']"
        ) if identifier_id else None
        if identifier is None or not (identifier.text or "").strip():
            raise RuntimeError("EPUB package document has no valid unique identifier")
        manifest_items = package_sections["manifest"].findall(f"{{{OPF_NAMESPACE}}}item")
        manifest_ids = set()
        for item in manifest_items:
            item_id = item.attrib.get("id", "").strip()
            href = item.attrib.get("href", "").strip()
            media_type = item.attrib.get("media-type", "").strip()
            if not item_id or item_id in manifest_ids or not href or not media_type:
                raise RuntimeError("EPUB package manifest contains an invalid item")
            item_path = str(PurePosixPath(package_path).parent / href)
            if href.startswith("/") or ".." in PurePosixPath(href).parts or item_path not in names:
                raise RuntimeError("EPUB package manifest points to a missing member")
            manifest_ids.add(item_id)
        if not manifest_ids:
            raise RuntimeError("EPUB package manifest contains no items")
        spine_items = package_sections["spine"].findall(f"{{{OPF_NAMESPACE}}}itemref")
        if not spine_items or any(
            not item.attrib.get("idref") or item.attrib["idref"] not in manifest_ids
            for item in spine_items
        ):
            raise RuntimeError("EPUB package spine contains an invalid manifest reference")
        expected_timestamp = (
            f'<meta property="dcterms:modified">{EPUB_MODIFIED}</meta>'.encode()
        )
        if metadata.count(expected_timestamp) != 1:
            raise RuntimeError("EPUB package timestamp validation failed")


def build_epub_artifact(base, master, output, run=subprocess.run):
    """Build one validated EPUB at a staged output path."""
    base = Path(base)
    master = Path(master)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".epub-artifact-", dir=output.parent) as directory:
        scratch = Path(directory)
        raw_epub = scratch / "THE-SCREENSHOT.raw.epub"
        normalized_epub = scratch / "THE-SCREENSHOT.normalized.epub"
        cmd = [
            "pandoc", str(master),
            "-o", str(raw_epub),
            "--from", "markdown",
            "--toc", "--toc-depth=1",
            "--split-level=1",
            "--css", str(base / "epub-book.css"),
            "--metadata", f"title={TITLE}",
            "--metadata", f"subtitle={SUBTITLE}",
            "--metadata", f"author={AUTHOR}",
            "--metadata", f"publisher={PUBLISHER}",
            "--metadata", f"identifier={IDENTIFIER}",
            "--metadata", f"date={DATE}",
            "--metadata", "lang=en-US",
        ]
        run(cmd, check=True)
        normalize_epub(raw_epub, normalized_epub)
        validate_epub(normalized_epub)
        os.replace(normalized_epub, output)
    return output


def publish_artifact_bundle(
    artifacts,
    recovery_root=None,
    replace=os.replace,
    lock_base=None,
    lock_held=False,
):
    """Publish staged files with serialized writes and durable rollback backups."""
    normalized = [(label, Path(staged), Path(final)) for label, staged, final in artifacts]
    if not normalized:
        raise RuntimeError("release bundle contains no artifacts")
    common_base = Path(os.path.commonpath([str(final.parent) for _, _, final in normalized]))
    lock_context = nullcontext() if lock_held else release_lock(lock_base or common_base)
    with lock_context:
        root = Path(recovery_root) if recovery_root else common_base / ".release-recovery"
        root.mkdir(mode=0o700, parents=True, exist_ok=True)
        recovery_dir = Path(tempfile.mkdtemp(prefix="bundle-", dir=root))
        records = []
        retain_recovery = False
        try:
            for index, (label, staged, final) in enumerate(normalized):
                if not staged.is_file() or staged.stat().st_size == 0:
                    raise RuntimeError(f"{label} staged release artifact is missing or empty")
                final.parent.mkdir(parents=True, exist_ok=True)
                existed = final.is_file()
                backup = recovery_dir / f"previous-{index}-{final.name}"
                if existed:
                    shutil.copy2(final, backup)
                records.append((label, staged, final, existed, backup))
            (recovery_dir / "manifest.json").write_text(
                json.dumps([
                    {
                        "label": label,
                        "final": str(final),
                        "existed": existed,
                        "backup": str(backup) if existed else None,
                    }
                    for label, _, final, existed, backup in records
                ], indent=2) + "\n",
                encoding="utf-8",
            )

            published = []
            try:
                for record in records:
                    _, staged, final, _, _ = record
                    replace(staged, final)
                    published.append(record)
            except Exception as publication_error:
                rollback_errors = []
                for index, (label, _, final, existed, backup) in reversed(list(enumerate(published))):
                    try:
                        if existed:
                            restore = recovery_dir / f"restore-{index}-{final.name}"
                            shutil.copy2(backup, restore)
                            replace(restore, final)
                        else:
                            final.unlink(missing_ok=True)
                    except Exception as error:
                        rollback_errors.append(f"{label} rollback failed: {error}")
                if rollback_errors:
                    retain_recovery = True
                    details = "; ".join(rollback_errors)
                    raise RuntimeError(
                        f"{details}. Last-good backups retained at {recovery_dir}"
                    ) from publication_error
                shutil.rmtree(recovery_dir)
                if root.exists() and not any(root.iterdir()):
                    root.rmdir()
                raise
        except Exception:
            if recovery_dir.exists() and not retain_recovery:
                shutil.rmtree(recovery_dir)
                if root.exists() and not any(root.iterdir()):
                    root.rmdir()
            raise
        else:
            shutil.rmtree(recovery_dir)
            if root.exists() and not any(root.iterdir()):
                root.rmdir()


def publish_epub_bundle(
    staged_master,
    staged_epub,
    master,
    epub,
    replace=os.replace,
    recovery_root=None,
    lock_base=None,
    lock_held=False,
):
    """Publish master and EPUB together, restoring both if publication fails."""
    publish_artifact_bundle(
        [
            ("master", staged_master, master),
            ("EPUB", staged_epub, epub),
        ],
        recovery_root=recovery_root,
        replace=replace,
        lock_base=lock_base,
        lock_held=lock_held,
    )


def build_epub(base=BASE, run=subprocess.run, replace=os.replace):
    """Build and publish a coherent master and EPUB bundle."""
    base = Path(base)
    master = base / "THE-SCREENSHOT.md"
    with release_lock(base):
        exports = base / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        epub = exports / "THE-SCREENSHOT.epub"

        with tempfile.TemporaryDirectory(prefix=".epub-bundle-", dir=base) as directory:
            scratch = Path(directory)
            staged_master = scratch / "THE-SCREENSHOT.md"
            staged_epub = scratch / "THE-SCREENSHOT.epub"
            staged_master, chapter_count = assemble_master(base, staged_master)
            build_epub_artifact(base, staged_master, staged_epub, run=run)
            expected_master, current_chapter_count = assemble_master_text(base)
            if current_chapter_count != chapter_count:
                raise RuntimeError("chapter source set changed during EPUB build")
            if staged_master.read_text(encoding="utf-8") != expected_master:
                raise RuntimeError("chapter sources changed during EPUB build")
            publish_epub_bundle(
                staged_master,
                staged_epub,
                master,
                epub,
                replace=replace,
                recovery_root=base / ".release-recovery",
                lock_base=base,
                lock_held=True,
            )

    print(f"assembled {chapter_count} files -> {master}")
    size = epub.stat().st_size
    print(f"built {epub} ({size/1024:.0f} KB)")
    return epub


if __name__ == "__main__":
    build_epub()
