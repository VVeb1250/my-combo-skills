"""Two production adapters currently used by the notification service."""

from dataclasses import dataclass
from typing import Protocol


class NotificationAdapter(Protocol):
    def send(self, recipient: str, body: str) -> str:
        """Send a message and return the provider receipt."""


@dataclass
class EmailAdapter:
    smtp_host: str

    def send(self, recipient: str, body: str) -> str:
        return f"email:{self.smtp_host}:{recipient}"


@dataclass
class SmsAdapter:
    account_id: str

    def send(self, recipient: str, body: str) -> str:
        return f"sms:{self.account_id}:{recipient}"
