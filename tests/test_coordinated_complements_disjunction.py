"""EPI-1: "ou" after a complement follows the "et" contracts of iterations 4 and 5.

"Marie dit que P ou que Q": Q is P's sibling complement under the same unique
governor (REPORTS / BELIEVES / hearsay / unresolved governance), never a
relative of P; the siblings form one disjunction (ALTERNATIVE "ou que",
CoordinationRef OR "disjunction"). "Marie dit que P ou Q": Q's attachment is
ambiguous (inside the complement or with the host) and fails closed exactly
like "V que P et Q"; the host is never made an alternative of Q.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.language_flow_projection import project_epistemic_flows


def _view(text):
    f = parse_utterance(text)
    claims = {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}
    states = {x.source_object: x.state for x in project_epistemic_flows(f)}
    return f, claims, states


@pytest.mark.parametrize("gov,relation,state", [
    ("Marie dit que", "REPORTS", "REPORTED"),
    ("On dit que", "REPORTS", "REPORTED"),
    ("Marie croit que", "BELIEVES", "BELIEVED"),
    ("Marie pense que", "BELIEVES", "BELIEVED"),
])
def test_ou_que_sibling_shares_the_governor(gov, relation, state):
    f, claims, states = _view(f"{gov} Paul a lancé P ou que Nadia a exécuté Q.")
    ref_f, ref_claims, ref_states = _view(f"{gov} Paul a lancé P et que Nadia a exécuté Q.")
    host, p, q = f.units
    assert (q.pragmatic, q.epistemic, q.embedded_under) == (p.pragmatic, p.epistemic, host.id)
    assert (q.pragmatic, q.epistemic) == (ref_f.units[2].pragmatic, ref_f.units[2].epistemic)
    kinds = {(r.kind, r.source, r.target) for r in f.relations}
    assert {(relation, host.id, p.id), (relation, host.id, q.id), ("ALTERNATIVE", p.id, q.id)} <= kinds
    assert not any(r.evidence == "rel" for r in f.relations)
    (coord,) = f.coordinations
    assert (coord.kind, coord.construction, coord.members) == ("OR", "disjunction", (p.id, q.id))
    assert states[p.id] == states[q.id] == state
    assert claims[p.id] == claims[q.id] == "NO_ASSERTION" and claims[host.id] == ref_claims[host.id]


def test_hearsay_and_unresolved_governance_siblings():
    f, claims, states = _view("Il paraît que Paul a lancé P ou que Nadia a exécuté Q.")
    assert [u.epistemic for u in f.units] == ["HEARSAY", "HEARSAY"]
    assert all(c == "NO_ASSERTION" for c in claims.values())
    f, claims, _ = _view("Marie sait que Paul a lancé P ou que Nadia a exécuté Q.")
    assert [u.epistemic for u in f.units[1:]] == ["UNRESOLVED_GOVERNANCE"] * 2
    assert all(u.embedded_under == "u1" for u in f.units[1:])


def test_three_sibling_disjuncts_form_one_group():
    f, _, states = _view("Marie dit que Paul a lancé P ou que Nadia a exécuté Q ou que Luc a vérifié R.")
    (coord,) = f.coordinations
    assert coord.members == ("u2", "u3", "u4") and all(states[m] == "REPORTED" for m in coord.members)


@pytest.mark.parametrize("gov", ["Marie dit que", "Marie croit que", "Marie a appris que"])
def test_ou_without_que_after_a_complement_fails_closed(gov):
    f, claims, _ = _view(f"{gov} Paul a lancé P ou Nadia a exécuté Q.")
    ref_f, ref_claims, _ = _view(f"{gov} Paul a lancé P et Nadia a exécuté Q.")
    q = f.units[-1]
    assert (q.pragmatic, q.epistemic) == ("EMBEDDED", "UNRESOLVED_GOVERNANCE")
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    assert not any(r.kind == "ALTERNATIVE" for r in f.relations)
    assert claims[f.units[0].id] == ref_claims[ref_f.units[0].id]
    assert not claims[q.id].startswith("ASSERTED")


def test_et_que_contract_unchanged():
    f, _, _ = _view("Marie dit que Paul a lancé P et que Nadia a exécuté Q.")
    assert f.coordinations == () and ("COORDINATES", "u2", "u3") in {(r.kind, r.source, r.target) for r in f.relations}
