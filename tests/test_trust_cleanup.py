import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "trust_cleanup", Path(__file__).resolve().parents[1] / "scripts/cleanup-ab-trust.py"
)
assert SPEC is not None and SPEC.loader is not None
cleanup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cleanup)


class TrustCleanupChecks(unittest.TestCase):
    def test_removes_exact_owned_project_and_preserves_other_bytes(self):
        prefix = b'model = "keep"\r\n# user preference\r\n'
        owned = b"[projects.'d:\\temp\\owned']\r\ntrust_level = \"trusted\"\r\n\r\n"
        suffix = b"[projects.'d:\\user\\repo']\r\ntrust_level = \"trusted\"\r\n"
        actual, keys = cleanup.remove_records(
            prefix + owned + suffix, {r"d:\temp\owned"}
        )
        self.assertEqual(actual, prefix + suffix)
        self.assertEqual(keys, [r"d:\temp\owned"])

    def test_refuses_owned_project_with_new_user_setting(self):
        raw = (
            b"[projects.'d:\\temp\\owned']\ntrust_level = \"trusted\"\ncustom = true\n"
        )
        with self.assertRaises(ValueError):
            cleanup.remove_records(raw, {r"d:\temp\owned"})

    def test_similar_path_is_not_owned(self):
        raw = b"[projects.'d:\\temp\\owned-user']\ntrust_level = \"trusted\"\n"
        self.assertEqual(cleanup.remove_records(raw, {r"d:\temp\owned"}), (raw, []))


if __name__ == "__main__":
    unittest.main()
