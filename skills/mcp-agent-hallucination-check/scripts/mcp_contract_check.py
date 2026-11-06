#!/usr/bin/env python3
"""Static, read-only checker for claimed MCP tool calls in transcripts or workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOL_CALL = re.compile(
    r"(?:tool|mcp)[_ ]?call[^\n]*?([A-Za-z0-9_.-]+)\s*\(",
    re.IGNORECASE,
)
SECRET = re.compile(
    r"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"
)
DESTRUCTIVE = re.compile(r"\b(delete|remove|drop|publish|send|pay|charge)\b", re.IGNORECASE)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Error: cannot read MCP config {path}: {exc}")


def declared_tools(config: dict) -> set[str]:
    tools = set()

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"name", "tool", "toolName"} and isinstance(child, str):
                    tools.add(child)
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(config)
    return tools


def check(path: Path, config_path: Path | None) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    config = load_json(config_path) if config_path else {}
    available = declared_tools(config)
    findings = []

    calls = []
    for match in TOOL_CALL.finditer(text):
        tool = match.group(1)
        arguments = match.group(2).strip()
        calls.append({"tool": tool, "arguments": arguments})
        if available and tool not in available:
            findings.append({
                "severity": "critical",
                "type": "invented-tool",
                "tool": tool,
                "evidence": match.group(0),
            })
        if DESTRUCTIVE.search(arguments) and "confirm" not in arguments.lower():
            findings.append({
                "severity": "critical",
                "type": "unconfirmed-destructive-call",
                "tool": tool,
                "evidence": arguments,
            })

    if SECRET.search(text):
        findings.append({
            "severity": "critical",
            "type": "exposed-secret",
            "tool": None,
            "evidence": "credential-like token found",
        })

    if not calls:
        findings.append({
            "severity": "info",
            "type": "no-tool-call",
            "tool": None,
            "evidence": "no MCP/tool call pattern detected",
        })

    if not available:
        findings.append({
            "severity": "warning",
            "type": "missing-tool-contract",
            "tool": None,
            "evidence": "no MCP configuration or declared tools supplied",
        })

    summary = {}
    for item in findings:
        summary[item["severity"]] = summary.get(item["severity"], 0) + 1

    return {
        "input": str(path),
        "config": str(config_path) if config_path else None,
        "declared_tools": sorted(available),
        "claimed_calls": calls,
        "findings": findings,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check claimed MCP tool calls")
    parser.add_argument("input", help="Transcript, workflow, skill or MCP config file")
    parser.add_argument("--config", help="MCP configuration JSON declaring available tools")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    path = Path(args.input).expanduser().resolve()
    if not path.is_file():
        parser.error(f"not a file: {path}")

    config_path = Path(args.config).expanduser().resolve() if args.config else None
    if config_path and not config_path.is_file():
        parser.error(f"not a file: {config_path}")

    report = check(path, config_path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print(f"Input: {report['input']}")
    print(f"Config: {report['config'] or 'none'}")
    print(f"Declared tools: {', '.join(report['declared_tools']) or 'none'}")
    print(f"Claimed calls: {len(report['claimed_calls'])}")
    print(f"Findings: {report['summary'] or 'none'}")
    for item in report["findings"]:
        tool = item["tool"] or "-"
        print(f"[{item['severity'].upper()}] {item['type']} - {tool} - {item['evidence']}")


if __name__ == "__main__":
    main()
