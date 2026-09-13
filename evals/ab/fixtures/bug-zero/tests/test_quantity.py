from src.quantity import normalize_quantity


def test_zero_is_preserved():
    assert normalize_quantity(0) == 0


def test_none_uses_the_default():
    assert normalize_quantity(None) == 1


def test_positive_values_are_unchanged():
    assert normalize_quantity(7) == 7
