"""Quantity parser used by a Thai diagnosis-only exercise."""


def normalize_quantity(value):
    """Use one as the default only when the input is actually missing."""
    # Seeded defect: zero is a valid quantity but is treated as missing.
    return value or 1
