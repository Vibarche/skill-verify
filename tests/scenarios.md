# Usage scenarios

These scenarios validate the improved skills beyond static structure tests. Run them in a disposable environment or a test project; never use production credentials.

## 1. Install a local skill

```bash
bash skills/skill-manager/scripts/skills.sh install /path/to/test-skill
bash skills/skill-manager/scripts/skills.sh list
```

Expected: `demo-skill` is installed under `~/.agents/skills/demo-skill`, has a `.source` file, and appears in `list`.

## 2. Refuse an unsafe overwrite

Install a local skill named `demo-skill`, then create another local skill with the same name but different instructions. Install the second one without `--force`.

Expected: exit code `3`, message `exists=demo-skill`, and no replacement of the first skill.

## 3. Update only managed skills

Install a skill from a local source, edit its `SKILL.md`, then run:

```bash
bash skills/skill-manager/scripts/skills.sh update demo-skill
```

Expected: the managed copy is refreshed from `.source`; the locally modified copy is preserved in the timestamped trash directory.

## 4. Remove without permanent loss

```bash
bash skills/skill-manager/scripts/skills.sh remove demo-skill
```

Expected: the skill disappears from `~/.agents/skills`, its Claude Code link is removed when present, and the folder remains under `~/.cache/removed-skills` with a timestamp.

## 5. Generate an API CLI

Use `connect-tool` with a test API that provides a read-only `/me` endpoint.

Expected: the generated CLI stores its key under `~/.config/<tool>-cli/config.json` with mode `0600`, runs `check`, and does not perform any write operation during validation.

## 6. Initialize a brain without data loss

Create a folder containing an existing `AGENTS.md` and one project. Run `setup-brain` on that folder.

Expected: the existing `AGENTS.md` is read, no file is silently overwritten, missing structure is added, and the user is asked before replacing existing global instruction files with links.

## 7. Validate skill metadata

```bash
python3 -m unittest discover -s tests -v
```

Expected: all structure and script tests pass, including skill-name/folder matching, description bounds, secret scanning, Python compilation, and Bash installation/removal behavior.
