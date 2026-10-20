"""Money helpers shared by the cart and the invoice."""


def to_cents(amount):
    """Convert a decimal amount in currency units to whole cents."""
    return int(amount * 100)
