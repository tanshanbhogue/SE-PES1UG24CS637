from hypothesis import given, strategies as st
from vending_machine import parse_coins, slot_position, change_due

@given(st.text() | st.none())
def test_parse_coins_no_crash(s):

@given(st.text() | st.none())
def test_slot_position_no_crash(s):

@given(st.text() | st.none())
def test_change_due_no_crash(s):
