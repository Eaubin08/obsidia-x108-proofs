#!/usr/bin/env python3
"""Assess the current P5 recorded evidence against the canonical P3 contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from periphery.cross_modal.contracts_v0 import build_cross_modal_coherence_report_v0
from periphery.gps_physical.corroboration_v0 import (
    PhysicalSourceChainEvidenceV0,
    build_gps_multisource_corroboration_v0,
)
from periphery.multimodal.bridge_v0 import ModalityObservationV0


FGI_SOURCE_REF = "rf:fgi-ut-dfmc:e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72"
FGI_HARDWARE_CHAIN = "recorded-rf-chain:fgi-ut-dfmc"


def _obs(
    *,
    observation_id: str,
    receiver_impl: str,
    ecef_delta_m: float,
) -> ModalityObservationV0:
    return ModalityObservationV0(
        observation_id=observation_id,
        modality="gnss",
        observed_at="2023-11-10T14:07:54Z",
        source_ref=FGI_SOURCE_REF,
        source_hash=FGI_SOURCE_REF.split(":")[-1],
        state={
            "proof_level": "RECORDED_REAL_RF",
            "live_capture_observed": False,
            "receiver_implementation": receiver_impl,
            "ecef_delta_m": ecef_delta_m,
        },
        evidence_refs=(f"evidence:{observation_id}",),
        frame_ref="frame:wgs84-ecef",
        generated=False,
    )


def _chain(*, receiver_impl: str) -> PhysicalSourceChainEvidenceV0:
    return PhysicalSourceChainEvidenceV0(
        source_ref=FGI_SOURCE_REF,
        modality="gnss",
        instrument_ref=f"software-receiver:{receiver_impl}",
        hardware_chain_ref=FGI_HARDWARE_CHAIN,
        configuration_ref=f"config:{receiver_impl}:fgi-ut-dfmc",
        identity_evidence_refs=(f"receiver-version:{receiver_impl}",),
        source_hash_refs=(FGI_SOURCE_REF.split(":")[-1],),
        calibration_not_applicable_ref=f"recorded-replay-calibration-na:{receiver_impl}",
        time_alignment_evidence_refs=("receiver-elapsed-seconds:aligned",),
        frame_alignment_evidence_refs=("frame:wgs84-ecef",),
    )


def assess() -> dict:
    gnss_sdr = _obs(
        observation_id="fgi-ut-dfmc:gnss-sdr",
        receiver_impl="gnss-sdr",
        ecef_delta_m=14640.407,
    )
    gsrx = _obs(
        observation_id="fgi-ut-dfmc:gsrx",
        receiver_impl="fgi-gsrx",
        ecef_delta_m=14639.336,
    )

    report = build_cross_modal_coherence_report_v0(
        report_id="p5:p3-gap:fgi-cross-receiver",
        observations=(gnss_sdr, gsrx),
    )

    p3 = build_gps_multisource_corroboration_v0(
        report_id="p5:p3-gap:fgi-cross-receiver",
        primary_gnss=gnss_sdr,
        secondary=gsrx,
        primary_chain=_chain(receiver_impl="gnss-sdr"),
        secondary_chain=_chain(receiver_impl="fgi-gsrx"),
        cross_modal_report=report,
    )

    return {
        "artifact": "gps_p5_p3_independent_source_gap_assessment",
        "decision_authority": "KX108_ONLY",
        "emits_verdict": False,
        "classification": "CROSS_RECEIVER_REPRODUCIBILITY_NOT_PHYSICAL_INDEPENDENCE",
        "same_recorded_rf_source": True,
        "different_receiver_implementations": True,
        "p3": {
            "p2_live_gnss_verified": p3.p2_live_gnss_verified,
            "source_independence_proven": p3.source_independence_proven,
            "calibration_binding_proven": p3.calibration_binding_proven,
            "temporal_alignment_proven": p3.temporal_alignment_proven,
            "spatial_alignment_proven": p3.spatial_alignment_proven,
            "multi_source_corroboration_proven": p3.multi_source_corroboration_proven,
            "blockers": list(p3.blockers),
            "causal_attribution_proven": p3.causal_attribution_proven,
            "physical_truth_proven": p3.physical_truth_proven,
        },
        "allowed_claim": (
            "Two receiver implementations independently reproduce the same effect "
            "from one recorded physical RF source."
        ),
        "forbidden_claim": (
            "The GNSS-SDR and GSRx results constitute independent physical-source corroboration."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    result = assess()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
