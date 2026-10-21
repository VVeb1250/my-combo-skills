import unittest

from users import find_user


class UserTests(unittest.TestCase):
    def test_existing_user(self):
        self.assertEqual(find_user(1)["name"], "Ada")

    def test_missing_user_raises(self):
        with self.assertRaises(KeyError):
            find_user(99)


if __name__ == "__main__":
    unittest.main()
