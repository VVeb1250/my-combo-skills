from catalog import select_labels


def initial_filters():
    return select_labels(None)


def after_user_selection(selected_labels):
    # The UI sends [] when the user clears every checkbox.
    return select_labels(selected_labels)
