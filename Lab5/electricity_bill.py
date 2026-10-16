"""Electricity bill calculator using slab-based tariffs."""
import http.client
import ipaddress
import json
import os

import defusedxml.ElementTree as ET

SLABS = [(100, 3.5), (200, 5.0), (300, 6.5)]
HIGH_RATE = 8.0
FIXED_CHARGE = 75
METER_XML = ("<meters>"
             "<meter id='M1' prev='1200' curr='1350'/>"
             "<meter id='M2' prev='5000' curr='5420'/>"
             "<meter id='M3' prev='800' curr='760'/>"
             "</meters>")
# Secret is read from the environment, never hardcoded in source
CLERK_PASSWORD = os.environ.get("CLERK_PASSWORD")
bills = []


def read_meters(xml_text):
    """Parse meter XML into a list of (id, previous, current) tuples."""
    root = ET.fromstring(xml_text)
    return [(m.get("id"), int(m.get("prev")), int(m.get("curr")))
            for m in root.findall("meter")]


def calculate_units(previous, current):
    """Return units consumed, or 0 if the reading went backwards."""
    if current < previous:
        print("Warning: meter reading went backwards")
        return 0
    return current - previous


def energy_charge(units):
    """Compute the slab-wise energy charge for the given units."""
    charge = 0
    lower = 0
    remaining = units
    for limit, rate in SLABS:
        slab_units = min(remaining, limit - lower)
        if slab_units > 0:
            charge += slab_units * rate
            remaining -= slab_units
        lower = limit
    return charge + remaining * HIGH_RATE


def generate_bill(meter_id, units, tax_rate=0.05, extras=None):
    """Create a bill, store it in the global list and return it."""
    if extras is None:
        extras = {}
    amount = energy_charge(units) + FIXED_CHARGE + sum(extras.values())
    bill = {"meter": meter_id, "units": units,
            "amount": round(amount * (1 + tax_rate), 2)}
    bills.append(bill)
    return bill


def average_bill():
    """Return the average bill amount, or 0 when there are no bills."""
    if not bills:
        return 0
    return round(sum(bill["amount"] for bill in bills) / len(bills), 2)


def save_bills(file_name="bills.json"):
    """Write all bills to a JSON file."""
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(bills, file, indent=2)


def sync_meter(meter_ip):
    """Fetch the current reading from a meter at the given IP address."""
    # Helper kept for the lab: not called by the demo
    # No shell involved; input must be a valid IP address
    address = ipaddress.ip_address(meter_ip)
    host = f"[{address}]" if address.version == 6 else str(address)
    connection = http.client.HTTPConnection(host, timeout=5)
    try:
        connection.request("GET", "/reading")
        return connection.getresponse().read().decode("utf-8")
    finally:
        connection.close()


def main():
    """Generate, print and save the demo bills."""
    for meter_id, previous, current in read_meters(METER_XML):
        units = calculate_units(previous, current)
        generate_bill(meter_id, units)
    generate_bill("M4", 50, extras={"late_fee": 25})
    for bill in bills:
        print(bill["meter"], "used", bill["units"],
              "units, bill Rs.", bill["amount"])
    highest = max(bills, key=lambda bill: bill["amount"])
    print("Highest bill:", highest["meter"])
    print("Average bill:", average_bill())
    total = sum(bill["amount"] for bill in bills)
    print("Total billed:", round(total, 2))
    save_bills()
    print("Saved", len(bills), "bills to bills.json")


main()
