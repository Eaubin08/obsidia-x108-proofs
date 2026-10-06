"""A verbless protasis is never dropped (H11 prerequisite).

"Lance R si P", "Lance R si possible", "Si P, lance R": a protasis without a recognised verb
opens no unit; it was silently dropped while R closed as an unconditional request. It is now
reported (unanalyzed_predicative_content, conditional_protasis[_of]); no CONDITIONS relation
is invented (it needs a unit); R keeps its gate; the frame stays open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary


def _prag(f):
    return [(u.lemma, u.pragmatic) for u in f.units]


def _req(f):
    return governable_summary(f)["requested_action_surfaces"]


@pytest.mark.parametrize("text,span,link", [
    ("Lance R si P.", "si P", "conditional_protasis_of=u1"),
    ("Lance R si possible.", "si possible", "conditional_protasis_of=u1"),
    ("Si P, lance R.", "P", "conditional_protasis"),
    ("Si possible, lance R.", "possible", "conditional_protasis"),
])
def test_verbless_protasis_is_never_dropped(text, span, link):
    f = parse_utterance(text)
    kept = [(f.raw[int(m.split(":")[1].split("-")[0]):int(m.split(":")[1].split("-")[1])], m.split(":", 2)[2])
            for m in f.missing if m.startswith("unanalyzed_predicative_content:")]
    assert kept == [(span, link)]
    assert _req(f) == ["lance"] and not f.closure


def test_verbless_protasis_then_main_imperative_keeps_request():
    f = parse_utterance("Lance R si P et lance Q.")
    assert _prag(f) == [("lancer", "REQUESTED"), ("lancer", "REQUESTED")]
    assert _req(f) == ["lance", "lance"]
    assert any(m.endswith(":conditional_protasis_of=u1") for m in f.missing) and not f.closure
