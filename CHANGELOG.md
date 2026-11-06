# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Professional repository README with evidence-first positioning.
- Original SVG repository banner.
- Contribution guide, code of conduct, and security policy.
- Issue and pull request templates.
- Initial repository structure and syntax validation workflow.
- `scripts/test-check.sh` with six gate regression scenarios.
- `scripts/test-hooks.sh` with twelve isolated hook scenarios and a fake runner fixture.

### Changed

- Verification runner accepts positional and named task/gate arguments and rejects unknown gates.
- Gate engine distinguishes tests, lint, build and typecheck and uses exit codes 0 (PASS), 1 (ECHEC), 2 (BLOQUE/invalid invocation) and 3 (PARTIEL).
- Tests are required when selected; lint, build and typecheck are currently optional.
- Runner preserves engine exit codes and reports partial results without promoting them to PASS.
- Hook configuration uses an event-keyed hooks object with PostToolUse/Bash and Stop handlers.
- Hook implementation reads event fields line-by-line, supports Stop/SubagentStop, consumes pending-task markers and discovers the runner across repository and copied-skill layouts.
- Hook remains intentionally non-blocking.
- README documents branch-specific installation, commands, actual report format, test prerequisites and known limitations as of 2026-11-06.

### Fixed

- Quoting in runner script-directory resolution.
- Literal .NET filename checks replaced with glob detection in the gate engine.
- Build and typecheck no longer share the same detection function.
- Hook pipe-delimiter parsing replaced with line-based field parsing.
- Hook runner discovery supports the repository layout and a skill copied under `.claude/skills`.
- Typecheck regression fixture made deterministic by using a project with no detectable typecheck command.

### Validation

On 2026-11-06, the maintainer executed both regression suites on `audit/skills-refresh-2026-11-05` at commit `53702bd`:

- `bash scripts/test-check.sh`: 6/6 scenarios PASS; exit code 0.
- `bash scripts/test-hooks.sh`: 12/12 scenarios PASS; exit code 0.

These results validate the covered regression scenarios only. They do not validate every runtime, every project type, production deployment, security posture or end-to-end agent workflow.

### Known limitations

- Engine JSON report currently retains summary counters only, not per-gate details.
- `--json` alone can produce PASS without executing gates; argument handling needs correction.
- Blocked gates take precedence over failed gates; timestamp directories can collide.
- Typecheck fallback may use network-dependent npx resolution, and lint detection depends on host tools.
- Hooks are non-blocking and do not provide deployment enforcement.
- `SubagentStop` is handled by the hook script but is not registered in the supplied hooks configuration.
- Cross-runtime compatibility and production hook integration remain untested.
- Changes remain on `audit/skills-refresh-2026-11-05`; this entry does not announce a release or merge into main.

## [0.1.0] - 2026-09-03

### Added

- Initial public collection of verification-oriented agent skills.
- Persistent `verify` workflow with evidence gates and explicit unknowns.
