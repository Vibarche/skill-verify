# Reliability Core

Reliability guardrails for AI agents.

This plugin exposes the following skills:

- `agent-memory-audit`: audits memory references, stale files, missing statuses and unsupported claims.
- `mcp-agent-hallucination-check`: detects invented MCP tools, exposed secrets, unconfirmed destructive actions and configuration issues.

## Install

```text
/plugin marketplace add agtktID/skill-verify
/plugin install reliability-core@skill-verify
```

## Skills

The skills remain maintained in the repository-level `skills/` directory. This plugin provides a focused installation bundle without duplicating their source files.
