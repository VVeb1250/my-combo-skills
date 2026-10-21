"""User directory."""

_USERS = {
    1: {"name": "Ada", "email": "ada@example.com"},
    2: {"name": "Lin", "email": "lin@example.com"},
}


def find_user(user_id):
    """Return the user dict. Raises KeyError when the user does not exist."""
    return _USERS[user_id]
