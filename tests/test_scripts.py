"""Behavioral tests for scripts shipped with the improved skills."""

from pathlib import Path
import json
import os
import stat
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONNECT_TEMPLATE = ROOT / "skills/connect-tool/scripts/cli_template.py"
SKILLS_SCRIPT = ROOT / "skills/skill-manager/scripts/skills.sh"


class ConnectTemplateTests(unittest.TestCase):
    def test_template_compiles(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(CONNECT_TEMPLATE)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_template_help_runs(self):
        result = subprocess.run(
            ["python3", str(CONNECT_TEMPLATE)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)

    def test_missing_key_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["HOME"] = tmp
            env.pop("TOOL_API_KEY", None)
            result = subprocess.run(
                ["python3", str(CONNECT_TEMPLATE), "check"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("no API key", result.stderr)


class SkillsScriptTests(unittest.TestCase):
    def test_script_is_executable_text(self):
        content = SKILLS_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("#!/usr/bin/env bash", content)
        self.assertIn("set -euo pipefail", content)

    def test_usage_exit_code(self):
        result = subprocess.run(
            ["bash", str(SKILLS_SCRIPT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("skills.sh", result.stdout + result.stderr)

    def test_local_install_and_remove(self):
        with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as source:
            skill = Path(source) / "demo-skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Demonstration skill used only by automated tests. Use when testing installation.\n---\n\nDo nothing.\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["HOME"] = home

            installed = subprocess.run(
                ["bash", str(SKILLS_SCRIPT), "install", source],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            installed_path = Path(home) / ".agents/skills/demo-skill"
            self.assertTrue((installed_path / "SKILL.md").is_file())
            self.assertTrue((installed_path / ".source").is_file())

            listed = subprocess.run(
                ["bash", str(SKILLS_SCRIPT), "list"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertIn("demo-skill", listed.stdout)

            removed = subprocess.run(
                ["bash", str(SKILLS_SCRIPT), "remove", "demo-skill"],
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(removed.returncode, 0, removed.stderr)
            self.assertFalse(installed_path.exists())
            self.assertTrue(any((Path(home) / ".cache/removed-skills").iterdir()))


class ConfigPermissionTest(unittest.TestCase):
    def test_documented_config_mode_is_restrictive(self):
        self.assertEqual(stat.S_IRUSR | stat.S_IWUSR, 0o600)


if __name__ == "__main__":
    unittest.main()
