# L6_L7_30 — Vending Machine

## Lab 7: Fuzz Testing

### About

This project demonstrates fuzz testing using **Hypothesis** and **pytest** on a small Python vending machine application.

The application contains three functions:

- `parse_coins(coins_csv)` – parses comma-separated coin values.
- `slot_position(code)` – converts a slot code (such as `B7`) into row and column coordinates.
- `change_due(payment)` – calculates the change due from a payment in `paid/price` format.

### Files

| File | Description |
|------|-------------|
| `vending_machine.py` | Vending machine application with input validation |
| `test_vending_machine.py` | Property-based tests using Hypothesis |
| `README.md` | Project documentation |

### Requirements

- Python 3
- pytest
- hypothesis

Install the required packages:

```bash
pip install pytest hypothesis
```

### Running the Application

From the `Lab7` directory, run:

```bash
python vending_machine.py
```

Example inputs:

- Coins: `5,10,25`
- Slot code: `B7`
- Payment: `200/150`

### Running the Tests

Run the property-based tests using:

```bash
python -m pytest test_vending_machine.py -v
```

### Fuzz Testing and Input Validation

Hypothesis generates a variety of inputs to test the application's functions, including invalid and unexpected values.

The tests check that:

- `parse_coins()` accepts valid positive integer coin values and rejects invalid input.
- `slot_position()` accepts valid letter-and-number slot codes and rejects malformed codes.
- `change_due()` accepts valid payment strings and rejects malformed payments or insufficient payment.

Invalid inputs raise `ValueError`, while valid inputs are checked against their expected results.

### Expected Result

All three property-based tests should pass after the input validation fixes have been applied.
