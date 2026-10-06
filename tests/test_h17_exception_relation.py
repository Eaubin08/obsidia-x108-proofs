"""H17 option A: EXCEPTS(exception, host): the host holds except when the exception holds.

Emitted only for one structural host ("Paul lance R sauf si / à moins que / excepté si Marie
lance P", preposed "Sauf si Marie lance P, lance R", "sauf quand"). Never CONDITIONS, CAUSES,
PREVENTS nor a negation; it creates no occurrence (host and exception stay UNRESOLVED), no
request, gate or constraint of its own. Several possible hosts (coordinated host) stay named
(exception_condition_open) and block closure; never the nearest. "sauf quand" keeps its
temporal reading held. A verbless exception ("sauf si P") has no unit: no relation, open.
"""
from __future__ import annotations

import pytest

from app.semantic.lattice.event_index import build_frame_event_index
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.ir_projection import governable_summary
from app.semantic.lattice.primitives import EMBEDDING_KINDS, TEMPORAL_KINDS, RelationKind


def _rels(f):
    return [(r.kind, r.source, r.target) for r in f.relations]


def _occ(f):
    return {e.predicate_ref: e.occurrence_claim.value for e in build_frame_event_index(f).events()}


def test_excepts_is_in_no_causal_temporal_or_embedding_family():
    assert RelationKind.EXCEPTS not in TEMPORAL_KINDS and RelationKind.EXCEPTS not in EMBEDDING_KINDS
    from app.semantic.lattice.projections import _CAUSAL
    assert RelationKind.EXCEPTS.value not in _CAUSAL


@pytest.mark.parametrize("text,exception,host,requested", [
    ("Paul lance R sauf si Marie lance P.", "u2", "u1", []),
    ("Paul lance R à moins que Marie lance P.", "u2", "u1", []),
    ("Lance R sauf si Marie lance P.", "u2", "u1", ["lance"]),
    ("Lance R excepté si Marie lance P.", "u2", "u1", ["lance"]),
    ("Sauf si Marie lance P, lance R.", "u1", "u2", ["lance"]),
])
def test_unique_host_excepts(text, exception, host, requested):
    f = parse_utterance(text)
    assert _rels(f) == [("EXCEPTS", exception, host)]
    assert _occ(f) == {"u1": "UNRESOLVED", "u2": "UNRESOLVED"}
    assert f.units[int(exception[1]) - 1].pragmatic == "HYPOTHETICAL"
    assert governable_summary(f)["requested_action_surfaces"] == requested and not f.constraints
    assert not any(a.startswith("exception_condition_open") for a in f.ambiguities) and f.closure


def test_negated_host_keeps_exact_prohibition():
    f = parse_utterance("Ne lance pas R sauf si Marie lance P.")
    assert _rels(f) == [("EXCEPTS", "u2", "u1")] and f.constraints == ("NO_EXECUTE(r)",)


def test_coordinated_host_stays_open():
    f = parse_utterance("Lance R et exécute Q sauf si Marie lance P.")
    assert not any(r[0] == "EXCEPTS" for r in _rels(f))
    assert "exception_condition_open:u3:host=u1,u2" in f.ambiguities and not f.closure


@pytest.mark.parametrize("text", ["Lance R sauf quand Marie lance P.", "Lance R excepté lorsque Marie lance P."])
def test_exception_when_keeps_temporal_hold(text):
    f = parse_utterance(text)
    assert _rels(f) == [("EXCEPTS", "u2", "u1")]
    assert f.closure_blockers == ("ambiguity:temporal_subordinate_open:u2",) and not f.closure


def test_verbless_exception_has_no_relation():
    f = parse_utterance("Lance R sauf si P.")
    assert _rels(f) == [] and not f.closure
