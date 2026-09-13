from src.inventory import Item, inventory_summary


def test_default_excludes_discontinued_items():
    assert inventory_summary([Item("active", 2), Item("old", 3, discontinued=True)]) == {
        "count": 1,
        "units": 2,
    }
