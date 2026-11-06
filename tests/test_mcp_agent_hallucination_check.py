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
                ["python3", str(SCRIPT), str(transcript), "--config", str(config), "--json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("invented-tool", types)

    def test_known_tool_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "Tool call: known_tool(search='test')\n",
                encoding="utf-8",
            )
            config = Path(tmp) / "config.json"
            config.write_text(
                json.dumps({"tools": [{"name": "known_tool"}]}),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--config", str(config), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertNotIn("invented-tool", types)

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

    def test_detects_unconfirmed_destructive_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "Tool call: known_tool(action='delete record')\n",
                encoding="utf-8",
            )
            config = Path(tmp) / "config.json"
            config.write_text(
                json.dumps({"tools": [{"name": "known_tool"}]}),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--config", str(config), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("unconfirmed-destructive-call", types)

    def test_confirmed_destructive_call_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "Tool call: known_tool(action='delete record', confirm=true)\n",
                encoding="utf-8",
            )
            config = Path(tmp) / "config.json"
            config.write_text(
                json.dumps({"tools": [{"name": "known_tool"}]}),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--config", str(config), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertNotIn("unconfirmed-destructive-call", types)

    def test_missing_config_reports_missing_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text(
                "Tool call: known_tool(search='test')\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("missing-tool-contract", types)

    def test_no_tool_call_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "transcript.md"
            transcript.write_text("No tool was used.\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(SCRIPT), str(transcript), "--json"],
                capture_output=True,
                text=True,
            )
            report = json.loads(result.stdout)
            types = {item["type"] for item in report["findings"]}
            self.assertIn("no-tool-call", types)


if __name__ == "__main__":
    unittest.main()
