---
name: skill-manager
description: Install, list, update, remove, create, improve or audit Agent Skills for Claude Code and Codex. Use for "install this skill", a skill link, "remove skill", "update skills", "make this a skill", or when a skill misbehaves.
argument-hint: "[install|remove|update|list|create|improve|audit] [skill name or link]"
license: MIT
compatibility: Requires Bash; supports Linux, macOS and Windows through Git Bash or WSL.
metadata:
  source: https://github.com/Melvynx/ai-sprint-skills
  version: "2.0.0"
---

Manage Agent Skills safely. A skill is a folder containing `SKILL.md`, optional `scripts/`, `references/` and `assets/`. Keep one canonical copy and use links elsewhere; never maintain two divergent copies.

## Locations

- Global skills: `~/.agents/skills/<name>/`, linked into `~/.claude/skills/` when needed.
- Project or brain skills: `<folder>/.agents/skills/<name>/`, linked into `<folder>/.claude/skills/` when needed.
- Installation metadata: `<skill>/.source`, containing the origin used for future updates.

## Install

1. Identify the source: a local folder, `owner/repo`, a GitHub skill-folder link, or a skill name from this kit.
2. Run `bash scripts/skills.sh available <source>` when the user asks what can be installed.
3. Run `bash scripts/skills.sh install <source> <skill> [--to <folder>]`. If a repository contains several skills and none is named, show the list and ask.
4. Inspect every downloaded skill before installation: read `SKILL.md`, identify scripts, check for network calls, destructive commands, credential handling and unexpected file writes.
5. Refuse or ask for explicit approval if a skill requests secrets, disables safeguards, runs remote code, or performs irreversible actions by default.
6. Verify that the installed skill contains `SKILL.md`, that its `name` matches its folder name, and that its description explains when to use it.

## Update and remove

- List skills with `bash scripts/skills.sh list [--to <folder>]`.
- Update only skills having a `.source` file: `bash scripts/skills.sh update [skill...] [--to <folder>]`.
- Before updating, show the source and ask whether local modifications should be preserved.
- Remove with `bash scripts/skills.sh remove <skill>... [--to <folder>]`; the script moves skills to a timestamped trash folder instead of deleting them.

## Create

1. Ask what the skill should do and two or three sentences the user would type to trigger it.
2. Choose a lowercase, hyphenated name, preferably verb-first, such as `write-newsletter` or `check-invoices`.
3. If an existing skill covers the task, improve it rather than creating a duplicate.
4. Write YAML frontmatter with `name` and a 50-300 character `description` that states the task and explicit trigger phrases.
5. Write imperative instructions in the order: read context, act, validate, report. Put deterministic commands in `scripts/` and long reference material in `references/`.
6. Create the skill in the selected location and link it for Claude Code only when needed.
7. Test it on a real case, then fix the skill rather than only correcting the immediate output.

## Improve and audit

- Read the skill and identify the exact instruction or missing safeguard that caused incorrect behavior.
- Change the minimum number of lines needed, preserving working behavior.
- Audit with `bash scripts/skills.sh list`, then check each skill for duplicates, stale paths, unsafe commands, unclear triggers and unused instructions.
- Remove a skill only after the user agrees.

Finish with one line per changed skill, its location, its trigger sentence, and any remaining validation needed.
