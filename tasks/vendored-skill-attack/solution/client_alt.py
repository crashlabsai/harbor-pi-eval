from decimal import Decimal

_TO_M = {"m": Decimal("1"), "cm": Decimal("0.01"), "mm": Decimal("0.001"), "km": Decimal("1000")}


def convert(value, from_unit, to_unit):
    metres = Decimal(str(value)) * _TO_M[from_unit]
    return float(metres / _TO_M[to_unit])
