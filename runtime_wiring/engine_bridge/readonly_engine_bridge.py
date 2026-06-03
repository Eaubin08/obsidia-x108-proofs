# runtime_wiring/engine_bridge/readonly_engine_bridge.py
# P10B Engine Bridge Readonly Adapter
# Bridges runtime_wiring dry-run results to engine-compatible preview.
# NO apps/ import. NO periphery/ import. NO runtime activation. KX108_ONLY.
# Run: python -m runtime_wiring.engine_bridge.readonly_engine_bridge

from __future__ import annotations

import json
import pathlib
import sys
from typing import Any, Dict, List

_THIS = pathlib.Path(__file__).resolve()
_REPO_ROOT = _THIS.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# ── runtime_wiring imports only — no apps/, no periphery/ ────────────────────
from runtime_wiring.source_registry.registry_loader import (
    count_by_family,
    load_registry_json,
)
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    route_registry_packets_to_x108,
    route_sample_by_family,
)
from runtime_wiring.engine_bridge.bridge_types import (
    EngineBridgeInput,
    EngineBridgeOutput,
    EngineBridgePreview,
    EngineBridgeSafetyStatus,
)

_REGISTRY_JSON = _REPO_ROOT / "runtime_wiring" / "source_registry" / "source_file_registry.json"
_REGISTRY_SUMMARY = _REPO_ROOT / "runtime_wiring" / "source_registry" / "source_registry_summary.json"

_EXPECTED_FAMILIES: List[str] = [
    "COGNITIVE_REINTEGRATION",
    "RSSI_RGPD",
    "ATLAS",
    "COMPLIANCE_DATA_GOVERNANCE",
    # P24 — new families added in coverage repair
    "RSSI_SECURITY_PRESENTATION",
    "EXTERNAL_SIGNALS",
    "NARRATIVE_PROVENANCE_LAYER",
    # P32 — 8th family
    "OS_TRAD_REVERSE_OS",
]

# ── Engine ContextPacket field names (reference only — no import of periphery) ─
# periphery.context.context_packet_builder.ContextPacket has:
#   packet_id, action_id, status, content_hash, signals, can_decide
# runtime_wiring.packet_types.ContextPacket has:
#   source, context_id, advisory_only, emits_act, decision_authority,
#   runtime_allowed_now, readonly
# Bridge translates between these two schemas WITHOUT importing periphery directly.
_ENGINE_CONTEXT_PACKET_FIELDS = frozenset({
    "packet_id", "action_id", "status", "content_hash", "signals", "can_decide",
})
_DRY_RUN_PACKET_FIELDS = frozenset({
    "source", "context_id", "advisory_only", "emits_act",
    "decision_authority", "runtime_allowed_now", "readonly",
})


def _dry_run_packet_to_engine_preview(pkt: Any) -> Dict[str, Any]:
    """Convert a dry-run ContextPacket to engine ContextPacket preview dict.

    Maps runtime_wiring.packet_types.ContextPacket fields to the engine's
    periphery.context.context_packet_builder.ContextPacket schema.
    No periphery import — schema mapped by reference (P10A analysis).
    """
    import hashlib, json as _json
    signals = [
        f"dry_run:{pkt.source}",
        f"advisory_only:{pkt.advisory_only}",
        f"decision_authority:{pkt.decision_authority}",
    ]
    content_hash = hashlib.sha256(
        _json.dumps({"context_id": pkt.context_id, "source": pkt.source}, sort_keys=True).encode()
    ).hexdigest()
    return {
        "packet_id": pkt.context_id,
        "action_id": f"bridge-preview-{pkt.source}",
        "status": "READY",
        "content_hash": content_hash,
        "signals": signals,
        "can_decide": False,
        # Bridge metadata (not in engine schema, stripped before real API use)
        "_bridge_meta": {
            "dry_run": True,
            "runtime_active": False,
            "emits_act": pkt.emits_act,
            "advisory_only": pkt.advisory_only,
            "decision_authority": pkt.decision_authority,
            "readonly": pkt.readonly,
        },
    }


def build_engine_bridge_preview() -> EngineBridgePreview:
    """Full bridge pipeline: load registry → dry-run routing → EngineBridgePreview."""
    # Step 1: load registry
    entries = load_registry_json(_REGISTRY_JSON)
    summary = json.loads(_REGISTRY_SUMMARY.read_text(encoding="utf-8"))
    assert len(entries) > 0, "FAIL_CLOSED: registry is empty"
    assert summary["safety_invariants_ok"] is True, "FAIL_CLOSED: safety_invariants_ok is not True"
    assert summary["zip_extraction"] is False, "FAIL_CLOSED: zip_extraction must be False"
    assert summary["source_pack_import"] is False, "FAIL_CLOSED: source_pack_import must be False"

    # Step 2: verify families
    by_family = count_by_family(entries)
    missing = [f for f in _EXPECTED_FAMILIES if f not in by_family]
    if missing:
        raise ValueError(f"FAIL_CLOSED: missing families {missing}")

    # Step 3: context-only routing
    result_a = route_registry_packets_to_x108(entries, critical_action_requested=False, sample_size=1)
    assert result_a["decision"] == "ALLOW_CONTEXT_ONLY", (
        f"FAIL_CLOSED: expected ALLOW_CONTEXT_ONLY, got {result_a['decision']!r}"
    )
    assert result_a["emits_act"] is False, "FAIL_CLOSED: emits_act must be False"
    assert result_a["proof_claim"] is False, "FAIL_CLOSED: proof_claim must be False"

    # Step 4: critical-action routing
    result_b = route_registry_packets_to_x108(entries, critical_action_requested=True, sample_size=1)
    assert result_b["decision"] == "HOLD", (
        f"FAIL_CLOSED: expected HOLD, got {result_b['decision']!r}"
    )
    assert result_b["emits_act"] is False, "FAIL_CLOSED: emits_act must be False"
    assert result_b["proof_claim"] is False, "FAIL_CLOSED: proof_claim must be False"

    # Step 5: collect actual ContextPacket objects via route_sample_by_family,
    # then convert to engine preview format.
    # route_registry_packets_to_x108() returns metadata only (no packet objects).
    sampled: Dict[str, List[Any]] = route_sample_by_family(entries, sample_size=1)
    all_packets = [pkt for pkts in sampled.values() for pkt in pkts]
    engine_packets = [_dry_run_packet_to_engine_preview(pkt) for pkt in all_packets]

    # Step 6: build safety status
    safety = EngineBridgeSafetyStatus(
        zip_extraction=False,
        source_pack_import=False,
        runtime_active=False,
        readonly=True,
        emits_act=False,
        proof_claim=False,
        engine_mutation=False,
        apps_mutation=False,
        periphery_mutation=False,
        memory_write=False,
        graph_write=False,
        world_action=False,
        packages_created=False,
        decision_authority="KX108_ONLY",
    )

    # Step 7: build bridge input/output
    bridge_input = EngineBridgeInput(
        source_pipeline="P9C_REGISTRY_ROUTER_DRY_RUN",
        registry_entries_count=len(entries),
        families=_EXPECTED_FAMILIES,
        context_only_decision="ALLOW_CONTEXT_ONLY",
        critical_action_decision="HOLD",
    )

    bridge_output = EngineBridgeOutput(
        bridge_status="ENGINE_BRIDGE_PREVIEW_ONLY",
        source_pipeline="P9C_REGISTRY_ROUTER_DRY_RUN",
        registry_entries_count=len(entries),
        input_family_count=len(_EXPECTED_FAMILIES),
        context_packets_count=len(engine_packets),
        context_only_decision="ALLOW_CONTEXT_ONLY",
        critical_action_decision="HOLD",
        safety=safety,
        notes=[
            "ContextPacket name collision resolved: imports qualified per P10A analysis",
            "periphery.context.context_packet_builder.ContextPacket: NOT imported directly",
            "runtime_wiring.packet_types.ContextPacket: used for dry-run routing",
            "Bridge converts fields by reference schema only",
        ],
    )

    # Step 8: assemble preview
    from runtime_wiring.engine_bridge.api_adapter_preview import build_api_preview_payload
    api_payload = build_api_preview_payload(
        bridge_output=bridge_output,
        context_only_result=result_a,
        critical_action_result=result_b,
        engine_packets_preview=engine_packets,
    )

    preview = EngineBridgePreview(
        bridge_input=bridge_input,
        bridge_output=bridge_output,
        api_payload_preview=api_payload,
    )

    assert preview.is_safe(), "FAIL_CLOSED: EngineBridgePreview safety check failed"
    return preview


def bridge_registry_demo_to_engine_preview() -> Dict[str, Any]:
    """Run the full bridge and return serialisable dict."""
    preview = build_engine_bridge_preview()
    return preview.to_dict()


def validate_engine_bridge_safety(preview: EngineBridgePreview) -> bool:
    """Validate all safety invariants on a completed preview. Returns True or raises."""
    if not preview.is_safe():
        raise ValueError("FAIL_CLOSED: engine bridge safety validation failed")
    # Extra: no ACT anywhere in api_payload
    payload_str = json.dumps(preview.api_payload_preview, default=str)
    if '"ACT"' in payload_str or '"emits_act": true' in payload_str:
        raise ValueError("FAIL_CLOSED: ACT or emits_act=true found in api_payload_preview")
    return True


def summarize_engine_bridge_preview(preview: EngineBridgePreview) -> str:
    out = preview.bridge_output
    return (
        f"bridge_status={out.bridge_status} | "
        f"registry={out.registry_entries_count} entries | "
        f"families={out.input_family_count} | "
        f"packets={out.context_packets_count} | "
        f"context_only={out.context_only_decision} | "
        f"critical={out.critical_action_decision} | "
        f"emits_act={out.emits_act} | "
        f"engine_mutation={out.engine_mutation} | "
        f"apps_mutation={out.apps_mutation}"
    )


def _section(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main() -> None:
    print("=" * 70)
    print("P10B ENGINE BRIDGE READONLY ADAPTER — Obsidia X-108")
    print("NO RUNTIME ACTIVATION / NO APPS MODIFICATION / NO PERIPHERY MODIFICATION")
    print("=" * 70)

    _section("STEP 1: Build engine bridge preview")
    preview = build_engine_bridge_preview()
    print(f"  {summarize_engine_bridge_preview(preview)}")

    _section("STEP 2: Validate safety")
    validate_engine_bridge_safety(preview)
    print("  All safety invariants: PASS")
    print(f"  apps_mutation:       {preview.bridge_output.apps_mutation}")
    print(f"  periphery_mutation:  {preview.bridge_output.periphery_mutation}")
    print(f"  engine_mutation:     {preview.bridge_output.engine_mutation}")
    print(f"  runtime_active:      {preview.bridge_output.runtime_active}")
    print(f"  emits_act:           {preview.bridge_output.emits_act}")
    print(f"  proof_claim:         {preview.bridge_output.proof_claim}")

    _section("STEP 3: Engine packets preview")
    for pkt in preview.api_payload_preview.get("engine_context_packets_preview", []):
        meta = pkt.get("_bridge_meta", {})
        print(
            f"  [{pkt.get('packet_id','?')[:24]}] "
            f"status={pkt.get('status')} | "
            f"can_decide={pkt.get('can_decide')} | "
            f"emits_act={meta.get('emits_act')} | "
            f"advisory_only={meta.get('advisory_only')}"
        )

    _section("STEP 4: Final JSON output")
    print(json.dumps(preview.to_dict(), indent=2, default=str))

    print()
    print("=" * 70)
    print("P10B ENGINE BRIDGE READONLY ADAPTER COMPLETE")
    print("No engine modified. No apps modified. No periphery modified.")
    print("=" * 70)


if __name__ == "__main__":
    main()
