# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Professional repository README with evidence-first positioning.
- Original SVG repository banner.
- Contribution guide, code of conduct, and security policy.
- Issue and pull request templates.
- Initial repository structure and syntax validation workflow.

## [0.2.0] - 2026-11-07

### Added

- Agentic Intelligence Suite with four new skills:
  - `agent-memory-architect`: memory architecture design with local/global compression.
  - `multi-agent-verifier`: planner/verifier workflow with state traces.
  - `agent-eval-designer`: benchmarks and evaluation metrics for agents.
  - `self-hosted-stack-guide`: self-hosted AI stack deployment guide.
- Plugin-level `README.md` describing the Agent Reliability Toolkit.

### Changed

- `skill-architect` upgraded to v1.2.0 with a new Skillware mode (typed schema, deterministic code, tests, embedded data).
- `mcp-agent-hallucination-check` upgraded to v1.1.0 with the four MCPHallu failure modes (Unreachable Goal, Branch Collapse, Tool Misuse, Context Forgetting).
- `skills/manifest.yml` updated to register the new Agentic Intelligence Suite.

## [0.1.0] - 2026-09-03

### Added

- Initial public collection of verification-oriented agent skills.
- Persistent `verify` workflow with evidence gates and explicit unknowns.
