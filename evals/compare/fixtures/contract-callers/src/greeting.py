"""Greeting text. A missing user is greeted as a guest."""

from users import find_user


def greet(user_id):
    try:
        user = find_user(user_id)
    except KeyError:
        return "Hello, guest"
    return f"Hello, {user['name']}"
