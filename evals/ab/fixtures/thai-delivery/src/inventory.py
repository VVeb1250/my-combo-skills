"""Inventory reporting primitives for a Thai delivery exercise."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    sku: str
    quantity: int
    discontinued: bool = False


def inventory_summary(items):
    """Return the count and units for currently available inventory."""
    available = [item for item in items if item.quantity > 0 and not item.discontinued]
    return {"count": len(available), "units": sum(item.quantity for item in available)}
