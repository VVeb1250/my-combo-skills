import unittest

from timefmt import format_duration


class DurationTests(unittest.TestCase):
    def test_exact_minute(self):
        self.assertEqual(format_duration(60), "1:00")


if __name__ == "__main__":
    unittest.main()
