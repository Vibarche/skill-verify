# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Professional repository README with evidence-first positioning.
- Original SVG repository banner.
- Contribution guide, code of conduct, and security policy.
- Issue and pull request templates.
- Initial repository structure and syntax validation workflow.
- `scripts/test-check.sh` with six authored gate regression scenarios.
- `scripts/test-hooks.sh` with isolated hook scenarios and a fake runner fixture.

### Changed

- Verification runner accepts positional and named task/gate arguments and rejects unknown gates.
- Gate engine distinguishes tests, lint, build and typecheck and uses exit codes 0 (PASS), 1 (ECHEC), 2 (BLOQUE/invalid invocation) and 3 (PARTIEL).
- Tests are required when selected; lint, build and typecheck are currently optional.
- Runner preserves engine exit codes and reports partial results without promoting them to PASS.
- Hook configuration uses an event-keyed hooks object with PostToolUse/Bash and Stop handlers.
- Hook implementation attempts to read current event fields and remains intentionally non-blocking.
- README documents branch-specific installation, commands, actual report format, test prerequisites and known limitations as of 2026-11-06.

### Fixed

- Quoting in runner script-directory resolution.
- Literal .NET filename checks replaced with glob detection in the gate engine.
- Build and typecheck no longer share the same detection function.

### Known limitations / validation pending

- No successful regression execution is claimed for this maintenance session; added tests are not passing-test evidence.
- Engine JSON report currently retains summary counters only, not per-gate details.
- `--json` alone can produce PASS without executing gates; argument handling needs correction.
- Blocked gates take precedence over failed gates; timestamp directories can collide.
- Typecheck fallback may use network-dependent npx resolution, and lint detection depends on host tools.
- Hook pipe-delimiter parsing can misassign fields; repeat prevention and trigger behavior require correction and tests.
- Hook runner paths and test fixture layout do not agree; copied `.claude/skills` installations are not handled by the supplied hook configuration.
- Typecheck test expectations do not match current optional-gate policy.
- Hooks are non-blocking and do not provide deployment enforcement.
- Changes remain on `audit/skills-refresh-2026-11-05`; this entry does not announce a release or merge into main.

## [0.1.0] - 2026-09-03

### Added

- Initial public collection of verification-oriented agent skills.
- Persistent `verify` workflow with evidence gates and explicit unknowns.
