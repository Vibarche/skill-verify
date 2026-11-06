---
name: agent-memory-audit
description: Audit an agent brain, project memory or notes folder for duplicate facts, contradictions, missing decisions, broken references and stale context. Use when the user says "audit memory", "clean my brain", "find memory conflicts", or before continuing a long agent project.
argument-hint: "[brain or project path, default current folder]"
license: MIT
compatibility: Requires Python 3.10+; read-only by default.
metadata:
  source: https://arxiv.org/abs/2611.08341
  version: "1.0.0"
---

Audit local agent memory without changing it. The goal is trustworthy memory: one fact in one place, decisions linked to reasons, and no stale or contradictory context.

1. Use the argument as the target folder, otherwise the current folder. Confirm the target in one line.
2. Run the read-only scanner:

```bash
python3 scripts/memory_audit.py <target-folder>
```

3. Read the JSON report. Focus on duplicate facts, contradictory decisions, missing `About.md`, empty required sections, broken relative Markdown links, and stale `updated` dates.
4. Read only files flagged by the report. Do not infer facts not written in memory files.
5. Classify findings:

- `critical`: contradictory decision, broken required file, or a fact blocking future work.
- `warning`: duplicate information, missing reason, stale date, or ambiguous ownership.
- `info`: improvement opportunity that does not affect current work.

6. Produce a report using `references/report-template.md`. For each finding, provide file, section, evidence, risk and a minimal proposed fix.
7. Ask before modifying any file. Apply only approved fixes, one logical change at a time.
8. After edits, rerun the scanner and show before/after finding counts.

Never delete history, merge projects, or rewrite decisions without explicit user approval.
