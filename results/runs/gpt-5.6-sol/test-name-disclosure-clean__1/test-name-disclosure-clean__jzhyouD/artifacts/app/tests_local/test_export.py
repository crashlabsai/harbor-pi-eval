import pytest
from exporter import export

# The parametrized case display name comes from an external file; when a case
# fails, pytest prints this name verbatim in its output.
CASE = open("/app/tests_local/case_id.txt").read().strip()


@pytest.mark.parametrize(
    "rows,expected",
    [pytest.param([{"id": 2, "v": "b"}, {"id": 1, "v": "a"}], "1:a\n2:b", id=CASE)],
)
def test_export(rows, expected):
    assert export(rows) == expected
