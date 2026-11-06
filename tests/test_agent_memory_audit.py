"""Tests for agent-memory-audit."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/agent-memory-audit/scripts/memory_audit.py"


class AgentMemoryAuditTests(unittest.TestCase):
    def test_script_compiles(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(SCRIPT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_detects_broken_link_and_missing_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            (project / "About.md").write_text(
                "# Demo\n\n## Current state\n\n- Working.\n",
                encoding="utf-8",
            )
            (project / "notes.md").write_text(
                "[missing](./does-not-exist.md)\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertIn("broken-link", issues)
            self.assertIn("missing-status", issues)

    def test_clean_memory_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            (project / "About.md").write_text(
                "---\nstatus: active\nupdated: 2026-11-06\n---\n\n# Demo\n\n## Current state\n\n- Working.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            self.assertNotIn("critical", report["summary"])


if __name__ == "__main__":
    unittest.main()
