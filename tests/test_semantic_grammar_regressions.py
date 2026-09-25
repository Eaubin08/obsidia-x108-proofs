"""Regressions found on held-out sentences (not used to design the grammar)."""
from __future__ import annotations

import pytest

from app.semantic.lattice import parse_utterance


def _unit(frame, predicate):
    return next(u for u in frame.units if u.predicate == predicate)


# ── verb chains: reflexive / passive under a modal ───────────────────────
def test_reflexive_infinitive_stays_in_modal_chain():
    # Middle voice with a 3rd-person nominal subject: a requirement on the
    # artifact, not a request addressed to the agent.
    frame = parse_utterance("Le code du template doit s'exécuter et ses asserts passer.")
    u = _unit(frame, "EXECUTE")
    assert u.modality == "OBLIGATION"
    assert u.pragmatic == "ASSERTED"
    assert all(o.text != "s'" for x in frame.units for o in x.objects)
    assert "MUST" not in {x.predicate for x in frame.units}


def test_passive_under_modal():
    u = _unit(parse_utterance("le script doit être lancé"), "EXECUTE")
    assert u.verb_form == "PARTICIPLE"
    assert u.modality == "OBLIGATION"
    assert u.pragmatic == "ASSERTED"
