#!/usr/bin/env python3
"""P4/P5 recorded GNSS evidence -> Brody -> KX108 dry-run smoke.

Consumes the frozen P4 development manifest and the recorded P5 evidence input.
P4 supplies trajectory-integrity anomaly evidence and a fail-closed GPS HOLD.
P5 bounds interpretation to strong observational support, explicitly non-causal.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.obsidia_api.brody_real_cognitive_join import run_real_cognitive_join
from apps.obsidia_api.brody_real_response_pipeline import (
    run_brody_real_response_pipeline,
)
from periphery.cognition.gps_defense_p4_p5_evidence_v0 import (
    build_p4_p5_brody_sigma_envelope_v0,
)


P4_FREEZE = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p4_temporal_classifier_freeze_v0.json"
)
P5_INPUT = (
    ROOT
    / "hackathons"
    / "nativebuilder-gps-defense"
    / "rf_attack_benchmark"
    / "p5_recorded_evidence_input_v0.json"
)
P5_ASSESSOR = ROOT / "scripts" / "gps" / "p5_causal_support_assessment.py"


def _load_p5_assessor():
    spec = importlib.util.spec_from_file_location(
        "p5_causal_support_assessment",
        P5_ASSESSOR,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("P5_ASSESSOR_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.assess


def _gps_micro() -> dict[str, Any]:
    return {
        "micro_core_version": "R6_DEFENSE_P4_P5_RECORDED_SMOKE",
        "domain_detected": "gps_defense_aviation",
        "hold_required": False,
        "is_adversarial": False,
        "survival_risk_flag": False,
        "projection_not_prediction_signal": {
            "is_prediction_claim": False,
        },
        "bio_animal_signal": {
            "dead_path_detection": [],
        },
    }


def build_report() -> dict[str, Any]:
    p4 = json.loads(P4_FREEZE.read_text(encoding="utf-8"))
    p5_input = json.loads(P5_INPUT.read_text(encoding="utf-8"))
    p5 = _load_p5_assessor()(p5_input)

    envelope = build_p4_p5_brody_sigma_envelope_v0(
        p4_freeze=p4,
        p5_assessment=p5,
    )

    message = (
        "Explique en lecture seule l'anomalie d'intégrité GPS observée et "
        "ses limites de preuve, sans conclure à une cause ni agir."
    )

    brody = run_brody_real_response_pipeline(
        message=message,
        language="fr",
        session_id="r6-defense-p4-p5-smoke",
    )

    joined = run_real_cognitive_join(
        message=message,
        language="fr",
        session_id="r6-defense-p4-p5-smoke",
        precomputed_micro_core=_gps_micro(),
        precomputed_brody_runtime=brody,
        precomputed_domain_sigma_envelope=envelope,
    )

    sigma = joined.get("sigma_domain_packet") or {}
    ticket = joined.get("decision_ticket_dry_run") or {}
    pre = brody.get("pre_reasoning_snapshot") or {}
    resolution_targets = (
        (pre.get("reasoning_directive") or {}).get(
            "resolution_targets",
            [],
        )
        or []
    )

    blockers = set(sigma.get("unknowns") or [])
    forbidden = set(sigma.get("forbidden_claims") or [])

    checks = {
        "brody_pre_reasoning_unblocked": (
            brody.get("response_source") == "REAL_BRODY_RUNTIME"
            and resolution_targets == []
        ),
        "p4_frozen_classifier_preserved": (
            sigma.get("p4_classifier_status")
            == "FROZEN_DEVELOPMENT_CLASSIFIER_AWAITING_BLIND_VALIDATION"
        ),
        "p4_anomaly_preserved": (
            sigma.get("p4_classification") == "ANOMALY"
            and sigma.get("p4_violation_count") == 3
        ),
        "p4_truth_free_preserved": (
            sigma.get("p4_truth_or_onset_consumed") is False
        ),
        "p4_claim_boundary_preserved": (
            sigma.get("p4_claim_boundary")
            == "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION"
        ),
        "p5_observational_not_causal": (
            sigma.get("p5_support_level")
            == "STRONG_OBSERVATIONAL_SUPPORT_NOT_CAUSAL"
            and sigma.get("causal_attribution_closed") is False
        ),
        "p5_blockers_preserved": {
            "NO_INDEPENDENT_PHYSICAL_SOURCE_CORROBORATION",
            "NO_CONTROLLED_INTERVENTION",
            "NO_HELDOUT_HOSTILE_VALIDATION",
        }.issubset(blockers),
        "spoofing_causal_claim_forbidden": (
            "SPOOFING_CAUSED_THE_OBSERVED_DISPLACEMENT" in forbidden
        ),
        "x108_hold_preserved": (
            sigma.get("x108_gate") == "HOLD"
            and joined.get("upstream_x108_gate_constraint") == "HOLD"
            and ticket.get("decision") == "HOLD"
            and ticket.get("x108_gate_status")
            == "X108_DRY_RUN_UPSTREAM_HOLD"
        ),
        "temporal_reason_preserved": (
            "TEMPORAL_INTEGRITY_ANOMALY"
            in (sigma.get("gate_reason_codes") or [])
        ),
        "precomputed_sigma_used": (
            joined.get("sigma_domain_packet_source")
            == "PRECOMPUTED_READONLY"
        ),
        "envelope_preserved_exactly": sigma == envelope,
        "kx108_only": (
            joined.get("decision_authority") == "KX108_ONLY"
            and ticket.get("decision_authority") == "KX108_ONLY"
        ),
        "no_act_or_verdict": (
            joined.get("allowed_to_act") is False
            and joined.get("allowed_to_decide") is False
            and joined.get("emits_act") is False
            and joined.get("emits_verdict") is False
            and ticket.get("emits_act") is False
        ),
    }

    verified = all(bool(v) for v in checks.values())

    return {
        "artifact": "r6_defense_p4_p5_recorded_evidence_to_brody_smoke",
        "status": (
            "P4_P5_RECORDED_EVIDENCE_TO_BRODY_VERIFIED"
            if verified
            else "P4_P5_RECORDED_EVIDENCE_TO_BRODY_FAILED_CLOSED"
        ),
        "verified": verified,
        "brody_response_source": brody.get("response_source"),
        "brody_remaining_resolution_targets": resolution_targets,
        "cognitive_join_status": joined.get("status"),
        "cognitive_join_completeness": joined.get("completeness"),
        "p4_classification": sigma.get("p4_classification"),
        "p4_first_anomaly_transition": sigma.get(
            "p4_first_anomaly_transition"
        ),
        "p4_ecef_step_m": sigma.get("p4_ecef_step_m"),
        "p4_claim_boundary": sigma.get("p4_claim_boundary"),
        "p5_support_level": sigma.get("p5_support_level"),
        "causal_attribution_closed": sigma.get(
            "causal_attribution_closed"
        ),
        "p5_blockers": sorted(blockers),
        "recorded_x108_gate": sigma.get("x108_gate"),
        "cognitive_ticket_decision": ticket.get("decision"),
        "cognitive_ticket_gate_status": ticket.get(
            "x108_gate_status"
        ),
        "checks": checks,
        "decision_authority": "KX108_ONLY",
        "readonly": True,
        "allowed_to_decide": False,
        "allowed_to_act": False,
        "emits_act": False,
        "emits_verdict": False,
        "memory_write": False,
        "kernel_mutation": False,
        "x108_mutation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
