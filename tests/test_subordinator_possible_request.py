"""N16: after "de sorte que / jusqu'à ce que", Q keeps its possible main-clause request.

N14 made the member after these subordinators ambiguous (lost-governor
contract) but, unlike G5-R, dropped its possible main-clause request reading
from runtime. The G5-R contract now applies after them too:
- CASE A, only the main imperative is possible: REQUESTED, gated;
- CASE B, subordinate continuation or main request: EMBEDDED, role REQUEST,
  exposed as a possible request, coordination_attachment_ambiguous;
- CASE C, only the subordinate continuation: no request exposure.
P stays a non-asserted lost-governor complement; no relation by proximity.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

CONNS = ["de sorte que", "jusqu'à ce que"]


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


@pytest.mark.parametrize("conn", CONNS)
def test_case_b_possible_request_is_exposed(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécute Q.")
    r, p, q = f.units
    assert (q.pragmatic, q.role) == ("EMBEDDED", "REQUEST") and not _gate(f)[q.id]
    assert q.surface in governable_summary(f)["requested_action_surfaces"]
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities
    assert p.pragmatic != "ASSERTED" and f"complement_governor_lost:{p.id}" in f.ambiguities
    assert not any(x.kind in {"CONDITIONS", "PRECEDES"} for x in f.relations) and not f.closure


@pytest.mark.parametrize("conn", CONNS)
def test_case_a_forced_main_imperative_is_a_request(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécutez Q.")
    q = f.units[-1]
    assert (q.pragmatic, _gate(f)[q.id]) == ("REQUESTED", True)


@pytest.mark.parametrize("conn", CONNS)
def test_case_c_subordinate_only_is_no_request(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécutent Q.")
    q = f.units[-1]
    assert q.surface not in governable_summary(f)["requested_action_surfaces"] and not _gate(f)[q.id]
