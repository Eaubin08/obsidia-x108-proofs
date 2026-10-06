"""D2b: "Paul se demande / ignore si P" never drops its (unknown) governing predication.

The governor verb is not in the lexicon: its clause had no unit and was silently dropped,
leaving "si P" as a free protasis with a closed frame. The governor clause is now reported
(unanalyzed_predicative_content) and the "si" complement is named
complement_under_unresolved_governor: frame open, no CONDITIONS, no request.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


@pytest.mark.parametrize("text,governor", [("Paul se demande si Marie a lancé P.", "Paul se demande"),
                                           ("Paul ignore si Marie a lancé P.", "Paul ignore")])
def test_unknown_governor_of_si_complement_is_kept(text, governor):
    f = parse_utterance(text)
    kept = [f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])] for m in f.missing]
    assert kept == [governor]
    assert f"complement_under_unresolved_governor:{f.units[0].id}" in f.ambiguities
    assert not any(r.kind == "CONDITIONS" for r in f.relations)
    assert governable_summary(f)["requested_world_actions"] == [] and not f.closure


def test_plain_condition_unchanged():
    f = parse_utterance("Lance R si Paul lance P.")
    assert [r.kind for r in f.relations] == ["CONDITIONS"] and f.closure
