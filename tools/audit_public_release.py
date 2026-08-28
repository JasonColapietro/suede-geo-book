#!/usr/bin/env python3
"""Fail closed when a tracked file is unsafe for the public book repository."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Sequence


TEXT_SCAN_LIMIT = 2 * 1024 * 1024
ALLOWED_BINARIES = {
    "exports/THE-SCREENSHOT.pdf",
    "exports/THE-SCREENSHOT.epub",
}
SECRET_PATTERNS = (
    re.compile(
        r"(?im)^(?:export\s+)?(?:api[_-]?key|secret|token|password|private[_-]?key)\s*[:=]\s*\S+"
    ),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[opsu]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)


@dataclass(frozen=True, order=True)
class Finding:
    code: str
    path: str
    detail: str


def _path_finding(path: str) -> Finding | None:
    pure = PurePosixPath(path)
    parts = set(pure.parts)
    name = pure.name

    if path == "docs/superpowers" or path.startswith("docs/superpowers/"):
        return Finding("agent-planning", path, "agent planning material is not public")
    if name in {"AI_HANDOFF.md", "AGENTS.md", "CLAUDE.md"}:
        return Finding("private-handoff", path, "private agent handoff or instruction file")
    if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
        return Finding("generated-cache", path, "generated Python cache")
    if name == ".DS_Store" or name == ".env" or name.startswith(".env."):
        return Finding("forbidden-path", path, "machine-local or environment file")
    if ".release-recovery" in parts:
        return Finding("forbidden-path", path, "private release recovery material")
    return None


def _looks_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]


def audit_tree(root: Path, tracked_paths: Sequence[str]) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []

    for relative in sorted(set(tracked_paths)):
        normalized = PurePosixPath(relative).as_posix()
        path_finding = _path_finding(normalized)
        if path_finding is not None:
            findings.append(path_finding)
            continue

        target = (root / normalized).resolve()
        try:
            target.relative_to(root)
        except ValueError:
            findings.append(Finding("path-escape", normalized, "tracked path escapes repository"))
            continue

        if not target.is_file():
            continue

        data = target.read_bytes()
        if normalized in ALLOWED_BINARIES:
            continue
        if _looks_binary(data):
            findings.append(Finding("binary-file", normalized, "unexpected binary file"))
            continue
        if len(data) > TEXT_SCAN_LIMIT:
            findings.append(Finding("oversized-file", normalized, "text file exceeds 2 MiB"))
            continue

        text = data.decode("utf-8", errors="replace")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(
                Finding("credential-pattern", normalized, "credential-like assignment redacted")
            )

    return sorted(findings)


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\x00") if item]


def format_findings(findings: Sequence[Finding]) -> None:
    for finding in findings:
        print(f"{finding.code}: {finding.path} ({finding.detail})")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = audit_tree(root, tracked_paths(root))
    if findings:
        format_findings(findings)
        print(f"publication audit: {len(findings)} finding(s)")
        return 1
    print("publication audit: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
