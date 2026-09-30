"""N14: "de sorte que" / "jusqu'à ce que" are subordinators, never relatives.

"sorte" (noun) and "ce" made "que" a relative attached to R: P became an
asserted relative of R, and "et exécute Q" a main head coordinated with R
(a main-clause request by proximity). They now open a subordinate with the
existing lost-governor contract (complement_governor_lost: P embedded,
unresolved governance, never asserted), and a coordinated member after it
takes the existing coordination_attachment_ambiguous contract (never
REQUESTED by proximity). Their final semantics are held (H05 / H11).
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.projections import ProjectionAxis, project


@pytest.mark.parametrize("conn", ["de sorte que", "jusqu'à ce que"])
def test_subordinator_is_not_a_relative_and_q_is_not_requested(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécute Q.")
    gate = {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}
    r, p, q = f.units
    assert (r.pragmatic, gate[r.id]) == ("REQUESTED", True)
    assert p.pragmatic != "ASSERTED" and f"complement_governor_lost:{p.id}" in f.ambiguities
    assert q.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} and not gate[q.id]
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    assert not any(x.kind == "COORDINATES" and q.id in (x.source, x.target) for x in f.relations)
    assert not f.closure


def test_noun_sorte_elsewhere_is_unchanged():
    f = parse_utterance("Lance la sorte de test.")
    assert not any(a.startswith("complement_governor_lost") for a in f.ambiguities)
