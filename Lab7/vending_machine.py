def parse_coins(coins_csv):
    return [int(c) for c in coins_csv.split(',')]

def slot_position(code):
    row = ord(code[0].upper()) - ord('A')
    column = int(code[1:]) - 1
    return row, column

def change_due(payment):
    paid, price = payment.split('/')
    change = int(paid) - int(price)
    return str(change // 5) + ' five-coins'

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
