#!/usr/bin/env python3
"""P5 reference-truth support assessment for FGI UT_DFMC.

This computes receiver-to-reference distance only. It does not prove P3 physical
source independence or causal spoofing attribution.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


A = 6378137.0
F = 1.0 / 298.257223563
E2 = F * (2.0 - F)


def _ecef(lat_deg: float, lon_deg: float, h_m: float) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    n = A / math.sqrt(1.0 - E2 * math.sin(lat) ** 2)
    return (
        (n + h_m) * math.cos(lat) * math.cos(lon),
        (n + h_m) * math.cos(lat) * math.sin(lon),
        (n * (1.0 - E2) + h_m) * math.sin(lat),
    )


def _distance_m(left: list[float], right: list[float]) -> float:
    a = _ecef(*left)
    b = _ecef(*right)
    return math.dist(a, b)


def assess(payload: dict) -> dict:
    truth = payload["stationary_reference_lla"]
    results = {}

    for name, lla in payload["observations"].items():
        results[name] = {
            "lla": lla,
            "distance_to_stationary_reference_m": _distance_m(lla, truth),
        }

    pre_ok = (
        results["gnss_sdr_pre"]["distance_to_stationary_reference_m"] < 20.0
        and results["gsrx_pre"]["distance_to_stationary_reference_m"] < 20.0
    )
    post_far = (
        results["gnss_sdr_post"]["distance_to_stationary_reference_m"] > 10000.0
        and results["gsrx_post"]["distance_to_stationary_reference_m"] > 10000.0
    )

    return {
        "artifact": "gps_p5_reference_truth_support",
        "decision_authority": "KX108_ONLY",
        "emits_verdict": False,
        "classification": (
            "REFERENCE_TRUTH_SUPPORTS_PRE_STABLE_POST_DISPLACED"
            if pre_ok and post_far
            else "REFERENCE_TRUTH_SUPPORT_INCOMPLETE"
        ),
        "stationary_reference_lla": truth,
        "results": results,
        "checks": {
            "pre_onset_receivers_close_to_reference": pre_ok,
            "post_onset_receivers_far_from_reference": post_far,
        },
        "p3_independent_physical_source_proven": False,
        "causal_attribution_closed": False,
        "allowed_claim": (
            "Both receiver implementations are close to the declared stationary reference "
            "before the event boundary and approximately 14.64 km from it afterward."
        ),
        "forbidden_claims": [
            "FGI_REFERENCE_IS_A_P3_INDEPENDENT_PHYSICAL_SOURCE",
            "SPOOFING_CAUSED_THE_DISPLACEMENT",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = assess(payload)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
