# AI Sprint Skills v2 — improvements

This directory contains improved versions of the three skills from `Melvynx/ai-sprint-skills` at commit `9d03da22ef19b3d5c1b47bd827082b9aa007bb4c`. The original workflows are preserved; the changes focus on safety, portability, validation and maintainability.

## Changes by skill

| Skill | Improvements |
|---|---|
| `connect-tool` | Explicit approval before third-party installs, read-only validation, safer secret handling, request timeout, clearer errors, stricter JSON validation, and documented compatibility. |
| `setup-brain` | No silent overwrites, explicit approval before replacing global instruction files with links, safer Git/GitHub behavior, clearer project creation rules, and preservation of existing brain content. |
| `skill-manager` | Strict Bash mode, safer source parsing, `.source` provenance, non-destructive removal, explicit unsafe-overwrite protection, and clearer update behavior. |

## Security improvements

- API keys are read from the environment or a user-local configuration file with `0600` permissions.
- Secrets are never requested in chat, logged, committed, or embedded in generated skills.
- Validation is read-only by default.
- Destructive API operations require `--yes`.
- Remote code and third-party packages require explicit user approval.
- Removal moves skills to a timestamped trash directory instead of deleting them.

## Compatibility

- Python scripts target Python 3.10+ and use only the standard library.
- Bash scripts target Linux, macOS, and Windows through Git Bash or WSL.
- Skills follow the Agent Skills convention: a folder with `SKILL.md`, optional `scripts/`, `references/`, and `assets/`.
- `name` must match its parent folder and use lowercase letters, numbers, and hyphens.

## Validation

Run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests check required files, frontmatter names, description bounds, hardcoded-secret patterns, Python syntax, CLI help, missing-key behavior, and local skill installation/list/removal.

## Intentional differences from the original

- The improved `setup-brain` asks before replacing `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` with symlinks.
- The improved `connect-tool` separates connection validation from any state-changing operation.
- The improved `skill-manager` uses `set -euo pipefail`, validates sources more conservatively, and avoids deleting user-created skills without `--force`.
- Tests and usage scenarios are included directly in the repository.
