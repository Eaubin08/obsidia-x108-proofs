#!/usr/bin/env python3
"""Deterministic GNSS temporal-discontinuity classifier for P4 development.

The classifier never consumes attack onset or truth labels. Calibration uses only
an accepted nominal/pre-attack receiver log. Detection operates only on receiver
outputs. Because the current FGI recording has already been inspected by humans,
results on that recording are DEVELOPMENT/POST_HOC evidence, not a blind final
benchmark.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

ALGORITHM_VERSION = "P4_TEMPORAL_DISCONTINUITY_V0"
DEVELOPMENT_STATUS = "DEVELOPMENT_POST_HOC_NOT_BLIND"

RX_SEC_RE = re.compile(r"Current receiver time:\s*(?:(\d+)\s*min\s*)?(\d+)\s*s")
POS_RE = re.compile(
    r"Position at (.+?) UTC using (\d+) observations is Lat = "
    r"([-0-9.]+) \[deg\], Long = ([-0-9.]+) \[deg\], Height = ([-0-9.]+) \[m\]"
)
FIRST_FIX_RE = re.compile(
    r"First position fix at (.+?) UTC is Lat = ([-0-9.]+) \[deg\], "
    r"Long = ([-0-9.]+) \[deg\], Height = ([-0-9.]+) \[m\]"
)


@dataclass(frozen=True)
class Position:
    receiver_second: int
    utc: str
    lat: float
    lon: float
    height_m: float
    observations: int | None = None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(value: str) -> datetime:
    for fmt in ("%Y-%b-%d %H:%M:%S.%f", "%Y-%b-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported GNSS UTC format: {value}")


def ecef(position: Position) -> tuple[float, float, float]:
    a = 6378137.0
    f = 1.0 / 298.257223563
    e2 = f * (2.0 - f)
    lat = math.radians(position.lat)
    lon = math.radians(position.lon)
    n = a / math.sqrt(1.0 - e2 * math.sin(lat) ** 2)
    x = (n + position.height_m) * math.cos(lat) * math.cos(lon)
    y = (n + position.height_m) * math.cos(lat) * math.sin(lon)
    z = (n * (1.0 - e2) + position.height_m) * math.sin(lat)
    return x, y, z


def ecef_distance(a: Position, b: Position) -> float:
    ea = ecef(a)
    eb = ecef(b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(ea, eb)))


def parse_positions(path: Path) -> list[Position]:
    receiver_second = 0
    positions: list[Position] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        rx = RX_SEC_RE.search(raw)
        if rx:
            receiver_second = int(rx.group(2)) + 60 * int(rx.group(1) or 0)
            continue

        m = POS_RE.search(raw)
        if m:
            positions.append(
                Position(
                    receiver_second=receiver_second,
                    utc=m.group(1),
                    observations=int(m.group(2)),
                    lat=float(m.group(3)),
                    lon=float(m.group(4)),
                    height_m=float(m.group(5)),
                )
            )
            continue

        ff = FIRST_FIX_RE.search(raw)
        if ff and not positions:
            positions.append(
                Position(
                    receiver_second=receiver_second,
                    utc=ff.group(1),
                    observations=None,
                    lat=float(ff.group(2)),
                    lon=float(ff.group(3)),
                    height_m=float(ff.group(4)),
                )
            )
    if len(positions) < 2:
        raise ValueError(f"Need at least two PVT positions in {path}")
    return positions


def transitions(positions: Iterable[Position]) -> list[dict]:
    seq = list(positions)
    out: list[dict] = []
    for prev, cur in zip(seq, seq[1:]):
        receiver_gap = max(0.0, float(cur.receiver_second - prev.receiver_second))
        gnss_dt = (parse_utc(cur.utc) - parse_utc(prev.utc)).total_seconds()
        out.append(
            {
                "from_receiver_second": prev.receiver_second,
                "to_receiver_second": cur.receiver_second,
                "from_utc": prev.utc,
                "to_utc": cur.utc,
                "ecef_step_m": ecef_distance(prev, cur),
                "receiver_gap_s": receiver_gap,
                "gnss_utc_delta_s": gnss_dt,
                "clock_residual_s": abs(gnss_dt - receiver_gap),
            }
        )
    return out


def _max(items: list[dict], key: str) -> float:
    return max(float(item[key]) for item in items)


def calibrate(baseline_log: Path) -> dict:
    positions = parse_positions(baseline_log)
    ts = transitions(positions)

    baseline_max = {
        "ecef_step_m": _max(ts, "ecef_step_m"),
        "clock_residual_s": _max(ts, "clock_residual_s"),
        "receiver_gap_s": _max(ts, "receiver_gap_s"),
    }

    # Conservative deterministic development thresholds. These constants are
    # part of the algorithm contract and must be frozen before blind validation.
    thresholds = {
        "ecef_step_m": max(100.0, baseline_max["ecef_step_m"] * 10.0),
        "clock_residual_s": max(5.0, baseline_max["clock_residual_s"] * 10.0),
        "receiver_gap_s": max(10.0, baseline_max["receiver_gap_s"] * 5.0),
    }

    return {
        "artifact": "p4_temporal_discontinuity_calibration",
        "algorithm_version": ALGORITHM_VERSION,
        "status": DEVELOPMENT_STATUS,
        "truth_or_onset_consumed": False,
        "baseline_log_sha256": sha256_file(baseline_log),
        "baseline_position_count": len(positions),
        "baseline_transition_count": len(ts),
        "baseline_feature_maxima": baseline_max,
        "thresholds": thresholds,
        "decision_rule": {
            "ANOMALY": "at least two threshold violations in one PVT transition",
            "UNKNOWN": "exactly one threshold violation in one PVT transition",
            "NOMINAL": "no threshold violations",
        },
        "claim_boundary": "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
    }


def detect(log_path: Path, calibration: dict) -> dict:
    positions = parse_positions(log_path)
    ts = transitions(positions)
    thresholds = calibration["thresholds"]

    evaluated = []
    overall = "NOMINAL"
    first_anomaly = None

    for item in ts:
        violations = {
            "ecef_step": item["ecef_step_m"] > thresholds["ecef_step_m"],
            "clock_residual": item["clock_residual_s"] > thresholds["clock_residual_s"],
            "receiver_gap": item["receiver_gap_s"] > thresholds["receiver_gap_s"],
        }
        count = sum(bool(v) for v in violations.values())
        if count >= 2:
            decision = "ANOMALY"
            overall = "ANOMALY"
            if first_anomaly is None:
                first_anomaly = {
                    **item,
                    "violations": violations,
                    "violation_count": count,
                }
        elif count == 1:
            decision = "UNKNOWN"
            if overall == "NOMINAL":
                overall = "UNKNOWN"
        else:
            decision = "NOMINAL"

        evaluated.append({**item, "violations": violations, "decision": decision})

    return {
        "artifact": "p4_temporal_discontinuity_detection",
        "algorithm_version": calibration["algorithm_version"],
        "status": DEVELOPMENT_STATUS,
        "truth_or_onset_consumed": False,
        "input_log_sha256": sha256_file(log_path),
        "calibration_log_sha256": calibration["baseline_log_sha256"],
        "thresholds": thresholds,
        "overall_classification": overall,
        "first_anomaly": first_anomaly,
        "position_count": len(positions),
        "transition_count": len(ts),
        "max_observed": {
            "ecef_step_m": _max(ts, "ecef_step_m"),
            "clock_residual_s": _max(ts, "clock_residual_s"),
            "receiver_gap_s": _max(ts, "receiver_gap_s"),
        },
        "claim_boundary": "TRAJECTORY_DISCONTINUITY_ONLY_NO_HOSTILE_OR_CAUSAL_ATTRIBUTION",
    }


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_cal = sub.add_parser("calibrate")
    p_cal.add_argument("--baseline-log", required=True, type=Path)
    p_cal.add_argument("--out", required=True, type=Path)

    p_det = sub.add_parser("detect")
    p_det.add_argument("--log", required=True, type=Path)
    p_det.add_argument("--calibration", required=True, type=Path)
    p_det.add_argument("--out", required=True, type=Path)

    args = parser.parse_args()

    if args.command == "calibrate":
        result = calibrate(args.baseline_log)
        write_json(result, args.out)
    else:
        calibration = json.loads(args.calibration.read_text(encoding="utf-8"))
        result = detect(args.log, calibration)
        write_json(result, args.out)

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
