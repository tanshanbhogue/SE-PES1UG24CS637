import pytest
from vending_machine import select_item, make_change, purchase


def test_select_item_all_decision_outcomes():
    assert select_item("water", {}, 200) == "invalid"
    assert select_item("cola", {"cola": 0}, 200) == "sold_out"
    assert select_item("cola", {"cola": 1}, 100) == "insufficient"
    assert select_item("cola", {"cola": 1}, 150) == "ok"


def test_make_change_negative_and_nonnegative():
    with pytest.raises(ValueError, match="negative amount"):
        make_change(-1)
    assert make_change(0) == []


def test_make_change_enters_each_coin_loop_and_exits_them():
    assert make_change(190) == [100, 50, 25, 10, 5]
    assert make_change(3) is None


def test_make_change_amount_not_representable():
    assert make_change(1) is None


def test_purchase_status_rejection_branch():
    stock = {"cola": 0}
    assert purchase("cola", stock, 200) == ("sold_out", [])
    assert stock["cola"] == 0


def test_purchase_no_exact_change_branch():
    stock = {"cola": 1}
    assert purchase("cola", stock, 153) == ("no_exact_change", [])
    assert stock["cola"] == 1


def test_purchase_success_branch():
    stock = {"chips": 2}
    assert purchase("chips", stock, 150) == ("dispensed", [50])
    assert stock["chips"] == 1
