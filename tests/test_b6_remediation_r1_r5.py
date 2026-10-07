"""B6-D remediation: complete SENS frame (R1), state-only instruction activation (R2), hard resource
bounds (R3), canonical replay (R4), strict JSON (R5)."""
from __future__ import annotations

import dataclasses
import json
import math

import pytest

from app.harness.state_explicit import contracts as C
from app.harness.state_explicit.context_assembly import assemble_context
from app.harness.state_explicit.contracts import StateEntry, StateStatus, error_entry
from app.harness.state_explicit.registry import WorkingStateRegistry
from app.harness.state_explicit.sens_adapter import sens_state_entries
from app.semantic.lattice.french_grammar import parse_utterance
from app.semantic.lattice.primitives import UtteranceFrame

_M = {"categories": ["PURE_RESPONSE"], "matrix": {"PURE_RESPONSE": {"brody_may": ["repondre"]}}}


def _reg(*entries):
    r = WorkingStateRegistry()
    for e in entries:
        r.register(e)
    return r


def _e(i, **kw):
    base = dict(state_id=f"s{i:03d}", state_type="NOTE", source_ref=f"t:{i}", payload={"i": i}, tags=("build",))
    base.update(kw)
    return StateEntry(**base)


# ── R1: every canonical frame field is preserved ────────────────────────────
_FIELDS = [f.name for f in dataclasses.fields(UtteranceFrame)]


@pytest.mark.parametrize("text", ["Paul lance P.", "Si le script qui teste P échoue, lance R.",
                                  "Paul et Nadia ont chacun lancé lentement P.", "Ne lance pas P.",
                                  "Lance P et ne lance pas P.", "Lance-le maintenant.",
                                  "Selon Marie, Paul a lancé P."])
def test_r1_complete_semantic_frame(text):
    (e,) = sens_state_entries(text)
    sf = e.payload["semantic_frame"]
    assert set(_FIELDS) <= set(sf)
    f = parse_utterance(text)
    for name in ("participant_configurations", "manner_modifiers", "constraints", "operator_scopes", "deixis",
                 "presupposed_referents", "evidence_needs", "oblique_arguments", "surface_act"):
        value = getattr(f, name)
        assert (len(sf[name]) == len(value)) if isinstance(value, tuple) else sf[name] == value


def test_r1_nested_unit_fields_kept():
    (e,) = sens_state_entries("Paul lance lentement P et Q.")
    unit = e.payload["semantic_frame"]["units"][0]
    assert {"lemma", "subject", "objects", "provenance"} <= set(unit)
    assert [a["text"] for a in unit["objects"]] == ["p", "q"]


# ── R2: query text never activates state instructions ───────────────────────
def _instr(query, *entries):
    return {i["instruction_id"] for i in assemble_context(query, _reg(*entries), capability_matrix=_M).instructions}


@pytest.mark.parametrize("query", ["error unknown", "memory authority blocked", "native memory error open"])
def test_r2_query_words_activate_nothing(query):
    assert _instr(query, _e(1)) == {"boundary_advisory_only"}


def test_r2_actual_state_activates():
    assert "state_error_visible" in _instr("x", error_entry("err", "t:src", RuntimeError()))
    assert "state_error_visible" in _instr("x", _e(2, status=StateStatus.UNKNOWN))


def test_r2_content_tags_activate_nothing():
    assert _instr("build", _e(3, tags=("build", "error", "sens_open", "native_memory"))) == {"boundary_advisory_only"}


# ── R3: hard bounds ─────────────────────────────────────────────────────────
def test_r3_query_bound():
    assemble_context("a" * C.MAX_QUERY_CHARS, _reg(_e(1)), capability_matrix=_M)
    with pytest.raises(C.ContextBoundError):
        assemble_context("a" * (C.MAX_QUERY_CHARS + 1), _reg(_e(1)), capability_matrix=_M)


def test_r3_entry_bound():
    p = assemble_context("build", _reg(*[_e(i) for i in range(C.MAX_STATE_ENTRIES)]), capability_matrix=_M)
    assert len(p.projection["included"]) == C.MAX_STATE_ENTRIES
    p = assemble_context("build", _reg(*[_e(i) for i in range(C.MAX_STATE_ENTRIES + 1)]), capability_matrix=_M)
    over = [o for o in p.omitted if o["reason"] == "ENTRY_LIMIT"]
    assert [o["state_id"] for o in over] == [f"s{C.MAX_STATE_ENTRIES:03d}"]


def test_r3_packet_bound_and_overflow_recorded():
    big = [_e(i, payload={"t": "x" * 60_000}, visibility="FULL") for i in range(C.MAX_STATE_ENTRIES)]
    p = assemble_context("build", _reg(*big), capability_matrix=_M)
    assert len(p.to_json().encode("utf-8")) <= C.MAX_PACKET_BYTES
    reasons = {o["reason"] for o in p.omitted} | {i["reason"] for i in p.projection["included"]}
    assert "PACKET_SIZE_LIMIT" in reasons or "PACKET_SIZE_LIMIT:reduced_to_SHORT" in reasons
    ids = {i["state_id"] for i in p.projection["included"]} | {o["state_id"] for o in p.omitted}
    assert ids == {e.state_id for e in big}


# ── R4: canonical replay ────────────────────────────────────────────────────
def test_r4_insertion_order_independent():
    a, b, c = _e(1), _e(2), _e(3)
    assert assemble_context("build", _reg(a, b, c), capability_matrix=_M).packet_id == \
        assemble_context("build", _reg(c, a, b), capability_matrix=_M).packet_id
    assert assemble_context("build", _reg(a, b, c), capability_matrix=_M).to_json() == \
        assemble_context("build", _reg(c, a, b), capability_matrix=_M).to_json()


def test_r4_changed_content_changes_id():
    assert assemble_context("build", _reg(_e(1)), capability_matrix=_M).packet_id != \
        assemble_context("build", _reg(_e(1, payload={"i": 99}), ), capability_matrix=_M).packet_id


# ── R5: strict JSON ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, {1: "a"}, {"a": {2: "b"}}, b"x", {1, 2}, object()])
def test_r5_strict_json_rejected(bad):
    with pytest.raises(ValueError):
        StateEntry(state_id="s", state_type="T", source_ref="x", payload={"v": bad})


def test_r5_recursive_rejected_and_canonical_json_strict():
    loop: list = []
    loop.append(loop)
    with pytest.raises(ValueError):
        StateEntry(state_id="s", state_type="T", source_ref="x", payload=loop)
    with pytest.raises(ValueError):
        C.canonical_json({"v": math.nan})
    assert json.loads(C.canonical_json({"b": 1, "a": [1.5, None, True]})) == {"a": [1.5, None, True], "b": 1}


def test_input_mutation_after_construction_has_no_effect():
    src = {"a": [1]}
    e = StateEntry(state_id="s", state_type="T", source_ref="x", payload=src)
    src["a"].append(2)
    assert e.payload == {"a": [1]}
