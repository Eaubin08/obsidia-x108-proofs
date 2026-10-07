"""B6 contracts: StateEntry is typed, addressable, bounded, immutable and non-sovereign."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.contracts import (BOUNDARY, StateEntry, StateStatus, Visibility, error_entry,
                                                  render_entry)


def _entry(**kw):
    base = dict(state_id="s1", state_type="NOTE", source_ref="test:s1", payload={"text": "bonjour"},
                provenance=("test",), tags=("note",))
    base.update(kw)
    return StateEntry(**base)


@pytest.mark.parametrize("field", ["state_id", "state_type", "source_ref"])
def test_identity_fields_are_required(field):
    with pytest.raises(ValueError):
        _entry(**{field: ""})


def test_entry_is_readonly_immutable_and_non_sovereign():
    e = _entry()
    assert e.readonly is True and e.boundary == BOUNDARY
    assert BOUNDARY["decision_authority"] == "KX108_ONLY"
    assert not any(BOUNDARY[k] for k in ("memory_write", "emits_act", "kernel_mutation",
                                         "allowed_to_decide", "allowed_to_act"))
    with pytest.raises(Exception):
        e.state_id = "other"
    p = e.payload
    p["text"] = "mutated"
    assert e.payload == {"text": "bonjour"}          # payload copies never write back


def test_payload_must_be_serializable_and_bounded():
    with pytest.raises(ValueError):
        _entry(payload={"x": object()})
    with pytest.raises(ValueError):
        _entry(payload={"x": "a" * 70_000})


def test_no_invented_timestamp():
    assert _entry().observed_at is None and "observed_at" not in _entry().to_dict()


def test_visibility_levels_and_hide_records_nothing_exposed():
    e = _entry(payload={"text": "x" * 5000})
    assert render_entry(e, Visibility.HIDE) is None
    short = render_entry(e, Visibility.SHORT)
    assert set(short) >= {"state_id", "state_type", "source_ref", "status"} and "payload" not in short
    long = render_entry(e, Visibility.LONG)
    assert long["payload_truncated"] is True and long["payload_chars"] > len(long["payload_preview"])
    full = render_entry(e, Visibility.FULL)
    assert full["payload"] == {"text": "x" * 5000}
    for view in (short, long, full):
        assert view["visibility_is_permission"] is False


def test_error_entry_keeps_failure_without_secret_text():
    e = error_entry("sens:err", "sens:parse", RuntimeError("password=hunter2"))
    assert e.status == StateStatus.ERROR and e.payload == {"error_type": "RuntimeError"}
    assert "hunter2" not in repr(e.to_dict())
