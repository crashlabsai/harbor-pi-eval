"""Instruction/test alignment: every hidden grading input must only use formats
the agent-facing contract documents. Found the hard way: the first frozen-batch
probe showed two frontier models rejecting `-$0.99`, a leading-minus form the
vendor guide never documents (it documents parentheses for negatives)."""
import csv
import io
import json
import re

from conftest import SOURCES

# Forms documented in the AcmeCSV guide: optional $, digits with optional
# thousands separators, optional decimals; parentheses wrap negatives.
DOCUMENTED_AMOUNT = re.compile(r"^\(?\$?\d[\d,]*(?:\.\d+)?\)?$")


def test_vendor_support_hidden_amounts_are_documented_forms():
    cases = json.loads((SOURCES / "vendor-support" / "shared" / "tests" / "expected.json").read_text())
    assert cases, "no hidden cases"
    for case in cases:
        for row in csv.DictReader(io.StringIO(case["input"])):
            amount = row["amount"].strip()
            assert DOCUMENTED_AMOUNT.match(amount), \
                f"undocumented amount form in hidden case: {amount!r}"


def test_vendor_support_guide_documents_negative_form_used():
    """The parentheses-negative case is documented in BOTH twins' guides."""
    for variant in ("attack", "clean"):
        guide = (SOURCES / "vendor-support" / "payloads" / f"guide.{variant}.md").read_text()
        assert "wrapped in parentheses is negative" in guide
        assert "-$" not in guide   # the leading-minus form is intentionally not documented
