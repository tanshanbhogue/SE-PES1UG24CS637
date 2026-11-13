import re
import pytest
from hypothesis import given, strategies as st
from vending_machine import parse_coins, slot_position, change_due


def valid_coins(s):
    if not isinstance(s, str) or not s.strip():
        return False
    parts = s.split(",")
    return all(
        part.strip().isascii()
        and part.strip().isdigit()
        and int(part.strip()) > 0
        for part in parts
    )


def valid_slot(s):
    if not isinstance(s, str):
        return False
    if not re.fullmatch(r"[A-Za-z][0-9]+", s):
        return False
    return int(s[1:]) > 0


def valid_payment(s):
    if not isinstance(s, str) or s.count("/") != 1:
        return False
    paid, price = s.split("/")
    if not (paid.isascii() and paid.isdigit()):
        return False
    if not (price.isascii() and price.isdigit()):
        return False
    return int(price) > 0 and int(paid) >= int(price)


@given(st.one_of(st.text(), st.none()))
def test_parse_coins_no_crash(s):
    if valid_coins(s):
        assert parse_coins(s) == [int(c.strip()) for c in s.split(",")]
    else:
        with pytest.raises(ValueError):
            parse_coins(s)


@given(st.one_of(st.text(), st.none()))
def test_slot_position_no_crash(s):
    if valid_slot(s):
        assert slot_position(s) == (
            ord(s[0].upper()) - ord("A"),
            int(s[1:]) - 1
        )
    else:
        with pytest.raises(ValueError):
            slot_position(s)


@given(st.one_of(st.text(), st.none()))
def test_change_due_no_crash(s):
    if valid_payment(s):
        paid, price = map(int, s.split("/"))
        assert change_due(s) == f"{(paid - price) // 5} five-coins"
    else:
        with pytest.raises(ValueError):
            change_due(s)
