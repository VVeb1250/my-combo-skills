"""Existing callers depend on the shared adapter seam."""

from notification_adapters import NotificationAdapter


def send_welcome(adapter: NotificationAdapter, recipient: str) -> str:
    return adapter.send(recipient, "Welcome")


def send_receipt(adapter: NotificationAdapter, recipient: str, total: str) -> str:
    return adapter.send(recipient, f"Receipt: {total}")
