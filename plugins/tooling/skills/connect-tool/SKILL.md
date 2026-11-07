---
name: connect-tool
description: Connect an approved tool such as Notion, Stripe or ClickFunnels to local agents by installing its official CLI or generating a minimal Python API CLI, then create a reusable skill. Use for "connect-tool notion", "connect X", "make a CLI for X", or "use my X API key".
argument-hint: "<tool name, e.g. notion or clickfunnels>"
license: MIT
compatibility: Requires Python 3.10+ for generated API CLIs; official CLIs may have their own requirements.
metadata:
  source: https://github.com/Melvynx/ai-sprint-skills
  version: "2.0.0"
---

Give the user's agents a new tool they can use from any folder as a `<tool>-cli` skill. Talk in the user's language, one short question at a time, without unnecessary jargon.

1. Confirm the tool and correct obvious spelling mistakes. If `~/.agents/skills/<tool>-cli/` already exists, inspect it and ask before changing it.
2. Prefer an official CLI published by the vendor. Check whether it is already installed with `command -v <cli>`. Never install a third-party package without explicit user approval.
3. If an official CLI exists, install it using its documented method, prefer non-sudo installation, and ask before using `sudo`. Verify it with `<cli> --version`, then read `--help` for the main commands.
4. If no official CLI exists, read only the official API documentation. Identify the base URL, authentication method, required settings, and the 5 to 10 read-mostly operations the user actually needs.
5. Copy `${CLAUDE_PLUGIN_ROOT}/skills/connect-tool/scripts/cli_template.py` to `~/.agents/skills/<tool>-cli/scripts/<tool>.py`. Fill only confirmed values: `TOOL`, `ENV_KEY`, `BASE_URL`, `KEY_URL`, `SETTINGS`, `auth_headers`, and `COMMANDS`. Keep `check` as a cheap read-only endpoint.
6. Tell the user where to create an API key and request the narrowest permissions needed. Have them run `python3 ~/.agents/skills/<tool>-cli/scripts/<tool>.py login` in their own terminal. Never ask them to paste a secret into the chat; if a secret is pasted into chat, do not use or repeat it; advise revoking it and generating a replacement locally.
7. Validate the connection with one harmless read-only command and one real read that returns a few items. Do not perform writes, deletes, payments, publications, or messages during validation.
8. Create `~/.agents/skills/<tool>-cli/SKILL.md`, under 30 lines, documenting only commands verified through `--help`, official documentation, or a successful test.
9. Link the skill for Claude Code only when needed: if `~/.claude/skills` is not already a link to `~/.agents/skills`, run `mkdir -p ~/.claude/skills && ln -sfn ~/.agents/skills/<tool>-cli ~/.claude/skills/<tool>-cli`.
10. Finish with: what was connected, where the skill lives, the command to try, and a warning that write operations require explicit confirmation.

Security rules:

- Never commit, echo, screenshot, or write an API key into a repository.
- Store generated configuration under the user's home directory with `0600` permissions.
- Treat every non-read operation as destructive until the user explicitly approves it.
- Do not install packages or run remote scripts without naming the source and obtaining approval.
