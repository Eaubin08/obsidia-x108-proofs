"""G2: a negated obligation is never shared positively onto a coordinated infinitive.

"Paul ne doit pas lancer P et exécuter Q": the obligation modal chain was
shared like a positive one, and Q (with no negation of its own) became a
positive OBLIGATION: "Paul must execute Q", a polarity the speaker never
uttered. With a second-person or impersonal host ("Tu ne dois pas ...",
"Il ne faut pas ...") Q even became an independent gated request.

¬(P∧Q), ¬P∧¬Q or another reading is held doctrine (H01): neither the
positive obligation nor the negation is copied; Q stays content under that
exact negated operator unit (negated_scope_open), never a request, and
closure stays open. The positive shared obligation is unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

_REQ = {"REQUESTED", "INDIRECT_REQUEST", "FORBIDDEN"}


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("text", [
    "Paul ne doit pas lancer P et exécuter Q.",
    "Paul ne devrait pas lancer P et exécuter Q.",
    "Paul ne doit pas lancer P, exécuter Q.",
    "Paul ne doit pas lancer P ou exécuter Q.",
    "Tu ne dois pas lancer P et exécuter Q.",
    "Il ne faut pas lancer P et exécuter Q.",
    "Je ne dois pas lancer P et exécuter Q.",
])
def test_member_under_negated_obligation_is_open_content(text):
    f = parse_utterance(text)
    host = f.units[0]
    (q,) = [u for u in f.units if u.lemma == "exécuter"]
    assert (host.lemma, host.modality, host.polarity) == ("lancer", "OBLIGATION", "negative")
    assert [a.head for a in q.objects] == ["q"]
    assert q.modality is None                          # positive obligation not copied
    assert (q.polarity, q.negator) == ("positive", None)  # negation not copied either
    assert q.pragmatic == "EMBEDDED" and q.pragmatic not in _REQ and not _gate(f)[q.id]
    assert q.embedded_under == host.id
    assert f"negated_scope_open:{q.id}" in f.ambiguities
    assert not any(c.construction == "shared_modality" for c in f.coordinations)
    assert "EXECUTE" not in governable_summary(f)["requested_world_actions"]
    assert not f.closure


def test_host_prohibition_is_kept():
    f = parse_utterance("Tu ne dois pas exécuter P et lancer Q.")
    assert f.units[0].pragmatic == "FORBIDDEN" and "NO_EXECUTE(p)" in f.constraints


@pytest.mark.parametrize("text", ["Paul doit lancer P et exécuter Q.", "Tu dois lancer P et exécuter Q.",
                                  "Il faut lancer P et exécuter Q."])
def test_positive_obligation_is_still_shared(text):
    f = parse_utterance(text)
    assert any(c.construction == "shared_modality" for c in f.coordinations)
    assert all(u.modality == "OBLIGATION" and u.polarity == "positive" for u in f.units)
    assert not any(a.startswith("negated_scope_open") for a in f.ambiguities)


def test_member_with_its_own_negation_under_positive_obligation_is_unchanged():
    f = parse_utterance("Paul doit lancer P et ne pas exécuter Q.")
    q = f.units[1]
    assert (q.modality, q.polarity) == ("OBLIGATION", "negative")
