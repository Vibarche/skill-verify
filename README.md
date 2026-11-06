# skill-verify

An evidence-first collection of 13 skills for AI coding agents. The collection covers project development, verification, skill design and Unity workflows. Skills provide instructions; their presence alone does not prove execution, security or production readiness.

## Development status

The verification refresh is being developed on `audit/skills-refresh-2026-11-05`. Changes on that branch are not necessarily available on `main` or through the default installer. No release is announced by this documentation update.

Regression scripts have been added, but successful execution has not been established in this maintenance session. Known implementation and test issues are listed below. Do not merge or deploy solely on the basis of these documentation changes.

## Installation

For the default repository version:

```bash
npx skills@latest add agtktID/skill-verify
```

To inspect the development branch:

```bash
git clone --branch audit/skills-refresh-2026-11-05 https://github.com/agtktID/skill-verify.git
cd skill-verify
```

To copy an individual skill into a consuming project, run from that project's root after cloning the repository alongside it:

```bash
mkdir -p .claude/skills
cp -R ../skill-verify/skills/verify .claude/skills/
```

Use the installation conventions supported by your agent. Runtime compatibility, permissions and hooks must be tested separately; no cross-runtime compatibility matrix has been validated during this refresh.

## Skill catalogue

| Skill | Purpose |
| --- | --- |
| [verify](skills/verify/) | Execute verification gates and collect evidence |
| [verify-feature-end2end](skills/verify-feature-end2end/) | Feature-level end-to-end verification |
| [verify-context-health](skills/verify-context-health/) | Review agent context usage |
| [verify-unity-playmode](skills/verify-unity-playmode/) | Unity test and build workflows |
| [project-init](skills/project-init/) | Project planning and initialization |
| [project-build](skills/project-build/) | Test-first feature implementation |
| [project-test](skills/project-test/) | Unit, integration and end-to-end testing |
| [project-ship](skills/project-ship/) | Release preparation and delivery |
| [project-review](skills/project-review/) | Code and architecture review |
| [skill-architect](skills/skill-architect/) | Design and evaluate skills |
| [gauntlet-loop-dev](skills/gauntlet-loop-dev/) | Iterative quality workflow |
| [indagis-feature-builder](skills/indagis-feature-builder/) | Project-specific feature workflow |
| [unity-gamedev](skills/unity-gamedev/) | Unity development workflow |

The catalogue describes intended responsibilities, not independently verified capabilities. Review a skill's instructions and scripts before granting execution permissions.

## Running verification

Run from the project you intend to check. Automatic detection inspects the current working directory; the runner does not change into the project root. Bash and the toolchains used by the selected gates must be available. Commands execute project code: review untrusted repositories before running them.

From this repository's root:

```bash
# Run all four gates.
bash skills/verify/scripts/run-verify.sh

# Select gates with positional arguments.
bash skills/verify/scripts/run-verify.sh 'Feature verification' tests,lint

# Or use named arguments.
bash skills/verify/scripts/run-verify.sh --task 'Feature verification' --gates tests,build

# Call the gate engine directly.
bash skills/verify/scripts/check.sh --tests --typecheck
```

For a skill copied into `.claude/skills`, use `.claude/skills/verify/scripts/run-verify.sh` instead.

### Exit codes

| Code | Status | Current behavior |
| --- | --- | --- |
| 0 | PASS | No failure, missing gate or blocked gate recorded; see limitations below |
| 1 | ECHEC | At least one gate failed and no blocked gate was recorded |
| 2 | BLOQUE / invalid invocation | A required test command was not detected, or arguments are invalid |
| 3 | PARTIEL | Optional gates were skipped, with no failure or blocked gate recorded |
| Other | Unexpected error | Not a validated result; inspect diagnostics |

`run-verify.sh` preserves the engine's exit code. A nonzero result must not be interpreted as PASS. A successful selected command does not prove coverage, end-to-end correctness or permission to deploy.

Tests are currently required when selected, including through `--all`. Lint, build and typecheck are treated as optional even when explicitly selected. A missing optional command produces SKIP and normally PARTIEL. This policy still needs refinement for release-blocking gates.

### Evidence

The engine writes command logs and a JSON summary under `.verify/<UTC timestamp>/`. The current `report.json` contains verdict and counters only: the implementation overwrites its earlier per-gate report content. It does not currently generate `report.md`.

## Hooks: experimental, non-blocking

Sources:

- `skills/verify/hooks/post-task.sh`
- `skills/verify/hooks/hooks.json`

The configuration contains PostToolUse/Bash and Stop handlers. The script also includes a SubagentStop branch, but that event is not registered in the supplied configuration. The script intends to read `hook_event_name`, `tool_name`, `tool_response` and `stop_hook_active`, and to consume `.verify/pending-task`. It runs the shell verification runner, not the `/verify` slash command.

The hook is informational: it returns 0 even if verification fails. It does not enforce release policy. `stop_hook_active` is intended as a Stop repeat guard, not a general concurrency lock.

Do not activate the current hook as a trusted verification gate yet:

- `IFS='|||'` splits on individual pipe characters, not the three-character delimiter. Payload fields can be misassigned, affecting trigger detection and the repeat guard.
- The supplied configuration assumes `<project>/skills/verify/hooks/post-task.sh`; it does not match an installation under `.claude/skills` or a separately copied `.claude/hooks` script.
- The marker is resolved from the current working directory.
- The hook does not change directory before checking the target project.
- The configured 60-second timeout may be insufficient for full verification.

Copying `hooks.json` into `.claude/hooks/` alone is not an activation procedure. After fixing and testing these issues, merge the appropriate hooks object into the consuming project's Claude Code settings without overwriting existing settings, and configure paths for the actual installation layout.

## Regression tests

```bash
bash scripts/test-check.sh
bash scripts/test-hooks.sh
```

Run both scripts and inspect each exit code; running the second command alone does not establish that the first passed. The engine suite uses temporary projects and requires npm for its package-script scenarios. The hook suite intends to use a fake runner and must not execute real project gates.

These are authored tests, not evidence of a passing test run. Current test limitations:

- `test-check.sh` expects unavailable typecheck to be BLOQUE, while the implementation treats it as optional. Its tsconfig fixture may invoke `npx tsc`, potentially causing package resolution or network access.
- Automatic lint detection depends on installed executables, so the gate tests are not fully hermetic.
- `test-hooks.sh` copies the hook to a temporary repository root, but the hook computes the runner path by ascending three directories. Positive trigger tests therefore do not reproduce the expected installation layout.
- The hook suite does not yet simulate a failing runner to prove non-blocking behavior on verification failure.

## Known engine issues still to fix

- `--json` is accepted but does not select gates or implement a distinct output mode. With only this option, zero gates can be reported as PASS.
- A blocked gate currently takes precedence over a failed gate in the aggregate verdict. Both counters must be inspected.
- Timestamp directories have one-second resolution and can collide.
- Package commands are detected with text matching rather than structured package.json parsing.
- Typecheck fallback uses `npx tsc --noEmit`; offline/local-only resolution is not enforced.
- Tool presence and project applicability are not consistently separated during detection.

The next validation milestone is to repair these issues, make test fixtures deterministic, execute both suites and record actual results before proposing a merge.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Never include secrets in logs or reports. Review changes before granting permissions, pushing, merging or deploying.

## License

MIT. See [LICENSE](LICENSE).
