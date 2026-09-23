from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib import request


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from domains.gps.gps_x108_gate import GpsX108Gate
from obsidia_core.guardians.path_fidelity_guard import evaluate_path_fidelity


PROOF_LEVELS = {
    "SYNTHETIC_TEST_ONLY",
    "STRUCTURED_STATE",
    "RECORDED_REAL_GNSS",
    "RECORDED_REAL_RF",
    "RECORDED_RF_ATTACK",
    "REAL_PASSIVE_GNSS",
    "HARDWARE_IN_THE_LOOP",
    "EXTERNAL_REPLICATION",
}

PHYSICAL_PROOF_LEVELS = {
    "RECORDED_REAL_GNSS",
    "RECORDED_REAL_RF",
    "RECORDED_RF_ATTACK",
    "REAL_PASSIVE_GNSS",
    "HARDWARE_IN_THE_LOOP",
    "EXTERNAL_REPLICATION",
}


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


@dataclass(frozen=True)
class PhysicalGateResult:
    status: str
    reason_codes: tuple[str, ...]
    eligible_for_p3_05: bool
    emits_verdict: bool = False
    decision_authority: str = "KX108_ONLY"


def load_observation(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("physical observation must be a JSON object")
    return data


def validate_observation(envelope: dict[str, Any]) -> list[str]:
    missing = []
    required = [
        "observation_id",
        "source_type",
        "proof_level",
        "eligible_for_physical_claim",
        "capture_timestamp",
        "processing_timestamp",
        "input_hash",
        "processor_name",
        "processor_config_hash",
        "observables_hash",
        "observables",
        "limitations",
    ]
    for key in required:
        if key not in envelope:
            missing.append(f"MISSING_{key.upper()}")

    proof_level = envelope.get("proof_level")
    if proof_level not in PROOF_LEVELS:
        missing.append("INVALID_PROOF_LEVEL")

    if proof_level == "SYNTHETIC_TEST_ONLY" and envelope.get("eligible_for_physical_claim") is not False:
        missing.append("SYNTHETIC_MUST_NOT_BE_PHYSICAL_CLAIM")

    if envelope.get("eligible_for_physical_claim") is True and proof_level not in PHYSICAL_PROOF_LEVELS:
        missing.append("PHYSICAL_CLAIM_REQUIRES_PHYSICAL_PROOF_LEVEL")

    observables = envelope.get("observables", {})
    if isinstance(observables, dict):
        expected = sha256_obj(observables)
        if envelope.get("observables_hash") not in {expected, "UNKNOWN"}:
            missing.append("OBSERVABLES_HASH_MISMATCH")
    else:
        missing.append("OBSERVABLES_NOT_OBJECT")

    return missing


def physical_reality_gate(envelope: dict[str, Any]) -> PhysicalGateResult:
    reasons = validate_observation(envelope)
    proof_level = envelope.get("proof_level")
    limitations = envelope.get("limitations", []) or []

    if proof_level == "SYNTHETIC_TEST_ONLY":
        reasons.append("SYNTHETIC_TEST_ONLY_NOT_PHYSICAL")
    if "NO_HARDWARE_DETECTED" in limitations:
        reasons.append("NO_HARDWARE_DETECTED")
    if envelope.get("input_hash") in {"", "UNKNOWN", None}:
        reasons.append("INPUT_HASH_UNKNOWN")

    unique = tuple(sorted(set(reasons)))
    if any(r.startswith("MISSING_") or r.endswith("MISMATCH") for r in unique):
        status = "REJECTED"
    elif "NO_HARDWARE_DETECTED" in unique:
        status = "UNKNOWN"
    elif unique:
        status = "UNKNOWN" if "SYNTHETIC_TEST_ONLY_NOT_PHYSICAL" in unique else "DEGRADED"
    else:
        status = "AUTHENTICATED"

    return PhysicalGateResult(
        status=status,
        reason_codes=unique,
        eligible_for_p3_05=status in {"AUTHENTICATED", "DEGRADED", "UNKNOWN"}
        and "NO_HARDWARE_DETECTED" not in unique,
    )


def observation_to_domain_payload(envelope: dict[str, Any]) -> dict[str, Any]:
    obs = envelope.get("observables", {}) or {}
    pvt = obs.get("pvt", {}) if isinstance(obs.get("pvt"), dict) else {}
    cn0 = obs.get("cn0_dbhz", obs.get("snr", 0.5))
    try:
        signal_noise_ratio = min(1.0, max(0.0, float(cn0) / 50.0))
    except Exception:
        signal_noise_ratio = 0.5

    payload = {
        "flow_type": "TRAJECTORY_DECISION",
        "mission_id": envelope.get("dataset_name", "GPS-PHYSICAL-V0"),
        "flight_id": envelope.get("observation_id", "PHYSICAL-OBS"),
        "altitude": float(pvt.get("altitude_m", 0.0) or 0.0),
        "ground_speed": float(pvt.get("speed_kt", 0.0) or 0.0),
        "gps_status": "ONLINE" if obs else "UNKNOWN",
        "satellites_count": len(envelope.get("satellites", []) or []),
        "signal_noise_ratio": signal_noise_ratio,
        "freshness_ms": float(obs.get("freshness_ms", 0.0) or 0.0),
        "g_load": float(obs.get("g_load", 1.0) or 1.0),
        "spoof_score": float(obs.get("spoof_score", 0.0) or 0.0),
        "replay_window_detected": bool(obs.get("replay_window_detected", False)),
        "sensor_attested": envelope.get("eligible_for_physical_claim") is True,
        "gps_available": bool(obs),
        "inertial_available": bool(obs.get("inertial_available", False)),
        "radio_available": bool(obs.get("radio_available", False)),
        "trajectory_drift_score": float(obs.get("trajectory_drift_score", 0.0) or 0.0),
        "source_conflict_score": float(obs.get("source_conflict_score", 0.0) or 0.0),
        "time_skew_score": float(obs.get("time_skew_score", 0.0) or 0.0),
        "brownout_score": float(obs.get("brownout_score", 0.0) or 0.0),
        "attestation_ready": envelope.get("eligible_for_physical_claim") is True,
        "rollback_possible": True,
        "authorized_route_hash": envelope.get("truth_reference", {}).get("route_hash", envelope.get("input_hash")),
    }
    payload["domain_state_hash"] = sha256_obj(payload)
    return payload


def run_observation(path: Path) -> dict[str, Any]:
    envelope = load_observation(path)
    gate = physical_reality_gate(envelope)
    payload = observation_to_domain_payload(envelope)
    p4_20 = evaluate_path_fidelity(payload).to_dict()
    x108 = GpsX108Gate().evaluate(payload)
    return {
        "mode": "PHYSICAL_OBSERVATION_ENVELOPE",
        "input_file": str(path),
        "physical_gate": asdict(gate),
        "domain_payload": payload,
        "p4_20_evidence": p4_20,
        "x108_result": x108,
        "claim_boundary": "Physical claim allowed only if proof_level is real and eligible_for_physical_claim is true.",
    }


def _rinex_lines(path: Path) -> list[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="ascii", errors="replace") as f:
        return f.readlines()


def _parse_rinex_epoch_v2(line: str) -> tuple[str, list[str]] | None:
    if len(line) < 32 or line[:3].strip() == "":
        return None
    try:
        year = int(line[1:3])
        month = int(line[4:6])
        day = int(line[7:9])
        hour = int(line[10:12])
        minute = int(line[13:15])
        sec = float(line[16:26])
        flag = int(line[28:29])
        sat_count = int(line[29:32])
    except ValueError:
        return None
    if flag > 1:
        return None
    full_year = 2000 + year if year < 80 else 1900 + year
    epoch = f"{full_year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{sec:06.3f}Z"
    sat_blob = line[32:].rstrip("\n")
    satellites = [sat_blob[i : i + 3].strip() for i in range(0, len(sat_blob), 3)]
    satellites = [s for s in satellites if s]
    return epoch, satellites[:sat_count]


def parse_rinex_observation_file(path: Path, station_log: Path | None = None) -> dict[str, Any]:
    lines = _rinex_lines(path)
    header: dict[str, Any] = {
        "rinex_version": "UNKNOWN",
        "marker_name": "UNKNOWN",
        "receiver": "UNKNOWN",
        "antenna": "UNKNOWN",
        "approx_position_xyz_m": [],
        "obs_types": [],
    }
    header_end = 0
    for idx, line in enumerate(lines):
        label = line[60:].strip() if len(line) >= 60 else ""
        value = line[:60].rstrip()
        if label == "RINEX VERSION / TYPE":
            header["rinex_version"] = value[:20].strip()
            header["rinex_type"] = value[20:40].strip()
        elif label == "MARKER NAME":
            header["marker_name"] = value.strip()
        elif label == "REC # / TYPE / VERS":
            header["receiver"] = value.strip()
        elif label == "ANT # / TYPE":
            header["antenna"] = value.strip()
        elif label == "APPROX POSITION XYZ":
            header["approx_position_xyz_m"] = [float(x) for x in value.split()[:3]]
        elif label == "# / TYPES OF OBSERV":
            parts = value.split()
            if parts:
                header["obs_types"].extend(parts[1:])
        elif label == "END OF HEADER":
            header_end = idx + 1
            break

    epochs: list[dict[str, Any]] = []
    constellation_counts: dict[str, int] = {}
    unique_sats: set[str] = set()
    for line in lines[header_end:]:
        parsed = _parse_rinex_epoch_v2(line)
        if not parsed:
            continue
        epoch, satellites = parsed
        for sat in satellites:
            unique_sats.add(sat)
            constellation_counts[sat[0]] = constellation_counts.get(sat[0], 0) + 1
        epochs.append({"epoch": epoch, "satellites": satellites})

    station_log_hash = sha256_file(station_log) if station_log and station_log.exists() else "NOT_PROVIDED"
    return {
        "file": str(path),
        "file_sha256": sha256_file(path),
        "station_log": str(station_log) if station_log else "NOT_PROVIDED",
        "station_log_sha256": station_log_hash,
        "header": header,
        "epoch_count": len(epochs),
        "first_epoch": epochs[0]["epoch"] if epochs else "UNKNOWN",
        "last_epoch": epochs[-1]["epoch"] if epochs else "UNKNOWN",
        "sample_epochs": epochs[:5],
        "unique_satellites": sorted(unique_sats),
        "constellation_counts": constellation_counts,
        "observed_constellations": sorted(constellation_counts.keys()),
    }


def rinex_to_observation_envelope(
    rinex_path: Path,
    station_log: Path | None,
    source_url: str,
    license_text: str,
) -> dict[str, Any]:
    parsed = parse_rinex_observation_file(rinex_path, station_log)
    now_ms = str(int(time.time() * 1000))
    obs = {
        "rinex_version": parsed["header"].get("rinex_version"),
        "marker_name": parsed["header"].get("marker_name"),
        "receiver": parsed["header"].get("receiver"),
        "antenna": parsed["header"].get("antenna"),
        "epoch_count": parsed["epoch_count"],
        "first_epoch": parsed["first_epoch"],
        "last_epoch": parsed["last_epoch"],
        "observed_constellations": parsed["observed_constellations"],
        "unique_satellite_count": len(parsed["unique_satellites"]),
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
        "observation_id": f"rinex-{parsed['header'].get('marker_name', 'UNKNOWN').lower()}-{parsed['first_epoch']}",
        "source_type": "RINEX_OBSERVATION_FILE",
        "proof_level": "RECORDED_REAL_GNSS",
        "eligible_for_physical_claim": True,
        "synthetic": False,
        "dataset_name": "NOAA_NGS_NCN_CORS_RINEX",
        "dataset_version": parsed["first_epoch"][:10],
        "license": license_text,
        "official_url": source_url,
        "capture_timestamp": parsed["first_epoch"],
        "processing_timestamp": now_ms,
        "receiver": {
            "station": parsed["header"].get("marker_name", "UNKNOWN"),
            "receiver": parsed["header"].get("receiver", "UNKNOWN"),
            "antenna": parsed["header"].get("antenna", "UNKNOWN"),
            "station_log_sha256": parsed["station_log_sha256"],
        },
        "constellation": parsed["observed_constellations"],
        "satellites": parsed["unique_satellites"],
        "observables": obs,
        "truth_reference": {
            "route_hash": parsed["file_sha256"],
            "labels_used_by_pipeline": False,
        },
        "input_hash": parsed["file_sha256"],
        "processor_name": "obsidia-rinex-v2-observation-parser",
        "processor_version": "v0",
        "processor_config_hash": sha256_obj({"mode": "rinex_v2_header_epoch_parser"}),
        "observables_hash": sha256_obj(obs),
        "domain_state_hash": "UNKNOWN",
        "parent_receipt_id": "UNKNOWN",
        "limitations": [
            "RINEX_OBSERVABLES_ONLY",
            "NO_RAW_RF_IQ",
            "NO_SENSOR_PRIVATE_KEY_ATTESTATION",
            "NO_PVT_SOLUTION_COMPUTED",
        ],
        "provenance": parsed,
    }
    return envelope


def _http_post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    started = int(time.time() * 1000)
    try:
        with request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except Exception as exc:
        return {
            "endpoint": url,
            "timestamp_ms": started,
            "status_http": "ERROR",
            "error": str(exc),
            "payload_sha256": sha256_obj(payload),
            "raw_response": "",
        }
    return {
        "endpoint": url,
        "timestamp_ms": started,
        "status_http": status,
        "payload": payload,
        "payload_sha256": sha256_obj(payload),
        "raw_response": raw,
        "raw_response_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    }


def run_rinex(
    rinex_path: Path,
    station_log: Path | None,
    source_url: str,
    license_text: str,
    kernel_endpoint: str,
) -> dict[str, Any]:
    envelope = rinex_to_observation_envelope(rinex_path, station_log, source_url, license_text)
    gate = physical_reality_gate(envelope)
    payload = observation_to_domain_payload(envelope)
    p4_20 = evaluate_path_fidelity(payload).to_dict()
    x108 = GpsX108Gate().evaluate(payload)
    http_probe = _http_post_json(kernel_endpoint, x108.get("ir_payload", payload))
    return {
        "mode": "RINEX_RECORDED_REAL_GNSS",
        "proof_level": "RECORDED_REAL_GNSS",
        "synthetic": False,
        "input_file": str(rinex_path),
        "station_log": str(station_log) if station_log else "NOT_PROVIDED",
        "official_url": source_url,
        "license": license_text,
        "physical_gate": asdict(gate),
        "observation_envelope": envelope,
        "domain_payload": payload,
        "p4_20_evidence": p4_20,
        "x108_result": x108,
        "kernel_http_evidence": http_probe,
    }


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
TRACKING_RE = re.compile(r"Tracking of GPS L1 C/A signal started on channel (?P<channel>\d+) for satellite GPS PRN (?P<prn>\d+)")
NAV_RE = re.compile(r"New GPS NAV message received.*GPS PRN (?P<prn>\d+).*CN0=(?P<cn0>[0-9.]+) dB-Hz")
FIRST_FIX_RE = re.compile(
    r"First position fix at (?P<time>.+?) UTC is Lat = (?P<lat>-?[0-9.]+) \[deg\], "
    r"Long = (?P<lon>-?[0-9.]+) \[deg\], Height = (?P<height>-?[0-9.]+) \[m\], with GDOP = (?P<gdop>[0-9.]+)"
)
POSITION_RE = re.compile(
    r"Position at (?P<time>.+?) UTC using (?P<observations>\d+) observations is Lat = (?P<lat>-?[0-9.]+) \[deg\], "
    r"Long = (?P<lon>-?[0-9.]+) \[deg\], Height = (?P<height>-?[0-9.]+) \[m\]"
)
VELOCITY_RE = re.compile(r"Velocity: East: (?P<east>-?[0-9.]+) \[m/s\], North: (?P<north>-?[0-9.]+) \[m/s\], Up = (?P<up>-?[0-9.]+) \[m/s\]")
RUN_TIME_RE = re.compile(r"Total GNSS-SDR run time: (?P<seconds>[0-9.]+) \[seconds\]")


def parse_gnss_sdr_stdout(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = ANSI_RE.sub("", raw)
    tracked: dict[str, set[int]] = {}
    cn0_by_prn: dict[str, list[float]] = {}
    positions: list[dict[str, Any]] = []
    velocities: list[dict[str, float]] = []
    first_fix: dict[str, Any] | None = None
    loss_of_lock_count = 0
    run_time_seconds = 0.0

    for line in clean.splitlines():
        if "Loss of lock" in line:
            loss_of_lock_count += 1
        if m := TRACKING_RE.search(line):
            tracked.setdefault(f"G{int(m.group('prn')):02d}", set()).add(int(m.group("channel")))
        if m := NAV_RE.search(line):
            cn0_by_prn.setdefault(f"G{int(m.group('prn')):02d}", []).append(float(m.group("cn0")))
        if m := FIRST_FIX_RE.search(line):
            first_fix = {
                "time_utc": m.group("time"),
                "lat_deg": float(m.group("lat")),
                "lon_deg": float(m.group("lon")),
                "altitude_m": float(m.group("height")),
                "gdop": float(m.group("gdop")),
            }
        if m := POSITION_RE.search(line):
            positions.append(
                {
                    "time_utc": m.group("time"),
                    "observations": int(m.group("observations")),
                    "lat_deg": float(m.group("lat")),
                    "lon_deg": float(m.group("lon")),
                    "altitude_m": float(m.group("height")),
                }
            )
        if m := VELOCITY_RE.search(line):
            velocities.append(
                {
                    "east_mps": float(m.group("east")),
                    "north_mps": float(m.group("north")),
                    "up_mps": float(m.group("up")),
                }
            )
        if m := RUN_TIME_RE.search(line):
            run_time_seconds = float(m.group("seconds"))

    avg_cn0 = 0.0
    all_cn0 = [v for values in cn0_by_prn.values() for v in values]
    if all_cn0:
        avg_cn0 = sum(all_cn0) / len(all_cn0)

    last_velocity = velocities[-1] if velocities else {"east_mps": 0.0, "north_mps": 0.0, "up_mps": 0.0}
    ground_speed_mps = math.hypot(last_velocity["east_mps"], last_velocity["north_mps"])
    last_position = positions[-1] if positions else first_fix or {}
    return {
        "stdout_file": str(path),
        "stdout_sha256": sha256_file(path),
        "tracked_satellites": sorted(tracked),
        "tracking_channels": {sat: sorted(channels) for sat, channels in tracked.items()},
        "nav_message_satellites": sorted(cn0_by_prn),
        "cn0_by_prn_dbhz": {sat: values for sat, values in sorted(cn0_by_prn.items())},
        "avg_cn0_dbhz": avg_cn0,
        "max_cn0_dbhz": max(all_cn0) if all_cn0 else 0.0,
        "first_fix": first_fix,
        "position_count": len(positions),
        "last_position": last_position,
        "last_velocity_mps": last_velocity,
        "ground_speed_mps": ground_speed_mps,
        "ground_speed_kt": ground_speed_mps * 1.943844,
        "loss_of_lock_count": loss_of_lock_count,
        "run_time_seconds": run_time_seconds,
    }


def gnss_sdr_run_to_observation_envelope(
    run_dir: Path,
    iq_file: Path,
    archive_file: Path,
    config_file: Path,
    source_url: str,
    license_text: str,
) -> dict[str, Any]:
    stdout_path = run_dir / "gnss_sdr_run_stdout_modern.log"
    parsed = parse_gnss_sdr_stdout(stdout_path)
    output_files = {
        "stdout_log": stdout_path,
        "gnss_sdr_log": run_dir / "gnss-sdr.log",
        "observables_dat": run_dir / "observables.dat",
        "pvt_dat": run_dir / "PVT.dat",
        "rinex_obs": run_dir / "GSDR214v18.26O",
        "rinex_nav": run_dir / "GSDR214v18.26N",
        "geojson": next(iter(run_dir.glob("PVT_*.geojson")), None),
        "gpx": next(iter(run_dir.glob("PVT_*.gpx")), None),
        "kml": next(iter(run_dir.glob("PVT_*.kml")), None),
    }
    output_hashes = {
        key: sha256_file(path)
        for key, path in output_files.items()
        if path is not None and path.exists()
    }
    pvt = {
        "lat_deg": parsed.get("last_position", {}).get("lat_deg", 0.0),
        "lon_deg": parsed.get("last_position", {}).get("lon_deg", 0.0),
        "altitude_m": parsed.get("last_position", {}).get("altitude_m", 0.0),
        "speed_kt": parsed.get("ground_speed_kt", 0.0),
        "observations": parsed.get("last_position", {}).get("observations", 0),
        "fix_time_utc": parsed.get("last_position", {}).get("time_utc", "UNKNOWN"),
    }
    observables = {
        "pvt": pvt,
        "cn0_dbhz": parsed["avg_cn0_dbhz"],
        "max_cn0_dbhz": parsed["max_cn0_dbhz"],
        "tracked_satellites": parsed["tracked_satellites"],
        "nav_message_satellites": parsed["nav_message_satellites"],
        "tracking_channels": parsed["tracking_channels"],
        "cn0_by_prn_dbhz": parsed["cn0_by_prn_dbhz"],
        "first_fix": parsed["first_fix"],
        "position_count": parsed["position_count"],
        "last_velocity_mps": parsed["last_velocity_mps"],
        "loss_of_lock_count": parsed["loss_of_lock_count"],
        "run_time_seconds": parsed["run_time_seconds"],
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
    now_ms = str(int(time.time() * 1000))
    return {
        "observation_id": "iq-cttc-2013-04-04-gnss-sdr-real-rf",
        "source_type": "GNSS_SDR_IQ_PROCESSING_RUN",
        "proof_level": "RECORDED_REAL_RF",
        "eligible_for_physical_claim": True,
        "synthetic": False,
        "dataset_name": "GNSS_SDR_CTTC_2013_04_04_SAMPLE",
        "dataset_version": "2013-04-04",
        "license": license_text,
        "official_url": source_url,
        "capture_timestamp": parsed.get("first_fix", {}).get("time_utc", "2013-04-04") if parsed.get("first_fix") else "2013-04-04",
        "processing_timestamp": now_ms,
        "receiver": {
            "processor": "gnss-sdr",
            "processor_version": "0.0.21.git-next-2a7214a4f",
            "front_end_center_frequency_hz": 1575420000,
            "sampling_frequency_sps": 4000000,
            "item_type": "ishort",
        },
        "constellation": ["G"],
        "satellites": parsed["tracked_satellites"],
        "observables": observables,
        "truth_reference": {
            "route_hash": sha256_file(iq_file),
            "labels_used_by_pipeline": False,
        },
        "input_hash": sha256_file(iq_file),
        "processor_name": "obsidia-gnss-sdr-stdout-normalizer",
        "processor_version": "v0",
        "processor_config_hash": sha256_file(config_file),
        "observables_hash": sha256_obj(observables),
        "domain_state_hash": "UNKNOWN",
        "parent_receipt_id": "UNKNOWN",
        "limitations": [
            "RECORDED_PUBLIC_IQ",
            "GNSS_SDR_CONTAINER_RUNTIME",
            "NO_SENSOR_PRIVATE_KEY_ATTESTATION",
            "NO_INERTIAL_CORROBORATION",
        ],
        "provenance": {
            "archive_file": str(archive_file),
            "archive_sha256": sha256_file(archive_file),
            "iq_file": str(iq_file),
            "iq_sha256": sha256_file(iq_file),
            "config_file": str(config_file),
            "config_sha256": sha256_file(config_file),
            "run_dir": str(run_dir),
            "output_hashes": output_hashes,
            "parsed_stdout": parsed,
        },
    }


def run_gnss_sdr_run(
    run_dir: Path,
    iq_file: Path,
    archive_file: Path,
    config_file: Path,
    source_url: str,
    license_text: str,
    kernel_endpoint: str,
) -> dict[str, Any]:
    envelope = gnss_sdr_run_to_observation_envelope(run_dir, iq_file, archive_file, config_file, source_url, license_text)
    gate = physical_reality_gate(envelope)
    payload = observation_to_domain_payload(envelope)
    p4_20 = evaluate_path_fidelity(payload).to_dict()
    x108 = GpsX108Gate().evaluate(payload)
    http_probe = _http_post_json(kernel_endpoint, x108.get("ir_payload", payload))
    return {
        "mode": "GNSS_SDR_RECORDED_REAL_RF",
        "proof_level": "RECORDED_REAL_RF",
        "synthetic": False,
        "physical_gate": asdict(gate),
        "observation_envelope": envelope,
        "domain_payload": payload,
        "p4_20_evidence": p4_20,
        "x108_result": x108,
        "kernel_http_evidence": http_probe,
    }


def detect_live_passive_receiver() -> dict[str, Any]:
    gnss_sdr = shutil.which("gnss-sdr")
    docker = shutil.which("docker")
    candidates = []
    for env_name in ("OBSIDIA_GNSS_DEVICE", "OBSIDIA_SDR_DEVICE"):
        if os.environ.get(env_name):
            candidates.append({"source": env_name, "value": os.environ[env_name]})

    status = "NO_HARDWARE_DETECTED"
    if candidates:
        status = "ENV_CONFIGURED_DEVICE_UNVERIFIED"

    return {
        "status": status,
        "proof_level": "REAL_PASSIVE_GNSS" if candidates else "STRUCTURED_STATE",
        "eligible_for_physical_claim": bool(candidates),
        "gnss_sdr_path": gnss_sdr or "NOT_FOUND",
        "docker_path": docker or "NOT_FOUND",
        "detected_candidates": candidates,
        "limitations": [] if candidates else ["NO_HARDWARE_DETECTED", "WINDOWS_HARDWARE_ENUMERATION_NOT_AVAILABLE"],
    }


def run_live_passive() -> dict[str, Any]:
    detection = detect_live_passive_receiver()
    now = str(int(time.time() * 1000))
    observables = {}
    envelope = {
        "observation_id": f"live-passive-{now}",
        "source_type": "LIVE_PASSIVE_RECEIVER",
        "proof_level": detection["proof_level"],
        "eligible_for_physical_claim": detection["eligible_for_physical_claim"],
        "dataset_name": "local-live-passive",
        "dataset_version": "v0",
        "license": "LOCAL_OPERATOR",
        "official_url": "UNKNOWN",
        "capture_timestamp": now,
        "processing_timestamp": now,
        "receiver": detection,
        "constellation": [],
        "satellites": [],
        "observables": observables,
        "truth_reference": {},
        "input_hash": "UNKNOWN",
        "processor_name": "obsidia-live-passive-adapter",
        "processor_version": "v0",
        "processor_config_hash": sha256_obj(detection),
        "observables_hash": sha256_obj(observables),
        "domain_state_hash": "UNKNOWN",
        "parent_receipt_id": "UNKNOWN",
        "limitations": detection["limitations"],
    }
    gate = physical_reality_gate(envelope)
    return {
        "mode": "LIVE_PASSIVE_ADAPTER",
        "status": detection["status"],
        "physical_gate": asdict(gate),
        "envelope": envelope,
        "blocked": detection["status"] == "NO_HARDWARE_DETECTED",
        "next_human_action": "Connect a passive GNSS/SDR receiver and set OBSIDIA_GNSS_DEVICE or provide GNSS-SDR output.",
    }


def run_blind_benchmark(manifest_path: Path) -> dict[str, Any]:
    manifest = load_observation(manifest_path)
    cases = manifest.get("cases", [])
    results = []
    for case in cases:
        public_path = ROOT / case["public_observation_path"]
        result = run_observation(public_path)
        results.append(
            {
                "case_id": case.get("case_id", public_path.stem),
                "public_observation_path": case["public_observation_path"],
                "x108_verdict": result["x108_result"].get("verdict"),
                "x108_source": result["x108_result"].get("source"),
                "physical_gate_status": result["physical_gate"]["status"],
                "receipt_id": result["x108_result"].get("receipt", {}).get("os3_ticket", {}).get("ticket_id"),
            }
        )
    return {
        "mode": "BLIND_BENCHMARK",
        "case_count": len(results),
        "results": results,
        "truth_manifest_used_by_pipeline": False,
    }


def write_result(result: dict[str, Any], out: Path | None) -> None:
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Obsidia GPS Physical Signal Periphery V0")
    parser.add_argument("--physical-observation", type=Path)
    parser.add_argument("--rinex", type=Path)
    parser.add_argument("--gnss-sdr-run", type=Path)
    parser.add_argument("--iq-file", type=Path)
    parser.add_argument("--archive-file", type=Path)
    parser.add_argument("--config-file", type=Path)
    parser.add_argument("--station-log", type=Path)
    parser.add_argument("--source-url", default="UNKNOWN")
    parser.add_argument("--license", default="UNKNOWN")
    parser.add_argument("--kernel-endpoint", default="http://127.0.0.1:3001/kernel/ragnarok")
    parser.add_argument("--live-passive", action="store_true")
    parser.add_argument("--blind-benchmark", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    selected = sum(bool(x) for x in [args.physical_observation, args.rinex, args.gnss_sdr_run, args.live_passive, args.blind_benchmark])
    if selected != 1:
        parser.error("select exactly one mode")

    if args.physical_observation:
        result = run_observation(args.physical_observation)
    elif args.rinex:
        result = run_rinex(
            args.rinex,
            args.station_log,
            args.source_url,
            args.license,
            args.kernel_endpoint,
        )
    elif args.gnss_sdr_run:
        if not args.iq_file or not args.archive_file or not args.config_file:
            parser.error("--gnss-sdr-run requires --iq-file, --archive-file, and --config-file")
        result = run_gnss_sdr_run(
            args.gnss_sdr_run,
            args.iq_file,
            args.archive_file,
            args.config_file,
            args.source_url,
            args.license,
            args.kernel_endpoint,
        )
    elif args.live_passive:
        result = run_live_passive()
    else:
        result = run_blind_benchmark(args.blind_benchmark)

    write_result(result, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
