from src.quantity import normalize_quantity


def test_zero_is_a_real_value():
    assert normalize_quantity(0) == 0


def test_none_uses_the_default():
    assert normalize_quantity(None) == 1
