# Agent reliability skills

These skills were selected from recent arXiv cs.AI research on agent memory, verification and MCP hallucinations.

## `agent-memory-audit`

Inspired by research on structured and compressed agent memory, this skill audits a brain or project folder for duplicate decisions, contradictions, broken links, missing project state and stale context.

- Source inspiration: [Enhancing Local and Global Structure in Compressed AI Agent Memory](https://arxiv.org/abs/2611.08341)
- Default behavior: read-only.
- Output: JSON report or human-readable findings.
- Integration: strengthens `setup-brain` by making memory health measurable.

## `mcp-agent-hallucination-check`

Inspired by MCPHallu, this skill statically reviews claimed MCP tool calls for invented tools, unsupported results, exposed credentials and unconfirmed destructive operations.

- Source inspiration: [MCPHallu: Benchmarking Reasoning, Execution, and Memory Hallucinations in MCP Agents](https://arxiv.org/abs/2611.07689)
- Default behavior: read-only; no MCP server is called.
- Output: PASS, PARTIEL, FAIL, or UNVERIFIABLE.
- Integration: strengthens `connect-tool` and `skill-manager` by adding a reliability gate.

## Validation

```bash
python3 -m unittest discover -s tests -v
```

## Safety

Neither skill sends network requests, executes MCP tools, or changes files by default. File modifications require explicit user approval and must be minimal, evidence-based changes.
