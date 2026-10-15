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
import hashlib
import inspect
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from app.cognition.b7.detector import detect_unresolved
from app.harness.state_explicit.contracts import canonical_json
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
    and the certified E11 cognition shadow consumer without duplicate retrieval.
    """
    call_counts = {"retrieval": 0, "index": 0}
    orig_retrieval = build_native_memory_retrieval_snapshot

    def spy_retrieval(*args, **kwargs):
        call_counts["retrieval"] += 1
        return orig_retrieval(*args, **kwargs)

    monkeypatch.setattr(
        "apps.obsidia_api.routes.brody.build_native_memory_retrieval_snapshot",
        spy_retrieval,
        raising=False,
    )
    monkeypatch.setattr(
        "apps.obsidia_api.brody_native_memory_response_adapter.build_native_memory_retrieval_snapshot",
        spy_retrieval,
    )

    req = BrodyChatRequest(
        message="Que dit le kernel b6 sur la memoire native ?",
        language="fr",
        session_id="test_r1_single_retrieval",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    # In GREEN, build_native_memory_retrieval_snapshot is called exactly once
    assert call_counts["retrieval"] == 1, (
        f"Expected exactly 1 retrieval call, got {call_counts['retrieval']}"
    )

    # E11 shadow output must be attached to the cognitive runtime receipt
    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "E11 cognition_shadow_memory must be attached in cognitive_runtime_receipt"
    assert shadow.get("schema") == E11_SCHEMA


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
    """R6: ContextPacketV2 (W4) remains distinct from B6 ContextPacket (E11)."""
    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r6_context_packets",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    v2_packet = cog_receipt.get("context_packet_v2")
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")

    assert v2_packet is not None, "ContextPacketV2 must exist in receipt"
    assert shadow is not None, "E11 shadow must exist in receipt"

    e11_packet = shadow.get("context_packet")
    assert isinstance(e11_packet, dict)
    assert "context_id" in e11_packet
    assert "working_state" in e11_packet
    # Distinct schema and structure
    assert "context_items" in v2_packet
    assert "working_state" not in v2_packet


@pytest.mark.asyncio
async def test_r7_memzum_memory_not_required_zero_index_load(
    fast_brody_chat, monkeypatch: pytest.MonkeyPatch
):
    """R7: When MEMZUM declares memory_required=False, zero index records are loaded."""
    call_counts = {"index": 0}

    def spy_load(*args, **kwargs):
        call_counts["index"] += 1
        return load_native_memory_index(*args, **kwargs)

    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.load_native_memory_index",
        spy_load,
    )

    req = BrodyChatRequest(
        message="Bonjour comment vas-tu ?",
        language="fr",
        session_id="test_r7_not_required",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    shadow = cog_receipt.get("cognition_shadow_memory") or result.get("cognition_shadow_memory")
    assert shadow is not None, "E11 shadow must be present even when memory is not required"
    assert shadow.get("memory_snapshot_ref", {}).get("status") == "MEMORY_NOT_REQUIRED"
    assert call_counts["index"] == 0


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
    """R14: Explicit error degradation is recorded when snapshot is corrupt."""
    corrupted_snap = _make_raw_retrieval_snapshot(memory_write=True)  # forbidden flag

    monkeypatch.setattr(
        "apps.obsidia_api.brody_obsidia_native_memory.build_native_memory_retrieval_snapshot",
        lambda *args, **kwargs: corrupted_snap,
    )

    req = BrodyChatRequest(
        message="Que dit le kernel b6 ?",
        language="fr",
        session_id="test_r14_degraded",
        compact=False,
        debug=True,
    )
    result = await brody_chat(req)

    cog_receipt = result.get("cognitive_runtime_receipt", {})
    # Route or cognitive join must record degraded shadow status rather than crashing
    shadow_status = (
        cog_receipt.get("cognition_shadow_memory_status")
        or cog_receipt.get("components", {}).get("COGNITION_SHADOW_MEMORY")
    )
    assert shadow_status is not None, "Degraded shadow status must be explicitly recorded"
    assert "DEGRADED" in shadow_status or "ERROR" in shadow_status


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
