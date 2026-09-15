FACTORS = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0}


def convert(value, from_unit, to_unit):
    return value * FACTORS[from_unit] / FACTORS[to_unit]
