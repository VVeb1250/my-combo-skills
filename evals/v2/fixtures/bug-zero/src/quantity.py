"""Small quantity parser with a seeded zero-value regression."""


def normalize_quantity(value):
    """Use one as the default only when the input is actually missing."""
    # Deliberately seeded defect for the workflow eval.
    return value or 1
