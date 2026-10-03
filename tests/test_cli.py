"""Exercise the shipped examples through the real process entrypoint."""

import json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CLITests(unittest.TestCase):
    def test_help_entrypoint(self):
        result = subprocess.run(
            [sys.executable, "-m", "contract_diff_analyzer", "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout)

    def test_documented_workflow(self):
        with tempfile.TemporaryDirectory() as folder:
            clone = Path(folder)
            shutil.copytree(
                ROOT / "contract_diff_analyzer", clone / "contract_diff_analyzer"
            )
            shutil.copytree(ROOT / "examples", clone / "examples")
            for command in ["compare examples/before.json examples/after.json"]:
                result = subprocess.run(
                    [sys.executable, "-m", "contract_diff_analyzer", *command.split()],
                    cwd=clone,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
            self.assertEqual(payload["breaking"], 2)
