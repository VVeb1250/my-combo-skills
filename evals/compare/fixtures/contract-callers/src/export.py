"""CSV export. Rows for missing users are skipped."""

from users import find_user


def export_rows(user_ids):
    rows = []
    for user_id in user_ids:
        try:
            user = find_user(user_id)
        except KeyError:
            continue
        rows.append(f"{user_id},{user['name']},{user['email']}")
    return rows
