from src.inventory import Item, inventory_summary


def test_default_behavior():
    assert inventory_summary([Item("active", 2), Item("old", 3, discontinued=True)]) == {
        "count": 1,
        "units": 2,
    }
