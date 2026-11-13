def parse_coins(coins_csv):
    if not isinstance(coins_csv, str) or not coins_csv.strip():
        raise ValueError("Coin input must be a non-empty string")

    coins = coins_csv.split(",")

    if not all(
        coin.strip().isascii()
        and coin.strip().isdigit()
        and int(coin.strip()) > 0
        for coin in coins
    ):
        raise ValueError("Coins must be positive integers separated by commas")

    return [int(coin.strip()) for coin in coins]


def slot_position(code):
    if not isinstance(code, str):
        raise ValueError("Slot code must be a string")

    if (
        len(code) < 2
        or not code[0].isascii()
        or not code[0].isalpha()
        or not code[1:].isascii()
        or not code[1:].isdigit()
        or int(code[1:]) <= 0
    ):
        raise ValueError("Invalid slot code. Expected format: B7")

    row = ord(code[0].upper()) - ord("A")
    column = int(code[1:]) - 1

    return row, column


def change_due(payment):
    if not isinstance(payment, str) or payment.count("/") != 1:
        raise ValueError("Payment must use the format paid/price")

    paid, price = payment.split("/")

    if (
        not paid.isascii()
        or not paid.isdigit()
        or not price.isascii()
        or not price.isdigit()
    ):
        raise ValueError("Payment and price must be integers")

    paid = int(paid)
    price = int(price)

    if price <= 0 or paid < price:
        raise ValueError("Price must be positive and payment must cover it")

    change = paid - price

    return str(change // 5) + " five-coins"


def main():
    print("==== Running parse_coins ====")
    user_input = input("Enter coin values as CSV (e.g. 5,10,25): ")
    result = parse_coins(user_input)
    print("Coins:", result)

    print("\n==== Running slot_position ====")
    user_input = input("Enter a slot code (e.g. B7): ")
    result = slot_position(user_input)
    print("Row and Column:", result)

    print("\n==== Running change_due ====")
    user_input = input("Enter paid/price (e.g. 200/150): ")
    result = change_due(user_input)
    print("Change Due:", result)


if __name__ == "__main__":
    main()
