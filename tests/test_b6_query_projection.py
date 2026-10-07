"""B6 query-aware projection: deterministic, non-mutating, omissions recorded, unknown relevance kept."""
from __future__ import annotations

from app.harness.state_explicit.contracts import StateEntry, StateStatus, Visibility
from app.harness.state_explicit.projection import Relevance, project
from app.harness.state_explicit.registry import WorkingStateRegistry


def _registry():
    r = WorkingStateRegistry()
    r.register(StateEntry(state_id="build", state_type="NOTE", source_ref="t:build", payload={},
                          tags=("build", "ci"), visibility=Visibility.LONG))
    r.register(StateEntry(state_id="cuisine", state_type="NOTE", source_ref="t:cuisine", payload={},
                          tags=("recette",)))
    r.register(StateEntry(state_id="untagged", state_type="NOTE", source_ref="t:untagged", payload={}))
    r.register(StateEntry(state_id="hidden", state_type="NOTE", source_ref="t:hidden", payload={},
                          tags=("build",), visibility=Visibility.HIDE))
    r.register(StateEntry(state_id="unknown", state_type="NOTE", source_ref="t:unknown", payload={},
                          tags=("recette",), status=StateStatus.UNKNOWN))
    return r


def test_projection_selects_records_and_never_mutates():
    r = _registry()
    before = r.snapshot()
    p = project("Le build CI est rouge", r)
    assert r.snapshot() == before
    included = {i.state_id: i for i in p.included}
    omitted = {o.state_id: o.reason for o in p.omitted}
    assert included["build"].relevance == Relevance.RELEVANT and included["build"].exposure == Visibility.LONG
    assert omitted["cuisine"] == "irrelevant_to_query" and omitted["hidden"] == "visibility_hide"
    assert set(included) | set(omitted) == {e.state_id for e in r.list_entries()}


def test_unknown_relevance_is_not_irrelevance():
    p = project("Le build CI est rouge", _registry())
    item = next(i for i in p.included if i.state_id == "untagged")
    assert item.relevance == Relevance.UNKNOWN_RELEVANCE and item.exposure == Visibility.SHORT


def test_unknown_state_is_always_exposed():
    p = project("Le build CI est rouge", _registry())
    item = next(i for i in p.included if i.state_id == "unknown")
    assert item.reason == "unresolved_state_always_exposed"


def test_projection_is_deterministic():
    assert project("Le build CI est rouge", _registry()).to_dict() == \
        project("Le  BUILD ci est rouge", _registry()).to_dict()
