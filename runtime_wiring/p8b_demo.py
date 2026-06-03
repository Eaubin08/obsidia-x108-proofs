# runtime_wiring/p8b_demo.py
# P8B Dry-Run Demo — run with: python runtime_wiring/p8b_demo.py
# No external dependencies. stdlib only.
# Demonstrates: contract loading → 4 packets → routing → decision → OS3 evidence

from __future__ import annotations
import json
import sys
import pathlib
from dataclasses import asdict

# Path setup: allow running from repo root or from runtime_wiring/
_THIS_DIR = pathlib.Path(__file__).resolve().parent
_REPO_ROOT = _THIS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from runtime_wiring.contracts_loader import load_all_contracts
from runtime_wiring.source_adapters import (
    cognitive_to_context_packet,
    rssi_rgpd_to_context_packet,
    atlas_to_context_packet,
    compliance_to_context_packet,
)
from runtime_wiring.dry_run_packet_router import route_packets


def main() -> None:
    print("=" * 70)
    print("P8B DRY-RUN WIRING DEMO - Obsidia X-108")
    print("=" * 70)
    print()

    # Step 1: Load and verify all 8 contracts
    print("[1/4] Loading contracts...")
    contracts_result = load_all_contracts()
    print(f"      Status: {contracts_result['status']}")
    print(f"      Repo root: {contracts_result['repo_root']}")
    print(f"      Contracts loaded: {len(contracts_result['contracts'])}/8")
    print()

    # Step 2: Create 4 ContextPacket via source adapters
    print("[2/4] Building 4 ContextPacket via source adapters...")

    cognitive_packet = cognitive_to_context_packet({
        "cognitive_tension": 0.42,
        "world_action_candidate": "adjust_context_window",
        "confidence": 0.55,
        "timestamp": "2026-06-03T12:00:00Z",
    })
    print(f"      [cognitive]   {cognitive_packet.context_id} — {cognitive_packet.boundary}")

    rssi_rgpd_packet = rssi_rgpd_to_context_packet({
        "security_posture_score": 0.71,
        "threat_model_version": "v1.0",
        "rgpd_readiness": "PRE_AUDIT",
        "timestamp": "2026-06-03T12:00:01Z",
    })
    print(f"      [rssi_rgpd]   {rssi_rgpd_packet.context_id} — {rssi_rgpd_packet.boundary}")

    atlas_packet = atlas_to_context_packet({
        "scenario_candidate": "domain_expansion_alpha",
        "scenario_confidence": 0.68,
        "actor_card": "external_partner_x",
        "timestamp": "2026-06-03T12:00:02Z",
    })
    print(f"      [atlas]       {atlas_packet.context_id} — {atlas_packet.boundary}")

    compliance_packet = compliance_to_context_packet({
        "iso27001_readiness": "CHECKLIST_PARTIAL",
        "dpia_status": "TEMPLATE_ONLY",
        "secnumcloud_target": True,
        "timestamp": "2026-06-03T12:00:03Z",
    })
    print(f"      [compliance]  {compliance_packet.context_id} — {compliance_packet.boundary}")
    print()

    all_packets = [cognitive_packet, rssi_rgpd_packet, atlas_packet, compliance_packet]

    # Step 3a: Route — normal case (no critical action)
    print("[3a/4] Routing - Scenario A: context advisory (no critical action)...")
    dt_a, ev_a, env_a = route_packets(
        packets=all_packets,
        critical_action_requested=False,
        action_candidate_type="EMIT_CONTEXT",
        source_module="p8b_demo_scenario_a",
    )
    print(f"       Decision: {dt_a.decision}")
    print(f"       Ticket:   {dt_a.ticket_id}")
    print(f"       Evidence: {ev_a.evidence_id}")
    print()

    # Step 3b: Route — critical action case
    print("[3b/4] Routing - Scenario B: critical action requested -> HOLD...")
    dt_b, ev_b, env_b = route_packets(
        packets=all_packets,
        critical_action_requested=True,
        action_candidate_type="WRITE",
        source_module="p8b_demo_scenario_b",
    )
    print(f"       Decision: {dt_b.decision}")
    print(f"       Ticket:   {dt_b.ticket_id}")
    print(f"       Evidence: {ev_b.evidence_id}")
    print(f"       Envelope: {env_b.intent_id}")
    print()

    # Step 4: Build and print final JSON output
    print("[4/4] Building final JSON report...")
    print()

    output = {
        "p8b_dry_run_demo": {
            "module": "runtime_wiring",
            "status": "DRY_RUN_ONLY",
            "decision_authority": "KX108_ONLY",
            "emits_act": False,
            "emits_real_decision": False,
        },
        "contracts_verification": {
            "status": contracts_result["status"],
            "contracts_checked": len(contracts_result["contracts"]),
            "contract_files": list(contracts_result["contracts"].keys()),
        },
        "context_packets": [
            asdict(cognitive_packet),
            asdict(rssi_rgpd_packet),
            asdict(atlas_packet),
            asdict(compliance_packet),
        ],
        "scenario_a_context_only": {
            "description": "Normal routing — context advisory, no critical action",
            "decision_ticket": asdict(dt_a),
            "os3_evidence_ticket": asdict(ev_a),
            "intent_envelope": None,
        },
        "scenario_b_critical_action": {
            "description": "Critical action requested → HOLD (X108 gate required)",
            "decision_ticket": asdict(dt_b),
            "os3_evidence_ticket": asdict(ev_b),
            "intent_envelope": asdict(env_b) if env_b else None,
        },
        "boundary_enforcement_summary": {
            "all_packets_advisory_only": all(p.advisory_only for p in all_packets),
            "all_packets_readonly": all(p.readonly for p in all_packets),
            "all_packets_no_act": all(not p.emits_act for p in all_packets),
            "all_packets_kx108_authority": all(
                p.decision_authority == "KX108_ONLY" for p in all_packets
            ),
            "scenario_a_no_real_allow": dt_a.decision != "ALLOW",
            "scenario_a_decision": dt_a.decision,
            "scenario_b_hold_on_critical": dt_b.decision == "HOLD",
            "scenario_b_decision": dt_b.decision,
        },
    }

    print(json.dumps(output, indent=2, default=str))
    print()
    print("=" * 70)
    print("P8B DRY-RUN COMPLETE - No world action executed. No real decision made.")
    print("=" * 70)


if __name__ == "__main__":
    main()
