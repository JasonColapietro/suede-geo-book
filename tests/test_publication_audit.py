import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tools.audit_public_release import audit_tree, format_findings


class PublicationAuditTests(unittest.TestCase):
    def test_audit_rejects_private_and_machine_local_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tracked = [
                "README.md",
                ".env",
                "notes/AI_HANDOFF.md",
                "__pycache__/x.pyc",
                "docs/superpowers/plans/publication.md",
            ]
            findings = audit_tree(root, tracked)

        self.assertEqual(
            {finding.code for finding in findings},
            {
                "forbidden-path",
                "private-handoff",
                "generated-cache",
                "agent-planning",
            },
        )

    def test_audit_redacts_suspicious_assignment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "config.txt"
            target.write_text("API_KEY=super-secret-value", encoding="utf-8")
            findings = audit_tree(root, ["config.txt"])

        self.assertEqual(findings[0].code, "credential-pattern")
        self.assertNotIn("super-secret-value", findings[0].detail)

        output = io.StringIO()
        with redirect_stdout(output):
            format_findings(findings)
        self.assertNotIn("super-secret-value", output.getvalue())

    def test_known_release_binaries_are_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            exports = root / "exports"
            exports.mkdir()
            (exports / "THE-SCREENSHOT.pdf").write_bytes(b"%PDF" + b"x" * 32)
            (exports / "THE-SCREENSHOT.epub").write_bytes(b"PK" + b"x" * 32)

            findings = audit_tree(
                root,
                ["exports/THE-SCREENSHOT.pdf", "exports/THE-SCREENSHOT.epub"],
            )

        self.assertEqual(findings, [])

    def test_unexpected_large_binary_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "private.bin"
            target.write_bytes(b"\x00" * 64)
            findings = audit_tree(root, ["private.bin"])

        self.assertEqual([finding.code for finding in findings], ["binary-file"])


if __name__ == "__main__":
    unittest.main()
