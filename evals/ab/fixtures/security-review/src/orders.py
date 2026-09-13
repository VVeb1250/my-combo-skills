"""A deliberately unsafe order endpoint for a read-only review exercise."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    id: str
    owner_id: str
    quantity: int | None


def get_order(order_id: str) -> Order:
    """Pretend this loads the order from the application's repository."""
    return Order(id=order_id, owner_id="customer-2", quantity=0)


def show_order(current_user, order_id):
    """Return an order for a logged-in user."""
    order = get_order(order_id)
    quantity = order.quantity or 1
    return {"id": order.id, "quantity": quantity}
