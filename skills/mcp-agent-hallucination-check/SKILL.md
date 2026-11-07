---
name: mcp-agent-hallucination-check
description: Check an MCP agent workflow for invented tools, invalid arguments, fabricated results, memory hallucinations and unsafe execution. Use when reviewing an MCP integration, debugging an agent that invents tool output, or validating a skill before automation.
argument-hint: "[workflow file, transcript, or MCP config path] [--config mcp-config.json]"
license: MIT
compatibility: Requires Python 3.10+; performs no network calls.
metadata:
  source: https://arxiv.org/abs/2611.07689
  version: "1.1.0"
---

Check whether an agent workflow uses MCP tools truthfully. This skill is read-only: it never calls an MCP server, executes a tool, or modifies configuration.

1. Identify the input: a workflow file, conversation transcript, skill, or MCP configuration.
2. Run the local contract checker:

```bash
python3 scripts/mcp_contract_check.py <input-file> --config <mcp-config.json>
```

3. Extract every claimed MCP tool call, including server, tool, arguments and claimed result.
4. Compare each claim with the tools declared in the separate MCP configuration.
5. Flag these hallucination classes:

- Invented server or tool name.
- Argument not present in the declared input schema.
- Required argument missing.
- Result claimed without a corresponding tool call.
- Memory claim not supported by a local memory file.
- Destructive operation presented as safe or automatic.
- Credential, token, or secret exposed in a transcript.

6. Map findings to the four MCPHallu failure modes:

- **Unreachable Goal** : la tâche est irréalisable ou un prérequis manque, mais l'agent insiste ou prétend avoir réussi.
- **Branch Collapse** : l'agent perd sa trajectoire de planification après une réponse inattendue d'un serveur.
- **Tool Misuse** : mauvaise sérialisation ou mauvais usage des paramètres d'appel.
- **Context Forgetting** : l'agent oublie les retours d'exécution précédents lors de sessions multi-serveurs.

7. Use `references/hallucination-checklist.md` for the full review sequence.
8. Produce a report with `references/report-template.md`. State evidence for every finding; never label something a hallucination without a concrete mismatch.
9. Propose corrections, but do not edit workflow files or MCP configuration without approval.

If no MCP configuration or tool contract is available, report `UNVERIFIABLE`, list the missing evidence, and ask for the configuration or tool schema.
