import pytest
from vending_machine import select_item, make_change, purchase


def test_select_item_invalid():
    assert select_item("water", {}, 200) == "invalid"


def test_select_item_sold_out():
    assert select_item("cola", {"cola": 0}, 200) == "sold_out"


def test_select_item_insufficient_credit():
    assert select_item("cola", {"cola": 2}, 100) == "insufficient"


def test_select_item_ok():
    assert select_item("cola", {"cola": 2}, 150) == "ok"


def test_make_change_zero():
    assert make_change(0) == []


def test_make_change_greedy_coins():
    assert make_change(190) == [100, 50, 25, 10, 5]


def test_make_change_negative_raises():
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-1)


def test_make_change_no_exact_change():
    assert make_change(3) is None


def test_purchase_rejected_status_does_not_change_stock():
    stock = {"cola": 0}
    assert purchase("cola", stock, 200) == ("sold_out", [])
    assert stock["cola"] == 0


def test_purchase_no_exact_change_does_not_change_stock():
    stock = {"cola": 2}
    assert purchase("cola", stock, 153) == ("no_exact_change", [])
    assert stock["cola"] == 2


def test_purchase_dispenses_and_returns_change():
    stock = {"cola": 2}
    assert purchase("cola", stock, 200) == ("dispensed", [50])
    assert stock["cola"] == 1
