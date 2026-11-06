"""Tests for agent-memory-audit."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest
from datetime import date, timedelta

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

    def test_valid_link_is_not_broken(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            (project / "About.md").write_text(
                "---\nstatus: active\nupdated: 2026-11-06\n---\n\n# Demo\n\n## Current state\n\n- See [notes](./notes.md).\n",
                encoding="utf-8",
            )
            (project / "notes.md").write_text("# Notes\n", encoding="utf-8")

            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertNotIn("broken-link", issues)

    def test_detects_invalid_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            (project / "About.md").write_text(
                "---\nstatus: active\nupdated: not-a-date\n---\n\n# Demo\n\n## Current state\n\n- Working.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertIn("invalid-date", issues)

    def test_detects_stale_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            stale_date = (date.today() - timedelta(days=91)).isoformat()
            (project / "About.md").write_text(
                f"---\nstatus: active\nupdated: {stale_date}\n---\n\n# Demo\n\n## Current state\n\n- Working.\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertIn("stale-file", issues)

    def test_detects_duplicate_decision(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            decision = "- 2026-11-06: Use PostgreSQL for the customer database."
            (project / "decisions-a.md").write_text(decision + "\n", encoding="utf-8")
            (project / "decisions-b.md").write_text(decision + "\n", encoding="utf-8")

            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertIn("duplicate-decision", issues)

    def test_detects_missing_current_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "projects/demo"
            project.mkdir(parents=True)
            (project / "About.md").write_text(
                "---\nstatus: active\nupdated: 2026-11-06\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), str(root), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            issues = {item["issue"] for item in report["findings"]}
            self.assertIn("missing-current-state", issues)

    def test_missing_target_fails_cleanly(self):
        result = subprocess.run(
            ["python3", str(SCRIPT), "/definitely/not/a/real/folder", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a folder", result.stderr)


if __name__ == "__main__":
    unittest.main()
