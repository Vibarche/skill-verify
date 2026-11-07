# Brain AGENTS.md template

Use this skeleton for the brain's `AGENTS.md`. Keep it under 120 lines and replace placeholders only with confirmed user information.

```markdown
# User's brain

Personal command center organized by project. This is the single guide for agents working in this folder.

## User

- What the user does, location and timezone.
- Products or businesses.
- Technical level and preferred autonomy.
- Daily tools.
- Actions that always require confirmation.
- Where goals, plans and notes live.

## Layout

- `AGENTS.md`: this guide.
- `projects/`: one folder per project or hub.
- `notes/journal/`: one daily file named `YYYY-MM-DD.md`.
- `notes/ideas/`: ideas not yet started.
- `notes/todos/`: tasks not tied to a project.
- `archives/`: completed projects, created only when needed.
- `.tmp/`: scratch files, logs and screenshots; ignored by Git.

Do not create additional root folders until there is content for them.

## Projects

Every piece of work belongs in `projects/<slug>/`. Use lowercase names with hyphens. Before creating a project, look for an existing hub that fits.

Each project contains:

- `About.md`: required; status, purpose, key information and current state.
- `Roadmap.md`: optional; only real open tasks.
- `files/`, `assets/`, `output/`: created only when they contain something.

Status values are `active`, `paused` and `done`. Move completed projects to `archives/` without deleting their history.

## Working rules

- Read a project's `About.md` before working on it.
- Record important decisions and rejected alternatives in `About.md`.
- Keep one fact in one place; update an existing file before creating a new one.
- Put repeatable processes in a skill, not in a saved prompt.
- Ask before deleting, publishing, sending, paying or performing another irreversible action.
- At the end of a session, update the relevant project files and today's journal.
```
