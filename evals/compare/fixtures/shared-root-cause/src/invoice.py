"""Invoice lines."""

from money import to_cents


def line_total_cents(unit_price, quantity):
    return to_cents(unit_price) * quantity
