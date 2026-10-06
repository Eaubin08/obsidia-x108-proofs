"""F1: a verbless exception condition ("Lance R sauf si P", "excepté si P", "à moins que P")
is never absorbed into the main object nor read as an ordinary condition.

It was merged back into the host clause: object "r sauf", NO_EXECUTE(r sauf), and "si P"
reported as a plain conditional protasis. The exception clause now stays its own clause,
reported as exception content (exception_condition), no CONDITIONS, the host keeps exactly
its object (and its gate / prohibition), the frame stays open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _kept(f):
    return [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":", 2)[2])
            for m in f.missing if m.startswith("unanalyzed_predicative_content:")]


@pytest.mark.parametrize("text,content", [("Lance R sauf si P.", "P"), ("Lance R excepté si P.", "P"),
                                          ("Lance R à moins que P.", "P"), ("Lance R, sauf si possible.", "possible")])
def test_verbless_exception_keeps_object_and_request(text, content):
    f = parse_utterance(text)
    assert [(u.pragmatic, tuple(a.text for a in u.objects)) for u in f.units] == [("REQUESTED", ("r",))]
    assert governable_summary(f)["requested_action_surfaces"] == ["lance"]
    assert _kept(f) == [(content, "exception_condition")]
    assert not any(r.kind == "CONDITIONS" for r in f.relations) and not f.closure


def test_verbless_exception_under_prohibition_keeps_exact_target():
    f = parse_utterance("Ne lance pas R sauf si P.")
    assert [(u.pragmatic, tuple(a.text for a in u.objects)) for u in f.units] == [("FORBIDDEN", ("r",))]
    assert f.constraints == ("NO_EXECUTE(r)",)
    assert _kept(f) == [("P", "exception_condition")] and not f.closure
