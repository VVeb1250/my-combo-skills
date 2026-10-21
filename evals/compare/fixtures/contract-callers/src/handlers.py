"""Request handlers addressed by name. lookup answers {'status': 404} for a missing user."""

from users import find_user

HANDLERS = {"lookup": find_user}


def handle(name, user_id):
    try:
        user = HANDLERS[name](user_id)
    except KeyError:
        return {"status": 404}
    return {"status": 200, "user": user}
