LABELS = ("new", "sale", "archived")


def select_labels(requested=None):
    selected = requested or LABELS
    return [label for label in selected if label in LABELS]
