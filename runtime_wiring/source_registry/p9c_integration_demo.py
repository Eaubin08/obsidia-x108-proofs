# runtime_wiring/source_registry/p9c_integration_demo.py
# P9C Registry Router Integration Demo
# Pipeline: source_file_registry.json -> adapter -> ContextPacket -> X108 stub -> OS3 evidence
# NO zip extraction. NO source pack import. NO runtime activation. Stdlib only.
# Run: python runtime_wiring/source_registry/p9c_integration_demo.py

from __future__ import annotations
import json
import pathlib
import sys
from dataclasses import asdict
from typing import Any, Dict, List

# Path setup
_THIS_FILE = pathlib.Path(__file__).resolve()
_REGISTRY_DIR = _THIS_FILE.parent
_REPO_ROOT = _REGISTRY_DIR.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.source_registry.registry_loader import (
    count_by_family,
    load_registry_json,
)
from runtime_wiring.source_registry.registry_to_adapter_dry_run import (
    entry_to_metadata,
    reject_forbidden_entries,
    route_entry_to_context_packet,
    route_registry_packets_to_x108,
    route_sample_by_family,
    select_routable_entries,
    summarize_routing_result,
)

_REGISTRY_JSON = _REGISTRY_DIR / "source_file_registry.json"
_REGISTRY_SUMMARY = _REGISTRY_DIR / "source_registry_summary.json"

_EXPECTED_FAMILIES = [
    "COGNITIVE_REINTEGRATION",
    "RSSI_RGPD",
    "ATLAS",
    "COMPLIANCE_DATA_GOVERNANCE",
]


def _section(title: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def main() -> None:
    print("=" * 70)
    print("P9C REGISTRY ROUTER INTEGRATION DEMO - Obsidia X-108")
    print("NO ZIP EXTRACTION / NO SOURCE PACK IMPORT / NO RUNTIME ACTIVATION")
    print("=" * 70)

    # ── Step 1: Load registry ─────────────────────────────────────────────────
    _section("STEP 1: Load source_file_registry.json")
    entries = load_registry_json(_REGISTRY_JSON)
    print(f"  Loaded: {len(entries)} entries")

    summary_raw = json.loads(_REGISTRY_SUMMARY.read_text(encoding="utf-8"))
    print(f"  Summary status: {summary_raw['registry_status']}")
    print(f"  safety_invariants_ok: {summary_raw['safety_invariants_ok']}")
    print(f"  zip_extraction: {summary_raw['zip_extraction']}")
    print(f"  source_pack_import: {summary_raw['source_pack_import']}")

    by_family = count_by_family(entries)
    print(f"  Families: {dict(by_family)}")

    # ── Step 2: Verify families ───────────────────────────────────────────────
    _section("STEP 2: Verify all 4 families present")
    missing = [f for f in _EXPECTED_FAMILIES if f not in by_family]
    if missing:
        print(f"  [BLOCK] Missing families: {missing}")
        sys.exit(1)
    for fam in _EXPECTED_FAMILIES:
        routable = select_routable_entries(entries, family=fam, limit=None)
        print(f"  {fam}: {by_family[fam]} total, {len(routable)} routable")

    # ── Step 3: Sample 1 routable entry per family ───────────────────────────
    _section("STEP 3: Sample 1 routable entry per family -> metadata")
    samples: List[Dict[str, Any]] = []
    sample_entries = []

    for fam in _EXPECTED_FAMILIES:
        routable = select_routable_entries(entries, family=fam, limit=1)
        if not routable:
            print(f"  [WARN] No routable entry for {fam}")
            continue
        entry = routable[0]
        meta = entry_to_metadata(entry)
        samples.append({
            "family": fam,
            "registry_id": entry.registry_id,
            "file_name": entry.file_name,
            "extension": entry.extension,
            "recommended_decision": entry.recommended_decision,
            "adapter_target": entry.adapter_target,
            "boundary": entry.boundary_required,
            "runtime_allowed_now": entry.runtime_allowed_now,
            "emits_act": entry.emits_act,
            "zip_content_read": False,
            "internal_path_label": meta["internal_path_label"],
        })
        sample_entries.append(entry)
        print(
            f"  [{fam}] {entry.file_name} ({entry.extension}) "
            f"-> {entry.adapter_target} | boundary: {entry.boundary_required[:40]}..."
            if len(entry.boundary_required) > 40
            else f"  [{fam}] {entry.file_name} ({entry.extension}) "
            f"-> {entry.adapter_target} | boundary: {entry.boundary_required}"
        )

    # ── Step 4: Convert each sample entry to ContextPacket ───────────────────
    _section("STEP 4: route_entry_to_context_packet (registry metadata only)")
    context_packets = []
    for entry in sample_entries:
        pkt = route_entry_to_context_packet(entry)
        context_packets.append(pkt)
        print(
            f"  [{pkt.source}] context_id={pkt.context_id} | "
            f"advisory_only={pkt.advisory_only} | emits_act={pkt.emits_act} | "
            f"decision_authority={pkt.decision_authority}"
        )

    # Validate all packets
    violations = [p for p in context_packets if p.emits_act or not p.advisory_only]
    assert violations == [], f"Packet violations: {violations}"
    print(f"  All {len(context_packets)} packets: emits_act=False, advisory_only=True [OK]")

    # ── Step 5: Route context-only ────────────────────────────────────────────
    _section("STEP 5: route_registry_packets_to_x108 (context-only, no critical action)")
    result_a = route_registry_packets_to_x108(
        entries,
        critical_action_requested=False,
        sample_size=1,
    )
    print(f"  {summarize_routing_result(result_a)}")
    print(f"  decision_ticket: {result_a['decision_ticket_id']}")
    print(f"  evidence:        {result_a['evidence_id']}")
    print(f"  verification:    {result_a['verification_status']}")

    assert result_a["decision"] == "ALLOW_CONTEXT_ONLY", (
        f"Expected ALLOW_CONTEXT_ONLY, got {result_a['decision']}"
    )
    assert result_a["emits_act"] is False
    assert result_a["proof_claim"] is False

    # ── Step 6: Route with critical action ────────────────────────────────────
    _section("STEP 6: route_registry_packets_to_x108 (critical_action_requested=True)")
    result_b = route_registry_packets_to_x108(
        entries,
        critical_action_requested=True,
        sample_size=1,
    )
    print(f"  {summarize_routing_result(result_b)}")
    print(f"  decision_ticket: {result_b['decision_ticket_id']}")
    print(f"  envelope:        {result_b['envelope_id']}")
    print(f"  evidence:        {result_b['evidence_id']}")

    assert result_b["decision"] == "HOLD", (
        f"Expected HOLD, got {result_b['decision']}"
    )
    assert result_b["emits_act"] is False
    assert result_b["proof_claim"] is False
    assert result_b["envelope_id"] is not None

    # ── Step 7: Verify no forbidden entries were routed ───────────────────────
    _section("STEP 7: Verify forbidden entries (py, quarantine, archive) rejected")
    _, rejected = reject_forbidden_entries(entries)
    forbidden_count = len(rejected)
    routable_count = len(entries) - forbidden_count
    print(f"  Total entries:    {len(entries)}")
    print(f"  Routable:         {routable_count}")
    print(f"  Rejected (total): {forbidden_count}")

    reason_counts: Dict[str, int] = {}
    for r in rejected:
        key = r["reason"].split(":")[0]
        reason_counts[key] = reason_counts.get(key, 0) + 1
    for reason, count in sorted(reason_counts.items(), key=lambda x: -x[1]):
        print(f"    {reason}: {count}")

    # ── Step 8: Build final JSON output ──────────────────────────────────────
    _section("STEP 8: Final JSON output")

    output = {
        "p9c_integration_demo": {
            "status": "DRY_RUN_ONLY",
            "decision_authority": "KX108_ONLY",
            "source_registry_entries": len(entries),
            "families_sampled": len(_EXPECTED_FAMILIES),
            "routable_entries": routable_count,
            "rejected_entries": forbidden_count,
        },
        "registry_verification": {
            "status": summary_raw["registry_status"],
            "safety_invariants_ok": summary_raw["safety_invariants_ok"],
            "zip_extraction": summary_raw["zip_extraction"],
            "source_pack_import": summary_raw["source_pack_import"],
            "runtime_allowed_now_true_count": summary_raw["runtime_allowed_now_true_count"],
            "emits_act_true_count": summary_raw["emits_act_true_count"],
        },
        "samples": samples,
        "context_only_result": {
            "decision": result_a["decision"],
            "decision_ticket_id": result_a["decision_ticket_id"],
            "decision_authority": result_a["decision_authority"],
            "emits_act": result_a["emits_act"],
            "dry_run": result_a["dry_run"],
            "total_packets": result_a["total_packets"],
            "families_routed": result_a["families_routed"],
            "all_packets_no_act": result_a["all_packets_no_act"],
            "all_packets_kx108_authority": result_a["all_packets_kx108_authority"],
        },
        "critical_action_result": {
            "decision": result_b["decision"],
            "decision_ticket_id": result_b["decision_ticket_id"],
            "decision_authority": result_b["decision_authority"],
            "emits_act": result_b["emits_act"],
            "dry_run": result_b["dry_run"],
            "envelope_id": result_b["envelope_id"],
            "total_packets": result_b["total_packets"],
        },
        "os3_evidence": {
            "context_only_evidence_id": result_a["evidence_id"],
            "proof_claim": result_a["proof_claim"],
            "verification_status": result_a["verification_status"],
            "critical_action_evidence_id": result_b["evidence_id"],
        },
        "rejection_summary": {
            "total_rejected": forbidden_count,
            "by_reason_prefix": reason_counts,
        },
        "safety": {
            "zip_extraction": False,
            "source_pack_import": False,
            "runtime_activation": False,
            "world_action": False,
            "memory_write": False,
            "graph_write": False,
            "act_produced": False,
            "real_proof_produced": False,
            "packages_created": False,
        },
    }

    print(json.dumps(output, indent=2, default=str))

    print()
    print("=" * 70)
    print("P9C INTEGRATION DEMO COMPLETE")
    print("No world action. No zip extracted. No source pack imported.")
    print("=" * 70)


if __name__ == "__main__":
    main()
