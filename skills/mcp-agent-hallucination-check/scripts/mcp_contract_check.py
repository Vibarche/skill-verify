#!/usr/bin/env python3
"""Static, read-only checker for claimed MCP tool calls in transcripts or workflows."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOL_CALL = re.compile(
    r"(?:tool|mcp)[_ ]?call[^\n]*?([A-Za-z0-9_.-]+)\s*\(([^)]*)\)",
    re.IGNORECASE,
)
SECRET = re.compile(
    r"(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})"
)
DESTRUCTIVE = re.compile(r"\b(delete|remove|drop|publish|send|pay|charge)\b", re.IGNORECASE)


def load_json_or_text(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".json":
        try:
            parsed = json.loads(text)
            return {"text": json.dumps(parsed, ensure_ascii=False), "config": parsed}
        except json.JSONDecodeError:
            return {"text": text, "config": {}}
    return {"text": text, "config": {}}


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


def check(path: Path) -> dict:
    data = load_json_or_text(path)
    text = data["text"]
    available = declared_tools(data["config"])
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

    summary = {}
    for item in findings:
        summary[item["severity"]] = summary.get(item["severity"], 0) + 1

    return {
        "input": str(path),
        "declared_tools": sorted(available),
        "claimed_calls": calls,
        "findings": findings,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check claimed MCP tool calls")
    parser.add_argument("input", help="Transcript, workflow, skill or MCP config file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    path = Path(args.input).expanduser().resolve()
    if not path.is_file():
        parser.error(f"not a file: {path}")

    report = check(path)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print(f"Input: {report['input']}")
    print(f"Declared tools: {', '.join(report['declared_tools']) or 'none'}")
    print(f"Claimed calls: {len(report['claimed_calls'])}")
    print(f"Findings: {report['summary'] or 'none'}")
    for item in report["findings"]:
        tool = item["tool"] or "-"
        print(f"[{item['severity'].upper()}] {item['type']} - {tool} - {item['evidence']}")


if __name__ == "__main__":
    main()
