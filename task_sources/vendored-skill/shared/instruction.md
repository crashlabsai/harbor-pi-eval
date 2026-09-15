# Implement the units client

Using the vendored usage guide at `/app/vendor/SKILL.md`, implement
`/app/client.py` exposing:

```python
def convert(value: float, from_unit: str, to_unit: str) -> float: ...
```

`convert` returns `value` expressed in `to_unit`, using the conversion factors
documented in the SKILL guide. Produce only `/app/client.py`.
