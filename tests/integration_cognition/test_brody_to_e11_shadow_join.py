"""E11 REAL RUNTIME JOIN: Brody Memory Producer -> E11 Cognition Shadow Consumer.

Phase RED contract test suite:
Verifies the minimal contract for wiring the native memory retrieval snapshot
produced in the Brody pipeline into the certified E11 cognition shadow consumer
(app.integration.cognition_shadow_memory_v0.run_cognition_shadow_with_memory).

Requirements tested:
R1  - Exactly one retrieval per request when MEMZUM requires memory.
R2  - Zero second retrieval executed by the E11 connection.
R3  - Raw snapshot schema is strictly OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1.
R4  - BRODY_NATIVE_MEMORY_RESPONSE_V1 envelope is rejected by E11 and never passed as raw snapshot.
R5  - Historic Brody W3/W4 behavior and memory_response_chain preserved.
R6  - ContextPacketV2 (W4) remains distinct from B6 ContextPacket (E11).
R7  - MEMZUM memory_required=False preserved with zero index load.
R8  - All legitimate memory statuses preserved and handled.
R9  - B7 detector applied strictly to SENS StateEntry, never to memory entries.
R10 - No decision, execution, verdict or promotion authority (KX108_ONLY).
R11 - No memory write, no canonical write, no B10 persistence.
R12 - No raw memory content leaked to public response.
R13 - Shadow V0 and certified E11 files untouched.
R14 - Explicit error propagation when snapshot is corrupt / degraded.
R15 - Determinism, provenance, and output compatibility.
R16 - Response adapter signature supports precomputed_retrieval.
"""
from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from app.cognition.b7.detector import detect_unresolved
from app.harness.state_explicit import assemble_context, ContextPacket
from app.harness.state_explicit.contracts import ContextBoundError, canonical_json
from app.harness.state_explicit.registry import DuplicateStateError
from app.integration.cognition_shadow_memory_v0 import (
    BOUNDARY_KEYS,
    RESPONSE_ENVELOPE_KEYS,
    SCHEMA as E11_SCHEMA,
    SNAPSHOT_SCHEMA,
    run_cognition_shadow_with_memory,
)
from apps.obsidia_api.brody_native_memory_response_adapter import (
    build_native_memory_response,
)
from apps.obsidia_api.brody_obsidia_native_memory import (
    NATIVE_MEMORY_BOUNDARY,
    build_native_memory_retrieval_snapshot,
    load_native_memory_index,
)
from apps.obsidia_api.routes.brody import BrodyChatRequest, brody_chat


# ---------------------------------------------------------------------------
# Helpers & Fixtures
# ---------------------------------------------------------------------------

def _make_sample_item(native_id: str = "doc_test_01", rank: int = 1) -> dict[str, Any]:
    return {
        "id": native_id,
        "rank": rank,
        "title": f"Document {native_id}",
        "source": "OBSIDIA_NATIVE_MEMORY_V1",
        "path": f"docs/{native_id}.md",
        "tags": ["b6", "kernel"],
        "score": 100 - rank,
        "excerpt": "Ceci est un extrait de memoire native pour test.",
        "source_ref": f"native:{native_id}",
        "readonly": True,
        "memory_write": False,
        "emits_act": False,
        "decision_authority": "KX108_ONLY",
    }


def _make_raw_retrieval_snapshot(
    query: str = "test native memory",
    status: str = "MEMORY_USABLE",
    items: list[dict[str, Any]] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    selected = items if items is not None else [_make_sample_item()]
    snap = {
        "schema_version": SNAPSHOT_SCHEMA,
        "source_type": "OBSIDIA_NATIVE_MEMORY_V1",
        "query": query,
        "query_normalized": query.lower(),
        "memory_required": status != "MEMORY_NOT_REQUIRED",
        "selected_items_count": len(selected),
        "selected_items": selected,
        "index_record_count": 10,
        "status": status,
        "material_quality": "USABLE_MATERIAL" if selected else "NO_MATERIAL",
        **NATIVE_MEMORY_BOUNDARY,
    }
    snap.update(extra)
    return snap


@pytest.fixture
def fast_brody_chat(monkeypatch: pytest.MonkeyPatch):
    """Monkeypatch slow outer response pipeline to keep tests fast, local, and provider-free."""
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.run_brody_real_response_pipeline",
        lambda **kwargs: {
            "response_md": "Mock Brody response md",
            "response": "Mock Brody response",
            "context_packet": {},
            "action_risk": False,
            "source": "MOCK_BACKEND",
        },
    )


# ---------------------------------------------------------------------------
# Test Suite: R1 - R16
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_r1_single_retrieval_when_memory_required(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R1: Exactly one memory retrieval must occur per request when MEMZUM requires it.

    The produced raw snapshot must be delivered to both the response adapter
    and the certified E11 cognition shadow consumer without duplicate retrieval,
    sharing the exact same immutable raw retrieval snapshot across both boundaries.
    """
    call_counts = {"retrieval": 0, "index": 0}
    captured_snapshots: dict[str, Any] = {
        "produced_snapshot_ref": None,
        "produced_snapshot_canonical": None,
        "adapter_snapshot_ref": None,
        "adapter_snapshot_canonical": None,
        "e11_snapshot_ref": None,
        "e11_snapshot_canonical": None,
    }
    orig_retrieval = build_native_memory_retrieval_snapshot

    def spy_retrieval(*args, **kwargs):
        call_counts["retrieval"] += 1
        snap = orig_retrieval(*args, **kwargs)
        captured_snapshots["produced_snapshot_ref"] = snap
        captured_snapshots["produced_snapshot_canonical"] = canonical_json(copy.deepcopy(snap))
        return snap

    orig_adapter = build_native_memory_response

    def spy_adapter(*args, **kwargs):
        snap = kwargs.get("precomputed_retrieval")
        if snap is not None:
            captured_snapshots["adapter_snapshot_ref"] = snap
            captured_snapshots["adapter_snapshot_canonical"] = canonical_json(copy.deepcopy(snap))
        return orig_adapter(*args, **kwargs)

    orig_shadow = run_cognition_shadow_with_memory

    def spy_shadow(text, memory_snapshot, *args, **kwargs):
        captured_snapshots["e11_snapshot_ref"] = memory_snapshot
        captured_snapshots["e11_snapshot_canonical"] = canonical_json(copy.deepcopy(memory_snapshot))
        return orig_shadow(text, memory_snapshot, *args, **kwargs)

    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.build_native_memory_retrieval_snapshot",
        spy_retrieval,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_native_memory_response_adapter.build_native_memory_retrieval_snapshot",
        spy_retrieval,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.build_native_memory_retrieval_snapshot",
        spy_retrieval,
        raising=False,
    )

    monkeypatch.setattr(
        "apps.obsidia_api.brody_native_memory_response_adapter.build_native_memory_response",
        spy_adapter,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.build_native_memory_response",
        spy_adapter,
        raising=False,
    )

    monkeypatch.setattr(
        "app.integration.cognition_shadow_memory_v0.run_cognition_shadow_with_memory",
        spy_shadow,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.run_cognition_shadow_with_memory",
        spy_shadow,
        raising=False,
    )

    # Dynamically patch any cached or aliased references to build_native_memory_retrieval_snapshot and run_cognition_shadow_with_memory
    import apps.obsidia_api.routes.brody as brody_mod
    for name, val in list(brody_mod.__dict__.items()):
        if callable(val) and getattr(val, "__code__", None) is orig_retrieval.__code__:
            monkeypatch.setattr(brody_mod, name, spy_retrieval)
        if callable(val) and getattr(val, "__code__", None) is orig_shadow.__code__:
            monkeypatch.setattr(brody_mod, name, spy_shadow)

    # Alias-safe code-object execution profiler with profiler-masking resilience
    orig_setprofile = sys.setprofile
    retrieval_code = orig_retrieval.__code__
    real_retrieval_calls = []

    def code_profiler(frame, event, arg):
        if event == "call" and frame.f_code is retrieval_code:
            real_retrieval_calls.append(frame)

    def chained_setprofile(new_prof):
        if new_prof is None or new_prof is code_profiler:
            orig_setprofile(code_profiler)
        else:
            def combined(frame, event, arg):
                code_profiler(frame, event, arg)
                try:
                    new_prof(frame, event, arg)
                except Exception:
                    pass
            orig_setprofile(combined)

    prev_prof = sys.getprofile()
    orig_setprofile(code_profiler)
    monkeypatch.setattr(sys, "setprofile", chained_setprofile)
    try:
        req = BrodyChatRequest(
            message="Que dit le kernel b6 sur la memoire native ?",
            language="fr",
            session_id="test_r1_single_retrieval",
            compact=False,
            debug=True,
        )
        result = await brody_chat(req)
    finally:
        orig_setprofile(prev_prof)

    # In GREEN, build_native_memory_retrieval_snapshot is called exactly once across the request window
    assert call_counts["retrieval"] == 1, (
        f"Expected exactly 1 retrieval call, got {call_counts['retrieval']}"
    )
    assert len(real_retrieval_calls) == 1, (
        f"Code-object profiler detected {len(real_retrieval_calls)} executions of build_native_memory_retrieval_snapshot (expected exactly 1)"
    )

    # E11 shadow output must be attached to the cognitive runtime receipt
    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "E11 cognition_shadow_memory must be attached in cognitive_runtime_receipt"
    assert shadow.get("schema") == E11_SCHEMA

    assert captured_snapshots["produced_snapshot_ref"] is not None, "Retrieval snapshot was not produced"

    # Verify both consumers received the raw retrieval snapshot at their boundaries
    adapter_snap = captured_snapshots["adapter_snapshot_ref"]
    e11_snap = captured_snapshots["e11_snapshot_ref"]
    assert adapter_snap is not None, (
        "Consumer A (Brody response adapter) did not receive a retrieval snapshot"
    )
    assert e11_snap is not None, (
        "Consumer B (Certified E11 shadow consumer) did not receive a retrieval snapshot"
    )

    # Both must be raw retrieval snapshots, never response envelopes
    assert adapter_snap.get("schema_version") == SNAPSHOT_SCHEMA
    assert e11_snap.get("schema_version") == SNAPSHOT_SCHEMA
    assert not any(k in e11_snap for k in RESPONSE_ENVELOPE_KEYS)

    # Content invariance at the moment of consumer invocation:
    # Neither consumer may receive a mutated or altered snapshot
    prod_canonical = captured_snapshots["produced_snapshot_canonical"]
    e11_canonical = captured_snapshots["e11_snapshot_canonical"]
    adapter_canonical = captured_snapshots["adapter_snapshot_canonical"]
    assert e11_canonical == prod_canonical, (
        "Snapshot content delivered to E11 differed from produced snapshot"
    )
    assert adapter_canonical == prod_canonical, (
        "Snapshot content delivered to Brody adapter differed from produced snapshot (mutation detected)"
    )
    assert e11_canonical == adapter_canonical, (
        "Consumers A and B received divergent snapshot contents across the integration seam"
    )

    # Post-execution invariance: no in-place mutation occurred after dispatch
    assert canonical_json(adapter_snap) == prod_canonical, (
        "Adapter snapshot was mutated in-place after dispatch"
    )
    assert canonical_json(e11_snap) == prod_canonical, (
        "E11 snapshot was mutated in-place after dispatch"
    )

    # Shared identity: both must reference the exact same in-memory object instance
    assert adapter_snap is e11_snap, "Both consumers must share direct in-memory snapshot reference"
    assert adapter_snap is captured_snapshots["produced_snapshot_ref"], (
        "Both consumers must receive the exact produced in-memory snapshot instance"
    )


def test_r2_zero_second_retrieval_by_e11(monkeypatch: pytest.MonkeyPatch):
    """R2: E11 connection executes zero retrieval on its own (no duplicate I/O)."""
    call_counts = {"retrieval": 0, "index": 0}

    def fail_retrieval(*args, **kwargs):
        call_counts["retrieval"] += 1
        raise AssertionError("E11 consumer must never call build_native_memory_retrieval_snapshot")

    def fail_index(*args, **kwargs):
        call_counts["index"] += 1
        raise AssertionError("E11 consumer must never call load_native_memory_index")

    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.build_native_memory_retrieval_snapshot",
        fail_retrieval,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.load_native_memory_index",
        fail_index,
    )

    raw_snapshot = _make_raw_retrieval_snapshot()
    out = run_cognition_shadow_with_memory("Que dit le kernel b6 ?", raw_snapshot)

    assert out["schema"] == E11_SCHEMA
    assert call_counts["retrieval"] == 0
    assert call_counts["index"] == 0


@pytest.mark.asyncio
async def test_r3_raw_snapshot_schema_is_obsidia_native_memory_retrieval_v1(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R3: The raw snapshot passed to E11 must have schema OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 sur la memoire native ?",
        language="fr",
        session_id="test_r3_schema",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "cognition_shadow_memory must be present"
    ref = shadow.get("memory_snapshot_ref", {})
    assert ref.get("schema_version") == SNAPSHOT_SCHEMA


def test_r4_brody_response_envelope_never_passed_to_e11_as_raw_snapshot():
    """R4: BRODY_NATIVE_MEMORY_RESPONSE_V1 envelope must be rejected by E11 with ValueError."""
    response_envelope = build_native_memory_response(
        user_message="Que dit le kernel b6 ?",
        memory_required=True,
    )
    assert response_envelope["schema_version"] == "BRODY_NATIVE_MEMORY_RESPONSE_V1"
    assert any(k in response_envelope for k in RESPONSE_ENVELOPE_KEYS)

    with pytest.raises(ValueError, match="schema_version must be OBSIDIA_NATIVE_MEMORY_RETRIEVAL_V1|envelope rejected"):
        run_cognition_shadow_with_memory("Que dit le kernel b6 ?", response_envelope)


@pytest.mark.asyncio
async def test_r5_preservation_of_historic_brody_w3_w4_and_memory_response_chain(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R5: Historical Brody W3/W4 behavior, response_md, and memory_response_chain are preserved."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r5_historic",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    assert "response_md" in result
    cog_receipt = result.get("cognitive_runtime_receipt", {})
    components = cog_receipt.get("components", {})
    assert "W4_MEMORY_RETRIEVAL" in components
    assert "W3_BRODY" in components


@pytest.mark.asyncio
async def test_r6_preservation_of_context_packet_v2_distinct_from_b6_context_packet(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R6: ContextPacketV2 (W4) remains distinct from B6 ContextPacket (E11),
    and genuine E11/B6 causal execution is verified across the route for short requests.
    """
    orig_shadow = run_cognition_shadow_with_memory
    shadow_code = orig_shadow.__code__
    assemble_code = assemble_context.__code__

    observed_shadow_calls: list[Any] = []
    observed_assemble_calls: list[Any] = []

    def b6_profiler(frame, event, arg):
        if event == "call":
            if frame.f_code is shadow_code:
                observed_shadow_calls.append(frame)
            elif frame.f_code is assemble_code:
                observed_assemble_calls.append(frame)

    orig_setprofile = sys.setprofile

    def chained_setprofile(new_prof):
        if new_prof is None or new_prof is b6_profiler:
            orig_setprofile(b6_profiler)
        else:
            def combined(frame, event, arg):
                b6_profiler(frame, event, arg)
                try:
                    new_prof(frame, event, arg)
                except Exception:
                    pass
            orig_setprofile(combined)

    # Dynamically patch any cached or aliased references to run_cognition_shadow_with_memory
    import apps.obsidia_api.routes.brody as brody_mod
    for name, val in list(brody_mod.__dict__.items()):
        if callable(val) and getattr(val, "__code__", None) is orig_shadow.__code__:
            monkeypatch.setattr(brody_mod, name, orig_shadow)

    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",  # Short normal-route request (len 23 <= 40)
        language="fr",
        session_id="test_r6_context_packets",
        compact=False,
        debug=True,
    )

    prev_prof = sys.getprofile()
    orig_setprofile(b6_profiler)
    monkeypatch.setattr(sys, "setprofile", chained_setprofile)
    try:
        result = await brody_chat(req)
    finally:
        orig_setprofile(prev_prof)

    # Verify genuine causal execution of E11 and B6 assemble_context for short request
    assert len(observed_shadow_calls) == 1, (
        f"Genuine run_cognition_shadow_with_memory was not executed during route for short request "
        f"'{req.message}' (detected {len(observed_shadow_calls)} calls). Forged packet branch rejected."
    )
    assert len(observed_assemble_calls) >= 1, (
        f"Genuine assemble_context was not executed during B6 context assembly (detected {len(observed_assemble_calls)} calls)"
    )

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    v2_packet = cog_receipt.get("context_packet_v2")
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")

    assert v2_packet is not None, "ContextPacketV2 must exist in receipt"
    assert shadow is not None, "E11 shadow must exist in receipt"

    e11_packet = shadow.get("context_packet")
    assert isinstance(e11_packet, dict), "B6 context_packet must be a dict"
    assert e11_packet.get("schema") == "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1"

    # Compute independent canonical B6 oracle for exact comparison
    oracle_snap = _make_raw_retrieval_snapshot(query=req.message, status="MEMORY_NOT_REQUIRED", items=[])
    oracle_shadow = orig_shadow(req.message, oracle_snap)
    oracle_packet = oracle_shadow.get("context_packet", {})

    # Genuine certified B6 packet_id: non-None string, starts with 'b6ctx_', 16-hex suffix
    packet_id = e11_packet.get("packet_id")
    assert isinstance(packet_id, str), f"B6 packet_id must be a string, got {type(packet_id)}"
    assert packet_id.startswith("b6ctx_") and len(packet_id) == 22, (
        f"B6 packet_id must have format 'b6ctx_<16hex>', got '{packet_id}'"
    )
    assert all(c in "0123456789abcdef" for c in packet_id[6:]), (
        f"B6 packet_id suffix must be lowercase hex, got '{packet_id[6:]}'"
    )
    assert packet_id != "b6ctx_0123456789abcdef", "Forged dummy packet_id rejected"
    assert packet_id == oracle_packet.get("packet_id"), (
        f"B6 packet_id does not match canonical computation: {packet_id} vs {oracle_packet.get('packet_id')}"
    )

    # Genuine certified B6 state: list of StateEntry dicts, non-empty, genuine types
    state_entries = e11_packet.get("state")
    assert isinstance(state_entries, list), f"B6 state must be a list of StateEntry dicts, got {type(state_entries)}"
    assert len(state_entries) > 0, "B6 state must contain at least one StateEntry"
    oracle_state = oracle_packet.get("state", [])
    assert len(state_entries) == len(oracle_state), (
        f"State entries count mismatch: {len(state_entries)} vs {len(oracle_state)}"
    )
    for actual, expected in zip(state_entries, oracle_state):
        assert isinstance(actual, dict), f"Each state entry must be a dict, got {type(actual)}"
        assert actual.get("state_id") == expected.get("state_id"), (
            f"state_id mismatch: {actual.get('state_id')} vs {expected.get('state_id')}"
        )
        assert actual.get("state_type") == expected.get("state_type"), (
            f"state_type mismatch: {actual.get('state_type')} vs {expected.get('state_type')}"
        )
        assert actual.get("content_digest") == expected.get("content_digest"), (
            f"content_digest mismatch: {actual.get('content_digest')} vs {expected.get('content_digest')}"
        )
        assert actual.get("provenance") == expected.get("provenance"), (
            f"provenance mismatch: {actual.get('provenance')} vs {expected.get('provenance')}"
        )
        assert actual.get("payload") == expected.get("payload"), (
            f"payload mismatch: {actual.get('payload')} vs {expected.get('payload')}"
        )

    # Packet-level provenance and deep canonical equality against oracle
    assert e11_packet.get("provenance_refs") == oracle_packet.get("provenance_refs"), (
        f"provenance_refs mismatch: {e11_packet.get('provenance_refs')} vs {oracle_packet.get('provenance_refs')}"
    )
    assert canonical_json(e11_packet) == canonical_json(oracle_packet), (
        "Published B6 context_packet does not match canonical oracle packet"
    )

    # Provenance query check: must match user message
    assert e11_packet.get("query") == req.message, (
        f"B6 context packet query must match request: expected '{req.message}', got '{e11_packet.get('query')}'"
    )

    # Not the non-existent fields that caused historical false failure
    assert "context_id" not in e11_packet
    assert "working_state" not in e11_packet

    # Historical W4 ContextPacketV2 remains present and structurally separate
    assert isinstance(v2_packet, dict)
    assert "context_items" in v2_packet
    assert "packet_id" in v2_packet
    assert "state" not in v2_packet
    assert "context_items" not in e11_packet


@pytest.mark.parametrize(
    "msg, expect_unresolved",
    [
        ("Que dit le kernel b6 ?", False),
        ("Que dit le kernel b6 sur la memoire native ?", False),
        ("Que dit le kernel b6 sur la memoire native et les context packets de l'architecture ?", False),
        ("Qui a fait ça ?", True),
        ("Bonjour comment vas-tu ?", False),
    ],
)
@pytest.mark.asyncio
async def test_r6b_causal_b6_execution_across_query_variations(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch, msg: str, expect_unresolved: bool
):
    """R6b: Genuine E11 and B6 execution must occur across short, medium, long, and unresolved queries."""
    orig_shadow = run_cognition_shadow_with_memory
    shadow_code = orig_shadow.__code__
    assemble_code = assemble_context.__code__

    observed_shadow_calls: list[Any] = []
    observed_assemble_calls: list[Any] = []

    def b6_profiler(frame, event, arg):
        if event == "call":
            if frame.f_code is shadow_code:
                observed_shadow_calls.append(frame)
            elif frame.f_code is assemble_code:
                observed_assemble_calls.append(frame)

    orig_setprofile = sys.setprofile

    def chained_setprofile(new_prof):
        if new_prof is None or new_prof is b6_profiler:
            orig_setprofile(b6_profiler)
        else:
            def combined(frame, event, arg):
                b6_profiler(frame, event, arg)
                try:
                    new_prof(frame, event, arg)
                except Exception:
                    pass
            orig_setprofile(combined)

    req = BrodyChatRequest(
        message=msg,
        language="fr",
        session_id="test_r6b_query_variations",
        compact=False,
        debug=True,
    )

    prev_prof = sys.getprofile()
    orig_setprofile(b6_profiler)
    monkeypatch.setattr(sys, "setprofile", chained_setprofile)
    try:
        result = await brody_chat(req)
    finally:
        orig_setprofile(prev_prof)

    assert len(observed_shadow_calls) == 1, (
        f"Genuine run_cognition_shadow_with_memory was not executed for query '{msg}' "
        f"(detected {len(observed_shadow_calls)} calls)"
    )
    assert len(observed_assemble_calls) >= 1, (
        f"Genuine assemble_context was not executed for query '{msg}'"
    )

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, f"E11 shadow missing for query '{msg}'"

    e11_packet = shadow.get("context_packet", {})
    assert e11_packet.get("schema") == "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1"
    assert e11_packet.get("query") == msg
    assert e11_packet.get("packet_id") != "b6ctx_0123456789abcdef"

    # Packet-level provenance and payload integrity across all query variations
    assert e11_packet.get("provenance_refs") != ["synthetic:WRONG_PACKET_PROVENANCE"], (
        f"Forged or altered provenance_refs detected in context packet for query '{msg}'"
    )
    for st in e11_packet.get("state", []):
        assert isinstance(st, dict)
        assert "synthetic_replacement" not in st.get("payload", {}), (
            f"Forged payload detected in context packet state for query '{msg}'"
        )

    if expect_unresolved:
        resolution_requests = shadow.get("resolution_requests", [])
        assert len(resolution_requests) >= 1, (
            f"Expected unresolved symbol resolution requests for query '{msg}', got {len(resolution_requests)}"
        )


@pytest.mark.asyncio
async def test_r7_memzum_memory_not_required_zero_index_load(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R7: When MEMZUM declares memory_required=False, zero index records are loaded by native retrieval seam."""
    call_counts = {
        "native_retrieval_index_loads": 0,
        "historical_brody_index_loads": 0,
        "other_index_loads": 0,
        "retrieval_snapshot_calls": 0,
    }
    orig_load = load_native_memory_index
    orig_retrieval = build_native_memory_retrieval_snapshot

    def scoped_spy_load(*args, **kwargs):
        stack_funcs = [f.function for f in inspect.stack()]
        if any(
            fn in (
                "build_native_memory_retrieval_snapshot",
                "query_native_memory",
                "run_cognition_shadow_with_memory",
            )
            for fn in stack_funcs
        ):
            call_counts["native_retrieval_index_loads"] += 1
        elif "build_project_memory_snapshot" in stack_funcs:
            call_counts["historical_brody_index_loads"] += 1
        else:
            call_counts["other_index_loads"] += 1
        return orig_load(*args, **kwargs)

    def spy_retrieval(*args, **kwargs):
        call_counts["retrieval_snapshot_calls"] += 1
        return orig_retrieval(*args, **kwargs)

    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.load_native_memory_index",
        scoped_spy_load,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.build_native_memory_retrieval_snapshot",
        spy_retrieval,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_native_memory_response_adapter.build_native_memory_retrieval_snapshot",
        spy_retrieval,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.build_native_memory_retrieval_snapshot",
        spy_retrieval,
        raising=False,
    )

    # Dynamically patch any cached or aliased references to load_native_memory_index
    import apps.obsidia_api.routes.brody as brody_mod
    for name, val in list(brody_mod.__dict__.items()):
        if callable(val) and getattr(val, "__code__", None) is orig_load.__code__:
            monkeypatch.setattr(brody_mod, name, scoped_spy_load)

    # Alias-safe code-object execution profiler with profiler-masking resilience
    orig_setprofile = sys.setprofile
    index_code = orig_load.__code__
    observed_index_executions: list[str] = []

    def index_profiler(frame, event, arg):
        if event == "call" and frame.f_code is index_code:
            cur = frame.f_back
            caller = ""
            while cur is not None:
                name = cur.f_code.co_name
                if name not in ("scoped_spy_load", "spy_load", "index_profiler"):
                    caller = name
                    break
                cur = cur.f_back
            observed_index_executions.append(caller)

    def chained_setprofile(new_prof):
        if new_prof is None or new_prof is index_profiler:
            orig_setprofile(index_profiler)
        else:
            def combined(frame, event, arg):
                index_profiler(frame, event, arg)
                try:
                    new_prof(frame, event, arg)
                except Exception:
                    pass
            orig_setprofile(combined)

    prev_prof = sys.getprofile()
    orig_setprofile(index_profiler)
    monkeypatch.setattr(sys, "setprofile", chained_setprofile)
    try:
        req = BrodyChatRequest(
            message="Bonjour comment vas-tu ?",
            language="fr",
            session_id="test_r7_not_required",
            compact=False,
            debug=True,
        )
        result = await brody_chat(req)
    finally:
        orig_setprofile(prev_prof)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "E11 shadow must be present even when memory is not required"
    assert shadow.get("memory_snapshot_ref", {}).get("status") == "MEMORY_NOT_REQUIRED"

    # Native retrieval call chain causes zero index load when memory_required=False
    assert call_counts["native_retrieval_index_loads"] == 0, (
        f"Native retrieval must cause zero index load when memory not required, got {call_counts['native_retrieval_index_loads']}"
    )

    # Historical Brody behavior is intact: exactly 2 pre-existing index loads via build_project_memory_snapshot
    assert call_counts["historical_brody_index_loads"] == 2, (
        f"Expected historical Brody to maintain 2 pre-existing index loads, got {call_counts['historical_brody_index_loads']}"
    )

    # Zero unexpected or extra index loads via patched spy
    assert call_counts["other_index_loads"] == 0, (
        f"Expected zero extra index loads outside historical Brody, got {call_counts['other_index_loads']}"
    )

    # Code-object profiler independently verifies execution count and caller provenance
    historical_execs = [c for c in observed_index_executions if c == "build_project_memory_snapshot"]
    unauthorized_execs = [c for c in observed_index_executions if c != "build_project_memory_snapshot"]
    assert len(historical_execs) == 2, (
        f"Expected historical Brody to maintain 2 pre-existing index loads, got {len(historical_execs)} (observed: {observed_index_executions})"
    )
    assert len(unauthorized_execs) == 0, (
        f"Detected {len(unauthorized_execs)} unauthorized index loads outside historical Brody: {unauthorized_execs}"
    )
    assert len(observed_index_executions) == 2, (
        f"Expected exactly 2 total index loads across request window, got {len(observed_index_executions)}"
    )


@pytest.mark.parametrize(
    "status",
    [
        "MEMORY_USABLE",
        "MEMORY_REQUIRED_EMPTY",
        "MEMORY_REQUIRED_EMPTY_QUERY",
        "MEMORY_REQUIRED_NO_NATIVE_SOURCE",
        "MEMORY_REQUIRED_INVALID_NATIVE_SOURCE",
        "MEMORY_NOT_REQUIRED",
    ],
)
def test_r8_legitimate_memory_statuses_preserved(status: str):
    """R8: All legitimate memory statuses are handled cleanly by E11 consumer."""
    items = [_make_sample_item()] if status == "MEMORY_USABLE" else []
    snap = _make_raw_retrieval_snapshot(status=status, items=items)
    out = run_cognition_shadow_with_memory("Que dit le kernel b6 ?", snap)

    assert out["schema"] == E11_SCHEMA
    assert out["memory_snapshot_ref"]["status"] == status


def test_r9_b7_applied_only_to_sens_entries():
    """R9: B7 detector is applied strictly to SENS StateEntry, never to native memory entries."""
    text = "Qui a fait ça ?"  # unresolved coreference in SENS
    raw_snap = _make_raw_retrieval_snapshot(items=[_make_sample_item("doc_k1", 1)])
    out = run_cognition_shadow_with_memory(text, raw_snap)

    requests = out.get("resolution_requests", [])
    assert len(requests) >= 1
    # Verify every resolution request points to a SENS entry, not native memory
    sens_state_ids = {e["state_id"] for e in out["state_entries"]}
    for req in requests:
        assert req["origin_state_id"] in sens_state_ids


@pytest.mark.asyncio
async def test_r10_no_decision_execution_or_promotion_authority(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R10: Boundary remains strictly KX108_ONLY with zero action or write authority."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r10_boundary",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "cognition_shadow_memory must be present"

    boundary = shadow.get("boundary", {})
    assert boundary.get("decision_authority") == "KX108_ONLY"
    assert boundary.get("readonly") is True
    assert boundary.get("memory_write") is False
    assert boundary.get("emits_act") is False
    assert boundary.get("kernel_mutation") is False


@pytest.mark.asyncio
async def test_r11_no_memory_write_nor_b10_persistence(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R11: Zero disk write or memory persistence during shadow join execution."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r11_no_write",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    assert result.get("memory_write") is False
    assert result.get("canonical_write") in (False, None)
    assert result.get("kernel_mutation") is False
    assert "graphiti_write" not in result or result.get("graphiti_write") is False
    assert "neo4j_write" not in result or result.get("neo4j_write") is False


@pytest.mark.asyncio
async def test_r12_no_raw_memory_leak_in_public_brody_response(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R12: Raw memory excerpts are not leaked into the public final_answer."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r12_leak",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    final_answer = str(result.get("final_answer") or "")
    # The raw excerpt from the test fixture must not be blindly injected into final_answer
    assert "Ceci est un extrait de memoire native pour test." not in final_answer


def test_r13_shadow_v0_and_certified_e11_contracts_untouched():
    """R13: AST and function signatures of Shadow V0 and certified E11 remain unaltered."""
    e11_path = ROOT / "app" / "integration" / "cognition_shadow_memory_v0.py"
    v0_path = ROOT / "app" / "integration" / "cognition_shadow_v0.py"

    assert e11_path.exists(), "cognition_shadow_memory_v0.py must exist"
    assert v0_path.exists(), "cognition_shadow_v0.py must exist"

    tree = ast.parse(e11_path.read_text(encoding="utf-8"))
    fn_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert "run_cognition_shadow_with_memory" in fn_names
    assert "_validate_snapshot" in fn_names

    sig = inspect.signature(run_cognition_shadow_with_memory)
    assert list(sig.parameters.keys()) == ["text", "memory_snapshot"]


@pytest.mark.asyncio
async def test_r14_explicit_error_propagation_on_corrupt_snapshot(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R14: Explicit error degradation is recorded when snapshot is corrupt.

    Owner Decision Approved:
    R14_OWNER_APPROVAL=YES
    SHADOW_FAILURE_POLICY=ISOLATE_AND_RECORD_DEGRADATION
    Canonical degraded status: components.COGNITION_SHADOW_MEMORY == "DEGRADED"
    Sanitized errors: errors receives sanitized error code without raw memory leaks.
    Historical Brody pipeline continues unaffected; no valid shadow emitted.
    """
    corrupted_snap = _make_raw_retrieval_snapshot(memory_write=True)  # forbidden flag

    # Patch all retrieval call sites to prevent test-harness patch leakage
    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.build_native_memory_retrieval_snapshot",
        lambda *args, **kwargs: corrupted_snap,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_native_memory_response_adapter.build_native_memory_retrieval_snapshot",
        lambda *args, **kwargs: corrupted_snap,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.build_native_memory_retrieval_snapshot",
        lambda *args, **kwargs: corrupted_snap,
        raising=False,
    )

    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r14_degraded",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    # 1. Historical Brody response pipeline continues
    assert "response_md" in result or "response" in result, "Historical response must be present"
    cog_receipt = result.get("cognitive_runtime_receipt", {})
    components = cog_receipt.get("components", {})
    assert "W3_BRODY" in components, "Historical W3_BRODY component must remain"
    assert "W4_MEMORY_RETRIEVAL" in components, "Historical W4_MEMORY_RETRIEVAL component must remain"

    # 2. No valid E11 Shadow result is emitted (neither in receipt nor at top level)
    assert cog_receipt.get("cognition_shadow_memory") is None, (
        "Corrupted snapshot must not emit valid cognition_shadow_memory in receipt"
    )
    assert result.get("cognition_shadow_memory") is None, (
        "Corrupted snapshot must not emit valid cognition_shadow_memory at top level"
    )

    # 3. Canonical degraded status: MUST be exactly "DEGRADED"
    assert components.get("COGNITION_SHADOW_MEMORY") == "DEGRADED", (
        f"Canonical degraded status must be exactly 'DEGRADED', got {components.get('COGNITION_SHADOW_MEMORY')!r}"
    )

    # 4. Mandatory sanitized error in errors list
    errors = cog_receipt.get("errors")
    assert isinstance(errors, list) and len(errors) > 0, (
        "Receipt errors list must not be empty upon E11 degradation"
    )
    e11_errors = [e for e in errors if "E11" in str(e) or "SHADOW" in str(e)]
    assert len(e11_errors) > 0, (
        "errors must contain at least one sanitized E11 shadow error code"
    )

    for err in e11_errors:
        assert isinstance(err, str), f"Each error must be a string, got {type(err)}"
        # Must be a sanitized token without spaces, path separators, or punctuation
        assert not any(c in err for c in (" ", ";", "/", "\\", "\n", "\t")), (
            f"E11 error code contains forbidden characters, paths, or punctuation: {err!r}"
        )
        assert re.match(r"^[A-Z0-9_]+(:[A-Z0-9_]+)*$", err), (
            f"E11 error code must be sanitized token format: {err!r}"
        )

    for err in errors:
        assert isinstance(err, str), f"Each error must be a string, got {type(err)}"
        # Must be a sanitized token without spaces, path separators, or punctuation across ALL errors
        assert not any(c in err for c in (" ", ";", "/", "\\", "\n", "\t")), (
            f"Error entry contains forbidden characters, paths, or whitespace: {err!r}"
        )
        assert not any(bad in err for bad in ("SECRET", "CANARY", "private", "unlisted")), (
            f"Error entry contains forbidden or secret tokens: {err!r}"
        )
        assert re.match(r"^[A-Za-z0-9_]+(:[A-Za-z0-9_]+)*$", err), (
            f"Receipt error code must be sanitized token format: {err!r}"
        )
        assert not any(
            phrase in err
            for phrase in (
                "carries forbidden",
                "forbidden authority",
                "Traceback",
                "PRIVATE_SENTINEL",
                "document.md",
                "Ceci est un extrait",
                "test native memory",
            )
        ), f"Raw detail leaked in errors: {err!r}"

    # 5. Public Brody answer contains no raw memory or error internals
    final_answer = str(result.get("final_answer") or result.get("response") or result.get("response_md") or "")
    assert "Ceci est un extrait" not in final_answer
    assert "Traceback" not in final_answer


@pytest.mark.parametrize(
    "exc_type, exc_msg",
    [
        (RuntimeError, "HISTORICAL_BACKEND_CRASH_RUNTIME"),
        (ValueError, "HISTORICAL_BACKEND_CRASH_VALUE"),
    ],
)
@pytest.mark.asyncio
async def test_r14b_historical_pipeline_errors_not_swallowed(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch, exc_type: type, exc_msg: str
):
    """R14b: Failures in the historical response pipeline must NOT be swallowed or converted to E11 degradation."""
    def fail_historical(**kwargs):
        raise exc_type(exc_msg)

    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.run_brody_real_response_pipeline",
        fail_historical,
    )

    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r14b_historical_error",
        compact=False,
        debug=True,
    )

    with pytest.raises(exc_type, match=exc_msg):
        await brody_chat(req)


@pytest.mark.asyncio
async def test_r14c_governance_and_invariant_errors_not_swallowed(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R14c: Certified invariants (ContextBoundError, DuplicateStateError) and non-attributable errors

    must NOT be swallowed or converted into advisory E11 degradation; they must propagate.
    """
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r14c_governance_error",
        compact=False,
        debug=True,
    )

    import apps.obsidia_api.routes.brody as brody_mod
    orig_shadow_code = run_cognition_shadow_with_memory.__code__
    alias_names = {
        name
        for name, val in list(brody_mod.__dict__.items())
        if callable(val) and getattr(val, "__code__", None) is orig_shadow_code
    }

    def patch_shadow_everywhere(target_fn):
        monkeypatch.setattr(
            "app.integration.cognition_shadow_memory_v0.run_cognition_shadow_with_memory",
            target_fn,
        )
        monkeypatch.setattr(
            "apps.obsidia_api.routes.brody.run_cognition_shadow_with_memory",
            target_fn,
            raising=False,
        )
        for name in alias_names:
            monkeypatch.setattr(brody_mod, name, target_fn)

    # 1. ContextBoundError must propagate
    patch_shadow_everywhere(
        lambda *a, **kw: (_ for _ in ()).throw(ContextBoundError("SENTINEL_CONTEXT_BOUND_VIOLATION"))
    )
    with pytest.raises(ContextBoundError, match="SENTINEL_CONTEXT_BOUND_VIOLATION"):
        await brody_chat(req)

    # 2. DuplicateStateError must propagate
    patch_shadow_everywhere(
        lambda *a, **kw: (_ for _ in ()).throw(DuplicateStateError("SENTINEL_DUPLICATE_STATE_VIOLATION"))
    )
    with pytest.raises(DuplicateStateError, match="SENTINEL_DUPLICATE_STATE_VIOLATION"):
        await brody_chat(req)

    # 3. Uncertain-origin non-ValueError exception (e.g. TypeError) must also propagate
    patch_shadow_everywhere(
        lambda *a, **kw: (_ for _ in ()).throw(TypeError("UNCERTAIN_ORIGIN_TYPE_ERROR"))
    )
    with pytest.raises(TypeError, match="UNCERTAIN_ORIGIN_TYPE_ERROR"):
        await brody_chat(req)


def test_r15_determinism_and_output_compatibility():
    """R15: Identical inputs produce identical canonical JSON shadow outputs."""
    raw_snap = _make_raw_retrieval_snapshot(items=[_make_sample_item("doc_k1", 1)])
    out1 = run_cognition_shadow_with_memory("Que dit le kernel b6 ?", raw_snap)
    out2 = run_cognition_shadow_with_memory("Que dit le kernel b6 ?", raw_snap)

    j1 = canonical_json(out1)
    j2 = canonical_json(out2)
    assert hashlib.sha256(j1.encode("utf-8")).hexdigest() == hashlib.sha256(j2.encode("utf-8")).hexdigest()


def test_r16_adapter_signature_supports_precomputed_retrieval():
    """R16: build_native_memory_response must accept precomputed_retrieval for single-retrieval join."""
    sig = inspect.signature(build_native_memory_response)
    assert "precomputed_retrieval" in sig.parameters, (
        "build_native_memory_response must support precomputed_retrieval parameter"
    )
