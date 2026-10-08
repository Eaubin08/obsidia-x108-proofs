#!/usr/bin/env python3
"""R6 Defense smoke: recorded real RF -> Brody -> cognitive join -> KX dry-run.

Uses the committed CTTC recorded-real-RF artifact and its recorded X108 response.
No RF is replayed here; this is an evidence-consumption integration smoke.
"""
from __future__ import annotations

import argparse
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
from periphery.cognition.gps_defense_recorded_evidence_v0 import (
    build_recorded_gps_sigma_envelope_v0,
)


DEFAULT_ARTIFACT = (
    ROOT
    / "artifacts"
    / "gps_iq_cttc_2013_04_04_recorded_real_rf_result.json"
)


def _gps_micro() -> dict[str, Any]:
    return {
        "micro_core_version": "R6_DEFENSE_RECORDED_EVIDENCE_SMOKE",
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


def build_report(artifact_path: Path) -> dict[str, Any]:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    envelope = build_recorded_gps_sigma_envelope_v0(artifact)

    message = (
        "Explique en lecture seule le statut de cette preuve GPS enregistrée, "
        "sans décider ni agir."
    )

    brody = run_brody_real_response_pipeline(
        message=message,
        language="fr",
        session_id="r6-defense-recorded-rf-smoke",
    )

    joined = run_real_cognitive_join(
        message=message,
        language="fr",
        session_id="r6-defense-recorded-rf-smoke",
        precomputed_micro_core=_gps_micro(),
        precomputed_brody_runtime=brody,
        precomputed_domain_sigma_envelope=envelope,
    )

    sigma = joined.get("sigma_domain_packet") or {}
    ticket = joined.get("decision_ticket_dry_run") or {}
    components = joined.get("components") or {}

    checks = {
        "physical_proof_level_preserved": (
            sigma.get("proof_status") == "RECORDED_REAL_RF"
        ),
        "recorded_x108_gate_preserved": (
            sigma.get("x108_gate") == "HOLD"
        ),
        "recorded_decision_id_preserved": (
            sigma.get("recorded_decision_id")
            == envelope.get("recorded_decision_id")
        ),
        "evidence_envelope_preserved_exactly": (
            sigma == envelope
        ),
        "sigma_envelope_hash_present": (
            isinstance(joined.get("sigma_domain_packet_sha256"), str)
            and len(joined.get("sigma_domain_packet_sha256")) == 64
        ),
        "precomputed_sigma_used": (
            joined.get("sigma_domain_packet_source")
            == "PRECOMPUTED_READONLY"
        ),
        "real_brody_runtime_joined": (
            components.get("W3_BRODY")
            == "READY:REAL_RUNTIME_ADAPTER"
        ),
        "kx108_dry_run_reached": (
            joined.get("kx108_admission") == "DRY_RUN"
            and ticket.get("dry_run") is True
        ),
        "kx108_only_preserved": (
            joined.get("decision_authority") == "KX108_ONLY"
            and ticket.get("decision_authority") == "KX108_ONLY"
        ),
        "no_act": (
            joined.get("allowed_to_act") is False
            and joined.get("emits_act") is False
            and ticket.get("emits_act") is False
        ),
        "no_decision_promotion": (
            joined.get("allowed_to_decide") is False
            and joined.get("emits_verdict") is False
            and sigma.get(
                "recorded_x108_gate_is_evidence_not_brody_authority"
            )
            is True
        ),
    }

    verified = all(bool(value) for value in checks.values())

    return {
        "artifact": "r6_defense_recorded_real_rf_to_brody_smoke",
        "status": (
            "RECORDED_REAL_RF_TO_BRODY_VERIFIED"
            if verified
            else "RECORDED_REAL_RF_TO_BRODY_FAILED_CLOSED"
        ),
        "verified": verified,
        "source_artifact": str(artifact_path.relative_to(ROOT)),
        "source_proof_level": envelope.get("proof_status"),
        "source_observation_id": envelope.get("observation_id"),
        "source_evidence_artifact_sha256": envelope.get(
            "evidence_artifact_sha256"
        ),
        "recorded_market_verdict": envelope.get("market_verdict"),
        "recorded_x108_gate": envelope.get("x108_gate"),
        "recorded_reason_code": envelope.get("reason_code"),
        "brody_response_source": brody.get("response_source"),
        "cognitive_join_status": joined.get("status"),
        "cognitive_join_completeness": joined.get("completeness"),
        "cognitive_ticket_decision": ticket.get("decision"),
        "cognitive_ticket_note": (
            "Context admission only; never a trajectory authorization."
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
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    report = build_report(args.artifact)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
