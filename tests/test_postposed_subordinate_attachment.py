"""N9 + N9b: postposed "avant que / après que / sans que" never attach by proximity.

N9: after a postposed temporal or "sans que" subordinate, a coordinated
member ("Lance R avant que Paul lance P et exécute Q") became a main-clause
request by proximity. The G5-R contract now covers these subordinates:
- morphology leaves only the main imperative (CASE A): REQUESTED, gated;
- subordinate continuation or main request both possible (CASE B): never
  REQUESTED, possible request exposed, coordination_attachment_ambiguous;
- only the subordinate continuation licensed (CASE C): no request.

N9b: "R et Q avant que P", "R puis Q après que P": the temporal relation
targeted the nearest head. With several possible hosts no PRECEDES target is
chosen; temporal_scope_ambiguous names the subordinate and its hosts, and
the subordinate keeps its temporal (non-asserted, never conditional)
occurrence. TEMPORALITY != CONDITION: condition_scope_ambiguous is not
reused. Single-host temporal subordinates are unchanged.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.projections import ProjectionAxis, project

CONNS = ["avant que", "après que", "sans que"]


def _gate(f):
    return {k: v["requires_gate"] for k, v in project(f, ProjectionAxis.AUTHORITY).items()}


def _claims(f):
    return {c.predicate_ref: c.occurrence_claim.value for c in build_frame_event_index(f).events()}


@pytest.mark.parametrize("conn", CONNS)
def test_case_b_member_is_a_possible_request_only(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécute Q.")
    q = f.units[-1]
    assert q.lemma == "exécuter" and (q.pragmatic, q.role) == ("EMBEDDED", "REQUEST") and not _gate(f)[q.id]
    assert q.surface in governable_summary(f)["requested_action_surfaces"]
    assert f"coordination_attachment_ambiguous:{q.id}" in f.ambiguities and not f.closure
    assert not any(x.kind == "COORDINATES" and q.id in (x.source, x.target) for x in f.relations)


@pytest.mark.parametrize("conn", CONNS)
def test_case_a_forced_main_imperative_is_a_request(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécutez Q.")
    q = f.units[-1]
    assert (q.pragmatic, _gate(f)[q.id]) == ("REQUESTED", True)


@pytest.mark.parametrize("conn", CONNS)
def test_case_c_subordinate_only_member_is_no_request(conn):
    f = parse_utterance(f"Lance R {conn} Paul lance P et exécutent Q.")
    q = f.units[-1]
    assert q.pragmatic not in {"REQUESTED", "INDIRECT_REQUEST"} and not _gate(f)[q.id]
    assert q.surface not in governable_summary(f)["requested_action_surfaces"]


@pytest.mark.parametrize("text,link", [
    ("Lance R et exécute Q avant que Paul lance P.", "COORDINATES"),
    ("Lance R puis exécute Q avant que Paul lance P.", "PRECEDES"),
    ("Lance R et exécute Q après que Paul a lancé P.", "COORDINATES"),
])
def test_temporal_scope_over_a_coordination_is_named_not_chosen(text, link):
    f = parse_utterance(text)
    r, q, p = f.units
    assert not any(x.kind == "PRECEDES" and p.id in (x.source, x.target) for x in f.relations)
    assert f"temporal_scope_ambiguous:{p.id}:host={r.id},{q.id}" in f.ambiguities
    assert not any(a.startswith("condition_scope_ambiguous") for a in f.ambiguities)
    assert _claims(f)[p.id] == "NO_ASSERTION" and not f.closure             # temporal, never asserted
    assert (link, r.id, q.id) in {(x.kind, x.source, x.target) for x in f.relations}


@pytest.mark.parametrize("text,rel", [("Lance R avant que Paul lance P.", ("PRECEDES", "u1", "u2")),
                                      ("Lance R après que Paul a lancé P.", ("PRECEDES", "u2", "u1"))])
def test_single_host_temporal_subordinate_is_unchanged(text, rel):
    f = parse_utterance(text)
    assert rel in {(x.kind, x.source, x.target) for x in f.relations}
    assert not any(a.startswith("temporal_scope_ambiguous") for a in f.ambiguities)
