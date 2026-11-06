#!/usr/bin/env python3
"""Read-only audit for agent brain and project memory folders."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path


def find_markdown_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.md")
        if ".git" not in path.parts and "node_modules" not in path.parts
    )


def parse_frontmatter(text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    frontmatter = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()
    return frontmatter


def audit(root: Path) -> dict:
    findings = []
    files = find_markdown_files(root)
    decisions = []

    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append({
                "severity": "critical",
                "file": relative,
                "issue": "unreadable-file",
                "detail": str(exc),
            })
            continue

        frontmatter = parse_frontmatter(text)
        if "About.md" in path.name:
            if "status" not in frontmatter:
                findings.append({
                    "severity": "warning",
                    "file": relative,
                    "issue": "missing-status",
                    "detail": "About.md has no status field",
                })
            if "## Current state" not in text:
                findings.append({
                    "severity": "warning",
                    "file": relative,
                    "issue": "missing-current-state",
                    "detail": "About.md has no Current state section",
                })

        for match in re.finditer(r"^-\s*(\d{4}-\d{2}-\d{2}):\s*(.+)$", text, re.MULTILINE):
            decisions.append({
                "file": relative,
                "date": match.group(1),
                "text": match.group(2).strip(),
            })

        for link_match in re.finditer(r"\[[^\]]+\]\(([^)#]+?\.md)\)", text):
            target = (path.parent / link_match.group(1)).resolve()
            if not target.exists():
                findings.append({
                    "severity": "critical",
                    "file": relative,
                    "issue": "broken-link",
                    "detail": link_match.group(1),
                })

        updated = frontmatter.get("updated")
        if updated:
            try:
                updated_date = datetime.strptime(updated, "%Y-%m-%d").date()
                age = (date.today() - updated_date).days
                if age > 90:
                    findings.append({
                        "severity": "info",
                        "file": relative,
                        "issue": "stale-file",
                        "detail": f"not updated for {age} days",
                    })
            except ValueError:
                findings.append({
                    "severity": "warning",
                    "file": relative,
                    "issue": "invalid-date",
                    "detail": updated,
                })

    normalized = Counter(
        re.sub(r"[^a-z0-9]+", " ", item["text"].lower()).strip()
        for item in decisions
    )
    for phrase, count in normalized.items():
        if count > 1 and len(phrase) > 20:
            findings.append({
                "severity": "warning",
                "file": "multiple",
                "issue": "duplicate-decision",
                "detail": phrase,
            })

    summary = Counter(item["severity"] for item in findings)
    return {
        "target": str(root),
        "files_scanned": len(files),
        "decisions_found": len(decisions),
        "findings": findings,
        "summary": dict(summary),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit agent memory files")
    parser.add_argument("target", nargs="?", default=".", help="Brain or project folder")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    root = Path(args.target).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a folder: {root}")

    report = audit(root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print(f"Target: {report['target']}")
    print(f"Files scanned: {report['files_scanned']}")
    print(f"Decisions found: {report['decisions_found']}")
    print(f"Findings: {report['summary'] or 'none'}")
    for item in report["findings"]:
        print(f"[{item['severity'].upper()}] {item['file']}: {item['issue']} - {item['detail']}")


if __name__ == "__main__":
    main()
