# acme-units-client

A tiny offline units client.

## Usage

`convert(value, from_unit, to_unit)` returns `value` expressed in `to_unit`.

## Conversion factors (relative to meters)

- `m`: 1.0
- `cm`: 0.01
- `mm`: 0.001
- `km`: 1000.0

Compute the result as `value * factor[from_unit] / factor[to_unit]`.

## Setup

No shell configuration is required. The client is a pure function: import it and
call `convert` directly. The conversion factors above are all you need to
produce correct results.
