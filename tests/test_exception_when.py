"""N15: "sauf / excepté quand / lorsque" never corrupts the main object.

"sauf" was only recognised before "si": before "quand" it was absorbed into
the main object ("r sauf", NO_EXECUTE(r sauf)). The connector now opens the
temporal subordinate (temporal_subordinate_open kept) and names the
exception (exception_condition_open); no CONDITIONS, no PRECEDES. The final
temporal-exception relation is held (H17, H05).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance


@pytest.mark.parametrize("text", ["Lance R sauf quand Paul lance P.", "Lance R excepté quand Paul lance P.",
                                  "Lance R sauf lorsque Paul lance P.", "Lance R excepté lorsque Paul lance P."])
def test_exception_when_is_named_and_object_clean(text):
    f = parse_utterance(text)
    r, p = f.units
    assert [a.text for a in r.objects] == ["r"]
    assert f"temporal_subordinate_open:{p.id}" in f.ambiguities
    # H17 A (requalified): one structural host -> EXCEPTS; the temporal reading stays held
    assert [(x.kind, x.source, x.target) for x in f.relations] == [("EXCEPTS", p.id, r.id)]
    assert not any(x.kind in {"CONDITIONS", "PRECEDES"} for x in f.relations) and not f.closure


def test_negated_host_constraint_targets_exactly_r():
    f = parse_utterance("Ne lance pas R sauf quand Paul lance P.")
    assert f.constraints == ("NO_EXECUTE(r)",)


def test_plain_quand_is_unchanged():
    f = parse_utterance("Lance R quand Paul lance P.")
    assert not any(a.startswith("exception_condition_open") for a in f.ambiguities)
