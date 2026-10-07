"""B6 WorkingStateRegistry: addressable, in-memory, duplicate fail-closed, no in-place mutation."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.contracts import StateEntry
from app.harness.state_explicit.registry import DuplicateStateError, WorkingStateRegistry


def _e(i):
    return StateEntry(state_id=f"s{i}", state_type="NOTE", source_ref=f"test:{i}", payload={"i": i})


def test_register_get_list_snapshot():
    r = WorkingStateRegistry()
    r.register(_e(1))
    r.register(_e(2))
    assert r.get("s2").payload == {"i": 2}
    assert [e.state_id for e in r.list_entries()] == ["s1", "s2"]
    snap = r.snapshot()
    assert [d["state_id"] for d in snap["entries"]] == ["s1", "s2"] and snap["durable_memory"] is False


def test_duplicate_state_id_fails_closed():
    r = WorkingStateRegistry()
    r.register(_e(1))
    with pytest.raises(DuplicateStateError):
        r.register(StateEntry(state_id="s1", state_type="NOTE", source_ref="other", payload={}))
    assert r.get("s1").source_ref == "test:1"


def test_unknown_id_fails_closed_and_listing_is_a_copy():
    r = WorkingStateRegistry()
    with pytest.raises(KeyError):
        r.get("missing")
    r.register(_e(1))
    entries = r.list_entries()
    assert isinstance(entries, tuple) and len(r.list_entries()) == 1


def test_only_state_entries_are_accepted():
    with pytest.raises(TypeError):
        WorkingStateRegistry().register({"state_id": "s1"})
