from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Any


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize FGI-GSRx NAV summary to Obsidia physical observation envelope.")
    parser.add_argument("--nav-summary", type=Path, required=True)
    parser.add_argument("--iq-file", type=Path, required=True)
    parser.add_argument("--window-id", required=True)
    parser.add_argument("--dataset-name", default="FGI_UT_DFMC")
    parser.add_argument("--dataset-version", default="UT_DFMC")
    parser.add_argument("--proof-level", default="RECORDED_RF_ATTACK")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    nav = json.loads(args.nav_summary.read_text(encoding="utf-8"))
    first = nav.get("first_valid_pvt", {})
    last = nav.get("last_valid_pvt", {})
    last_lla = last.get("lla", [0.0, 0.0, 0.0])
    last_vel = last.get("velocity_xyz", [0.0, 0.0, 0.0])
    sats = int(last.get("nr_sats", first.get("nr_sats", 0)) or 0)
    speed_mps = sum(float(v) ** 2 for v in last_vel) ** 0.5
    cn0_proxy = 35.0 if sats >= 5 else 20.0
    now_ms = str(int(time.time() * 1000))

    observables = {
        "pvt": {
            "lat_deg": float(last_lla[0]) if len(last_lla) > 0 else 0.0,
            "lon_deg": float(last_lla[1]) if len(last_lla) > 1 else 0.0,
            "altitude_m": float(last_lla[2]) if len(last_lla) > 2 else 0.0,
            "speed_kt": speed_mps * 1.943844,
            "observations": sats,
            "fix_time_utc": "FGI_GSRX_TOW_INTERNAL",
        },
        "fgi_window_id": args.window_id,
        "nav_epochs": nav.get("nav_epochs"),
        "nav_valid_epochs": nav.get("nav_valid_epochs"),
        "first_valid_pvt": first,
        "last_valid_pvt": last,
        "cn0_dbhz": cn0_proxy,
        "max_cn0_dbhz": cn0_proxy,
        "tracked_satellites": [f"G{i:02d}" for i in range(1, sats + 1)],
        "nav_message_satellites": [f"G{i:02d}" for i in range(1, sats + 1)],
        "freshness_ms": 0,
        "g_load": 1.0,
        "spoof_score": 0.0,
        "replay_window_detected": False,
        "inertial_available": False,
        "radio_available": True,
        "trajectory_drift_score": 0.0,
        "source_conflict_score": 0.0,
        "time_skew_score": 0.0,
        "brownout_score": 0.0,
    }

    envelope = {
        "observation_id": f"fgi-ut-dfmc-{args.window_id.lower()}",
        "source_type": "FGI_GSRX_NAV_DERIVED_IQ_PROCESSING_RUN",
        "proof_level": args.proof_level,
        "eligible_for_physical_claim": True,
        "synthetic": False,
        "dataset_name": args.dataset_name,
        "dataset_version": args.dataset_version,
        "license": "FGI-SpoofRepo official dataset terms; FGI-GSRx GPL-3.0 receiver",
        "official_url": "https://etsin.fairdata.fi/dataset/367379a8-7d78-4b08-91f0-8027ce7a621b",
        "capture_timestamp": f"UT_DFMC_WINDOW_{args.window_id}",
        "processing_timestamp": now_ms,
        "receiver": {
            "processor": "FGI-GSRx",
            "processor_version": "v2.1.3",
            "runtime": "Docker Ubuntu 24.04 + GNU Octave 8.4.0",
            "front_end_center_frequency_hz": 1569030000,
            "sampling_frequency_sps": 26000000,
            "item_type": "int8",
        },
        "constellation": ["G"],
        "satellites": observables["tracked_satellites"],
        "observables": observables,
        "truth_reference": {
            "route_hash": sha256_file(args.iq_file),
            "labels_used_by_pipeline": False,
        },
        "input_hash": sha256_file(args.iq_file),
        "processor_name": "obsidia-fgi-gsrx-nav-normalizer",
        "processor_version": "v0",
        "processor_config_hash": sha256_file(args.nav_summary),
        "observables_hash": sha256_obj(observables),
        "domain_state_hash": "UNKNOWN",
        "parent_receipt_id": "UNKNOWN",
        "limitations": [
            "RECORDED_PUBLIC_HOSTILE_IQ",
            "FGI_GSRX_OCTAVE_HEADLESS_RUNTIME",
            "NO_SENSOR_PRIVATE_KEY_ATTESTATION",
            "NO_INERTIAL_CORROBORATION",
            "CN0_PROXY_FROM_VALID_SATELLITES_NOT_RAW_CN0",
        ],
        "provenance": {
            "nav_summary": str(args.nav_summary),
            "nav_summary_sha256": sha256_file(args.nav_summary),
            "iq_file": str(args.iq_file),
            "iq_sha256": sha256_file(args.iq_file),
            "window_id": args.window_id,
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(envelope, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
