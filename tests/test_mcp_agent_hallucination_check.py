"""Tests for mcp-agent-hallucination-check."""

from pathlib import Path
import json
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/mcp-agent-hallucination-check/scripts/mcp_contract_check.py"


class McpHallucinationCheckTests(unittest.TestCase):
    def test_script_compiles(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(SCRIPT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_detects_invented_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "Tool call: unknown_tool(search='test')\n",
                encoding="utf-8",
            )
            config = Path(tmp) / "config.json"
            config.write_text(
                json.dumps({"tools": [{"name": "known_tool"}]}),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("invented-tool", types)

    def test_detects_exposed_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text("key=sk-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("exposed-secret", types)


if __name__ == "__main__":
    unittest.main()
