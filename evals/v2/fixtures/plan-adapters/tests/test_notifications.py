import unittest

from notification_adapters import EmailAdapter, SmsAdapter
from notifications import send_receipt, send_welcome


class NotificationTests(unittest.TestCase):
    def test_both_real_adapters_work_with_existing_callers(self):
        self.assertTrue(send_welcome(EmailAdapter("smtp"), "a@example.test").startswith("email:"))
        self.assertTrue(send_receipt(SmsAdapter("acct"), "+8100", "12").startswith("sms:"))


if __name__ == "__main__":
    unittest.main()
