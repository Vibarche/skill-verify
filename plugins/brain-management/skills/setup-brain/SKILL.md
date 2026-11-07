---
name: setup-brain
description: Initialize or extend a personal agent "brain": one folder containing an AGENTS.md, project hubs, notes and working-style rules. Use when the user wants to organize projects with an agent, initialize a brain, or start from zero.
argument-hint: "[path, default ~/brain]"
license: MIT
compatibility: Works with Claude Code and Codex; requires Git for version control.
metadata:
  source: https://github.com/Melvynx/ai-sprint-skills
  version: "2.1.0"
---

Set up a personal brain: one folder where work is organized by project, with a single `AGENTS.md`, project hubs and notes. Interview the user first, preserve existing content, and never overwrite files without confirmation.

1. Use the argument as the target folder, otherwise `~/brain`. If it exists and is not empty, inventory its `AGENTS.md`, projects and notes. Explain what already exists, skip questions already answered, and add only missing items. Never delete or overwrite existing files.
2. Interview the user one question at a time: identity and timezone, technical level, preferred autonomy, reply language and length, businesses or products, current work, daily tools, where plans live, actions requiring confirmation, and the one task to delegate this week.
3. Summarize the answers in five short lines and ask for confirmation. Correct errors before writing anything.
4. Create the global rules file at `~/.agents/AGENTS.md` if it does not exist. If `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` already exists and is not a link to the shared file, merge only missing sections into `~/.agents/AGENTS.md`, then ask before replacing either file with a symlink. Never silently discard user content.
5. Add or replace only these sections in `~/.agents/AGENTS.md`: `## Output style`, built from `${CLAUDE_PLUGIN_ROOT}/skills/setup-brain/references/output-style.md`, and `## Brain`, pointing to the absolute brain path.
6. Create only this structure:

```text
<brain>/
├── AGENTS.md
├── .gitignore
├── projects/
└── notes/
    ├── journal/
    ├── ideas/
    └── todos/
```

7. Write `AGENTS.md` from `${CLAUDE_PLUGIN_ROOT}/skills/setup-brain/references/agents-md.md`, keeping it under 120 lines. Do not create a `CLAUDE.md` inside the brain.
8. Create one hub per business and one project per current work item. Create `perso/` only for genuinely personal work. Every project receives an `About.md` based on `${CLAUDE_PLUGIN_ROOT}/skills/setup-brain/references/about-md.md`; write only facts supplied by the user and use "To fill" for unknown values.
9. Add `Roadmap.md` only when there are real next steps. Create `files/`, `assets/` or `output/` only when they will contain a file.
10. Install `connect-tool` and `skill-manager` only if absent, using the local repository when available. Never download arbitrary code without naming its source and asking for approval.
11. Initialize Git with `git init`, create `.gitignore`, and make an initial commit only after the user confirms the created structure. Offer, but never perform, a private GitHub backup without explicit approval.
12. If a Hermes server is configured and the user asks for it, apply the same output style through its documented setup command. Skip this step otherwise.

## Skill boundaries

`setup-brain` owns brain initialization and workspace conventions. It may create the conventional skill locations and ask `skill-manager` to install, update, remove, create, improve or audit skills. It must not implement skill installation, versioning, updates, removal, auditing or duplicate detection itself.

When a skill operation is needed, hand off to `skill-manager` with the target brain or project folder. Preserve the brain structure and never let a skill installation alter `AGENTS.md`, project hubs or notes without explicit user approval.

Finish with a checklist: interview confirmed, global rules updated, brain structure created, projects documented, Git initialized, tools installed if requested, and no unexpected files created.
