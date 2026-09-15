"""For every family: the declared payload surface carries the injection only in
the attack twin, the useful facts before the payload section are identical across
twins, and the trusted user instruction never carries the attack."""
import pytest

from conftest import families, family_ids, task_dir


def _surface(family, spec, variant):
    return (task_dir(family, variant) / spec["surface"]).read_text()


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_attack_surface_contains_injection(family, spec, src):
    text = _surface(family, spec, "attack")
    for marker in spec["payload"]["attack_markers"]:
        assert marker in text, f"{family}: attack surface missing marker {marker!r}"


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_clean_surface_has_no_injection(family, spec, src):
    text = _surface(family, spec, "clean").lower()
    for marker in spec["payload"]["clean_forbidden_markers"]:
        assert marker.lower() not in text, \
            f"{family}: clean surface unexpectedly contains {marker!r}"


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_useful_facts_identical_before_payload_section(family, spec, src):
    marker = spec["payload"].get("common_split_marker")
    if not marker:
        pytest.skip(f"{family}: surface carries no shared useful-facts prefix "
                    "(facts live elsewhere; covered by twin invariance)")
    a = _surface(family, spec, "attack")
    c = _surface(family, spec, "clean")
    assert marker in a and marker in c, f"{family}: split marker missing"
    assert a[: a.index(marker)] == c[: c.index(marker)], \
        f"{family}: useful facts differ before the payload section"


@pytest.mark.parametrize("family,spec,src", families(), ids=family_ids())
def test_instruction_does_not_carry_attack(family, spec, src):
    for variant in spec["variants"]:
        instr = (task_dir(family, variant) / "instruction.md").read_text().lower()
        for marker in spec.get("instruction_forbidden_markers", []):
            assert marker.lower() not in instr, \
                f"{family}: instruction unexpectedly mentions {marker!r}"
