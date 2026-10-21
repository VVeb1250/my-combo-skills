"""Independent contract: every caller keeps its documented missing-user behavior."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(os.environ["COMBO_EVAL_ROOT"]) / "src"))

from billing import invoice_email  # noqa: E402
from export import export_rows  # noqa: E402
from greeting import greet  # noqa: E402
from handlers import handle  # noqa: E402
from users import find_user  # noqa: E402


class ContractCallers(unittest.TestCase):
    def test_find_user_returns_none_for_a_missing_user(self):
        self.assertIsNone(find_user(99))
        self.assertEqual(find_user(1)["name"], "Ada")

    def test_greeting_still_greets_a_guest(self):
        self.assertEqual(greet(99), "Hello, guest")
        self.assertEqual(greet(1), "Hello, Ada")

    def test_billing_still_raises_lookup_error(self):
        self.assertEqual(invoice_email(1), "ada@example.com")
        with self.assertRaises(LookupError):
            invoice_email(99)

    def test_export_skips_missing_users(self):
        self.assertEqual(export_rows([1, 99, 2]), ["1,Ada,ada@example.com", "2,Lin,lin@example.com"])

    def test_named_handler_answers_404(self):
        self.assertEqual(handle("lookup", 99), {"status": 404})
        self.assertEqual(handle("lookup", 1)["status"], 200)


if __name__ == "__main__":
    unittest.main(verbosity=2)
