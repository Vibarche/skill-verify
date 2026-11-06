"""Structural validation for the improved ai-sprint skills."""

from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
MANIFEST = SKILLS / "manifest.yml"

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

    def test_every_skill_directory_is_in_manifest(self):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        registered = {item["name"] for item in manifest["skills"]}
        for skill_dir in SKILLS.iterdir():
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
                continue
            self.assertIn(
                skill_dir.name,
                registered,
                f"skill directory missing from manifest: {skill_dir.name}",
            )

    def test_every_manifest_path_exists_with_skill_md(self):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        for item in manifest["skills"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_dir(), f"manifest path missing: {path}")
            self.assertTrue(
                (path / "SKILL.md").is_file(),
                f"SKILL.md missing for manifest skill: {item['name']}",
            )

    def test_manifest_contains_all_eighteen_skills(self):
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["skills"]), 18)


if __name__ == "__main__":
    unittest.main()
