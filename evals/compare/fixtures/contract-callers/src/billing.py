"""Billing helpers. invoice_email raises LookupError when the user does not exist."""

from users import find_user


def invoice_email(user_id):
    try:
        user = find_user(user_id)
    except KeyError:
        raise LookupError(f"no such user: {user_id}") from None
    return user["email"]
