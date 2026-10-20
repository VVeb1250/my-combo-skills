"""Shopping cart totals."""

from money import to_cents


def cart_total_cents(prices):
    return sum(to_cents(price) for price in prices)
