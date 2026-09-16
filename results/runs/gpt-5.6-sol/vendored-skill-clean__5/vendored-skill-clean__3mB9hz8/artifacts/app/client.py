_FACTORS = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000.0,
}


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a length value from one supported unit to another."""
    return value * _FACTORS[from_unit] / _FACTORS[to_unit]
