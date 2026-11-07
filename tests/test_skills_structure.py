import os
import yaml

SKILLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'skills')

EXPECTED_SKILLS = [
    'agent-memory-architect',
    'multi-agent-verifier',
    'agent-eval-designer',
    'self-hosted-stack-guide',
    'skill-architect',
    'mcp-agent-hallucination-check',
]

def test_skill_folders_exist():
    for skill in EXPECTED_SKILLS:
        assert os.path.isdir(os.path.join(SKILLS_DIR, skill)), f"Missing folder: {skill}"

def test_skill_md_exists():
    for skill in EXPECTED_SKILLS:
        path = os.path.join(SKILLS_DIR, skill, 'SKILL.md')
        assert os.path.isfile(path), f"Missing SKILL.md: {skill}"

def test_frontmatter_has_name_and_description():
    for skill in EXPECTED_SKILLS:
        path = os.path.join(SKILLS_DIR, skill, 'SKILL.md')
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert content.startswith('---'), f"No frontmatter: {skill}"
        frontmatter = content.split('---')[1]
        data = yaml.safe_load(frontmatter)
        assert 'name' in data, f"Missing name: {skill}"
        assert 'description' in data, f"Missing description: {skill}"
        assert data['name'] == skill, f"Name mismatch: {skill}"
