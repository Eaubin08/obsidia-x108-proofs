"""B6 SENS / Native Memory adapters: open semantics stay open, D1-D5 never promoted, readonly memory."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.contracts import StateStatus
from app.harness.state_explicit.memory_adapter import native_memory_state_entries
from app.harness.state_explicit.sens_adapter import sens_state_entries


def _frame(text):
    (e,) = sens_state_entries(text)
    return e


def test_closed_utterance_is_known():
    e = _frame("Paul lance P.")
    assert e.status == StateStatus.KNOWN and e.payload["semantic_closure"]["closed"] is True
    assert e.payload["raw"] == "Paul lance P." and e.uncertainty == ()


@pytest.mark.parametrize("text", [
    "Paul et Nadia qui lancent P échouent.",                          # D1
    "Le fichier que Marie l'ouvre disparaît.",                        # D3
    "Si le script qui teste P échoue, lance R.",                      # D4
    "Selon Marie, si le script qui teste P échoue, lance R.",         # D5
    "Lance P et ne lance pas P.",                                     # contradiction
    "Lance-le.",                                                      # unresolved reference
])
def test_open_sens_state_is_preserved_never_promoted(text):
    e = _frame(text)
    assert e.status == StateStatus.OPEN and "sens_open" in e.tags
    assert e.payload["semantic_closure"]["closed"] is False and e.uncertainty
    p = e.payload
    kept = set(p["missing"]) | set(p["ambiguities"]) | set(p["unresolved_references"]) | set(p["contradictions"])
    assert kept and kept <= set(e.uncertainty)
    assert p["requested_is_authorized"] is False


def test_parser_failure_becomes_an_error_entry(monkeypatch):
    import app.harness.state_explicit.sens_adapter as mod

    def boom(_):
        raise RuntimeError("secret")
    monkeypatch.setattr(mod, "parse_utterance", boom)
    (e,) = mod.sens_state_entries("Lance P.")
    assert e.status == StateStatus.ERROR and "secret" not in repr(e.to_dict())


def test_native_memory_snapshot_is_converted_readonly():
    snap = {"status": "OK", "selected_items": [
        {"id": "nm-1", "title": "Build", "tags": ["build"], "excerpt": "texte", "source_ref": "native:nm-1",
         "score": 3, "path": "docs/x.md"},
        {"title": "sans id"}]}
    entries = native_memory_state_entries(snap)
    assert [e.status for e in entries] == [StateStatus.KNOWN, StateStatus.ERROR]
    assert entries[0].state_id == "native_memory:nm-1" and entries[0].source_ref == "native:nm-1"
    assert entries[0].payload["memory_write"] is False


def test_native_memory_not_required_gives_no_entry_and_unknown_status_is_kept():
    assert native_memory_state_entries({"status": "MEMORY_NOT_REQUIRED", "selected_items": []}) == ()
    (e,) = native_memory_state_entries({"status": "MEMORY_INDEX_UNAVAILABLE", "selected_items": []})
    assert e.status == StateStatus.UNKNOWN
