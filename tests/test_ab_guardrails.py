import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "ab_eval", Path(__file__).resolve().parents[1] / "scripts/run-ab-eval.py"
)
assert SPEC is not None and SPEC.loader is not None
evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluation)


class ABGuardrailChecks(unittest.TestCase):
    def test_null_redirection_is_not_a_file_write(self):
        self.assertFalse(evaluation.is_write_like("git status --short 2>$null"))
        self.assertFalse(evaluation.is_write_like("rg --files . 2>\"'$null'"))

    def test_null_redirection_does_not_hide_real_writes(self):
        self.assertTrue(
            evaluation.is_write_like("Get-Content source > result.txt 2>$null")
        )
        self.assertTrue(
            evaluation.is_write_like("Set-Content output.txt value 2>$null")
        )


if __name__ == "__main__":
    unittest.main()
