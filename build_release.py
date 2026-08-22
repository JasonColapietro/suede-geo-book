#!/usr/bin/env python3
"""Build and publish the master, EPUB, and PDF as one coherent release."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from build_epub import (
    BASE,
    assemble_master,
    assemble_master_text,
    build_epub_artifact,
    publish_artifact_bundle,
    release_lock,
)
from build_pdf import build_pdf_artifact, render_pdf_with_chromium


def build_release(
    base=BASE,
    run=subprocess.run,
    render=render_pdf_with_chromium,
    find_executable=shutil.which,
    replace=os.replace,
    epub_builder=build_epub_artifact,
    pdf_builder=build_pdf_artifact,
):
    """Stage every format and publish only after the complete build succeeds."""
    base = Path(base)
    with release_lock(base):
        exports = base / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        master = base / "THE-SCREENSHOT.md"
        epub = exports / "THE-SCREENSHOT.epub"
        pdf = exports / "THE-SCREENSHOT.pdf"

        with tempfile.TemporaryDirectory(prefix=".release-bundle-", dir=base) as directory:
            scratch = Path(directory)
            staged_master = scratch / "THE-SCREENSHOT.md"
            staged_epub = scratch / "THE-SCREENSHOT.epub"
            staged_pdf = scratch / "THE-SCREENSHOT.pdf"
            staged_master, chapter_count = assemble_master(base, staged_master)

            epub_builder(base, staged_master, staged_epub, run=run)
            pdf_builder(
                base,
                staged_master,
                staged_pdf,
                run=run,
                render=render,
                find_executable=find_executable,
            )

            expected_master, current_chapter_count = assemble_master_text(base)
            if current_chapter_count != chapter_count:
                raise RuntimeError("chapter source set changed during release build")
            if staged_master.read_text(encoding="utf-8") != expected_master:
                raise RuntimeError("chapter sources changed during release build")
            for label, artifact in (("EPUB", staged_epub), ("PDF", staged_pdf)):
                if not artifact.is_file() or artifact.stat().st_size == 0:
                    raise RuntimeError(f"{label} release artifact is missing or empty")

            publish_artifact_bundle(
                [
                    ("master", staged_master, master),
                    ("EPUB", staged_epub, epub),
                    ("PDF", staged_pdf, pdf),
                ],
                recovery_root=base / ".release-recovery",
                replace=replace,
                lock_base=base,
                lock_held=True,
            )

    print(f"assembled {chapter_count} files -> {master}")
    print(f"built {epub} ({epub.stat().st_size/1024:.0f} KB)")
    print(f"built {pdf} ({pdf.stat().st_size/1024:.0f} KB)")
    return master, epub, pdf


if __name__ == "__main__":
    build_release()
