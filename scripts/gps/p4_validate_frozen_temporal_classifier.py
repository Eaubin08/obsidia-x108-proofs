#!/usr/bin/env python3
"""Run the frozen P4 temporal classifier on a receiver log without recalibration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from p4_temporal_discontinuity_classifier import detect


def calibration_from_freeze(freeze: dict) -> dict:
    return {
        "algorithm_version": freeze["algorithm_version"],
        "baseline_log_sha256": freeze["calibration_contract"]["baseline_log_sha256"],
        "thresholds": freeze["thresholds"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    freeze = json.loads(args.freeze.read_text(encoding="utf-8"))
    if freeze.get("thresholds_may_change_before_blind_validation") is not False:
        raise SystemExit("Freeze contract does not lock thresholds.")

    result = detect(args.log, calibration_from_freeze(freeze))
    result["freeze_artifact"] = freeze.get("artifact")
    result["validation_mode"] = "FROZEN_CLASSIFIER_NO_RECALIBRATION"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
