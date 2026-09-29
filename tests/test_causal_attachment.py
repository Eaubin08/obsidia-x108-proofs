"""Causal C2: no nearest causal binding after a complement.

"Marie dit que B parce que A": A may justify B (inside Marie's report) or
the saying itself; the parser used to bind CAUSES(A -> dire) to the nearest
main clause and the flow projected it as the speaker's LINGUISTIC causal
claim. Within one sentence, a "car / parce que / puisque / donc" clause
after a complement (or a detached source) now fails closed like
"V que P et Q" (iteration 5): ambiguous attachment, no CAUSES relation, no
causal flow, claim never asserted. A sentence boundary ("... P. Donc Q.")
and plain causes ("B parce que A") are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_causal_flows


def _view(text):
    f = parse_utterance(text)
    claims = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    return f, claims, project_causal_flows(f)


@pytest.mark.parametrize("text", [
    "Marie dit que Nadia a arrêté Q parce que Paul a lancé P.",
    "Marie dit que Nadia a arrêté Q car Paul a lancé P.",
    "Marie croit que Nadia a arrêté Q puisque Paul a lancé P.",
    "Marie dit que Paul a lancé P donc Nadia a arrêté Q.",
    "Selon Marie, Nadia a arrêté Q parce que Paul a lancé P.",
])
def test_cause_after_a_complement_is_not_bound_to_the_nearest_host(text):
    f, claims, flows = _view(text)
    last = f.units[-1]
    assert (last.pragmatic, last.epistemic) == ("EMBEDDED", "UNRESOLVED_GOVERNANCE")
    assert f"coordination_attachment_ambiguous:{last.id}" in f.ambiguities
    assert not any(r.kind == "CAUSES" for r in f.relations) and flows == ()
    assert not (claims.get(last.id) or "").startswith("ASSERTED")


@pytest.mark.parametrize("text,src,tgt", [
    ("Nadia a arrêté Q parce que Paul a lancé P.", "u2", "u1"),
    ("Paul a lancé P donc Nadia a arrêté Q.", "u1", "u2"),
    ("Marie dit que Paul a lancé P. Donc Nadia a arrêté Q.", "u1", "u3"),
])
def test_plain_and_cross_sentence_causes_unchanged(text, src, tgt):
    f, _, flows = _view(text)
    assert ("CAUSES", src, tgt) in {(r.kind, r.source, r.target) for r in f.relations}
    assert [fl.relation_type for fl in flows] == ["CAUSES"]


def test_condition_consequent_unchanged():
    f, _, flows = _view("Si Marie dit que P a échoué, alors Nadia arrête Q.")
    assert [fl.relation_type for fl in flows] == ["CONDITIONS"]
