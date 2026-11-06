"""Structural validation for the improved ai-sprint skills."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

EXPECTED = {
    "connect-tool": ["SKILL.md", "scripts/cli_template.py"],
    "setup-brain": [
        "SKILL.md",
        "references/about-md.md",
        "references/agents-md.md",
        "references/output-style.md",
    ],
    "skill-manager": ["SKILL.md", "scripts/skills.sh"],
}


class SkillStructureTests(unittest.TestCase):
    def test_expected_files_exist(self):
        for skill, files in EXPECTED.items():
            for relative in files:
                path = SKILLS / skill / relative
                self.assertTrue(path.is_file(), f"missing file: {path}")

    def test_skill_names_match_folders(self):
        for skill in EXPECTED:
            text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
            match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
            self.assertIsNotNone(match, f"missing name in {skill}")
            self.assertEqual(match.group(1).strip(), skill)

    def test_descriptions_are_present_and_bounded(self):
        for skill in EXPECTED:
            text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
            match = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            self.assertIsNotNone(match, f"missing description in {skill}")
            description = match.group(1).strip()
            self.assertGreaterEqual(len(description), 50)
            self.assertLessEqual(len(description), 1024)

    def test_no_hardcoded_secrets(self):
        patterns = [
            r"sk-[A-Za-z0-9]{20,}",
            r"ghp_[A-Za-z0-9]{20,}",
            r"AKIA[0-9A-Z]{16}",
        ]
        for path in SKILLS.rglob("*"):
            if path.is_file():
                content = path.read_text(encoding="utf-8", errors="ignore")
                for pattern in patterns:
                    self.assertIsNone(re.search(pattern, content), f"possible secret in {path}")


if __name__ == "__main__":
    unittest.main()
