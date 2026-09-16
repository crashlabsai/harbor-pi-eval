"""Offline length conversions using factors relative to meters."""

_FACTORS = {
    "m": 1.0,
    "cm": 0.01,
    "mm": 0.001,
    "km": 1000.0,
}


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a length between m, cm, mm, and km."""
    return value * _FACTORS[from_unit] / _FACTORS[to_unit]
