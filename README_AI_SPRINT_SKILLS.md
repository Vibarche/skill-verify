# AI Sprint Skills v2

Improved versions of `connect-tool`, `setup-brain`, and `skill-manager`, based on `Melvynx/ai-sprint-skills` commit `9d03da22ef19b3d5c1b47bd827082b9aa007bb4c`.

## Skills

| Skill | Purpose | Entry point |
|---|---|---|
| `connect-tool` | Connect an approved external service through its official CLI or a generated Python API CLI. | `skills/connect-tool/SKILL.md` |
| `setup-brain` | Initialize and maintain a project-oriented agent brain. | `skills/setup-brain/SKILL.md` |
| `skill-manager` | Install, inspect, update, remove, create, improve and audit skills. | `skills/skill-manager/SKILL.md` |

## Installation

Copy the desired skill folder into your Agent Skills directory:

```bash
mkdir -p ~/.agents/skills
cp -R skills/connect-tool ~/.agents/skills/
cp -R skills/setup-brain ~/.agents/skills/
cp -R skills/skill-manager ~/.agents/skills/
```

For Claude Code, create links when your skills directory is separate:

```bash
mkdir -p ~/.claude/skills
ln -sfn ~/.agents/skills/connect-tool ~/.claude/skills/connect-tool
ln -sfn ~/.agents/skills/setup-brain ~/.claude/skills/setup-brain
ln -sfn ~/.agents/skills/skill-manager ~/.claude/skills/skill-manager
```

## Validation

```bash
python3 -m unittest discover -s tests -v
```

## Safety

These skills do not contain credentials. API keys remain on the local machine, preferably supplied through an environment variable or entered through the generated CLI's hidden login prompt. Never paste a secret into a chat, repository, screenshot, or log.
