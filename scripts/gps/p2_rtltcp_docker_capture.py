#!/usr/bin/env python3
"""P2 live passive GNSS capture through Windows rtl_tcp -> Docker GNSS-SDR.

The adapter is fail-closed:
- it accepts only RtlTcp_Signal_Source configs;
- it refuses File_Signal_Source/offline configs;
- it requires a bound receiver identity manifest/evidence pair;
- it promotes only when runtime GNSS observables are actually parsed.

Decision authority remains KX108_ONLY.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from domains.gps.gps_x108_gate import GpsX108Gate
import importlib.util

_PSP_PATH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "physical_signal_periphery.py"
_PSP_SPEC = importlib.util.spec_from_file_location("physical_signal_periphery_p2_rtltcp", _PSP_PATH)
if _PSP_SPEC is None or _PSP_SPEC.loader is None:
    raise RuntimeError(f"Cannot load physical signal periphery: {_PSP_PATH}")
PSP = importlib.util.module_from_spec(_PSP_SPEC)
sys.modules[_PSP_SPEC.name] = PSP
_PSP_SPEC.loader.exec_module(PSP)
sha256_file = PSP.sha256_file
sha256_obj = PSP.sha256_obj
parse_gnss_sdr_stdout = PSP.parse_gnss_sdr_stdout
physical_reality_gate = PSP.physical_reality_gate
observation_to_domain_payload = PSP.observation_to_domain_payload
evaluate_path_fidelity = PSP.evaluate_path_fidelity
_http_post_json = PSP._http_post_json
_verify_receiver_identity_manifest = PSP._verify_receiver_identity_manifest
_live_capture_observed = PSP._live_capture_observed

EXPECTED_IMPLEMENTATION = "RtlTcp_Signal_Source"
EXPECTED_FREQ_HZ = 1575420000
EXPECTED_SAMPLE_RATE = 2000000
EXPECTED_PORT = 1234
EXPECTED_CONTAINER_HOST = "host.docker.internal"


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith(";") or line.startswith("[") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.split(";", 1)[0].strip()
    return values


def validate_live_config(path: Path) -> list[str]:
    if not path.exists():
        return ["GNSS_SDR_CONFIG_NOT_FOUND"]
    cfg = parse_config(path)
    errors: list[str] = []

    impl = cfg.get("SignalSource.implementation", "")
    if impl != EXPECTED_IMPLEMENTATION:
        errors.append("LIVE_SOURCE_NOT_RTLTCP")
    if "File_Signal_Source" in impl:
        errors.append("OFFLINE_FILE_SOURCE_FORBIDDEN")

    if cfg.get("SignalSource.address") != EXPECTED_CONTAINER_HOST:
        errors.append("RTLTCP_CONTAINER_HOST_MISMATCH")

    try:
        port = int(cfg.get("SignalSource.port", "0"))
    except ValueError:
        port = 0
    if port != EXPECTED_PORT:
        errors.append("RTLTCP_PORT_MISMATCH")

    try:
        freq = int(cfg.get("SignalSource.freq", "0"))
    except ValueError:
        freq = 0
    if freq != EXPECTED_FREQ_HZ:
        errors.append("GPS_L1_FREQUENCY_MISMATCH")

    try:
        fs = int(cfg.get("SignalSource.sampling_frequency", "0"))
    except ValueError:
        fs = 0
    if fs != EXPECTED_SAMPLE_RATE:
        errors.append("RTLTCP_SAMPLE_RATE_MISMATCH")

    if cfg.get("SignalSource.samples", "") not in {"0", ""}:
        errors.append("LIVE_SOURCE_MUST_NOT_USE_FINITE_OFFLINE_SAMPLE_COUNT")

    return errors


def tcp_ready(host: str = "127.0.0.1", port: int = EXPECTED_PORT, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _docker_image_id(image: str) -> str:
    try:
        result = subprocess.run(
            ["docker", "image", "inspect", "--format", "{{.Id}}", image],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "UNKNOWN"
    except Exception:
        pass
    return "UNKNOWN"


def build_capture_result(
    *,
    config_file: Path,
    receiver_manifest_path: Path,
    receiver_evidence_path: Path,
    stdout_path: Path,
    started_ms: int,
    ended_ms: int,
    docker_image: str,
    docker_image_id: str,
    command: list[str],
    return_code: int | str,
    kernel_endpoint: str,
    config_errors: list[str] | None = None,
) -> dict[str, Any]:
    config_errors = list(config_errors or [])
    receiver_manifest, receiver_identity_verified, identity_errors = _verify_receiver_identity_manifest(
        receiver_manifest_path, receiver_evidence_path
    )

    parsed = parse_gnss_sdr_stdout(stdout_path) if stdout_path.exists() else {}
    capture_observed = _live_capture_observed(parsed, stdout_path)
    source_contract_ok = not config_errors
    promoted = capture_observed and receiver_identity_verified and source_contract_ok

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
        "cn0_dbhz": parsed.get("avg_cn0_dbhz", 0.0),
        "max_cn0_dbhz": parsed.get("max_cn0_dbhz", 0.0),
        "tracked_satellites": parsed.get("tracked_satellites", []),
        "nav_message_satellites": parsed.get("nav_message_satellites", []),
        "tracking_channels": parsed.get("tracking_channels", {}),
        "cn0_by_prn_dbhz": parsed.get("cn0_by_prn_dbhz", {}),
        "first_fix": parsed.get("first_fix"),
        "position_count": parsed.get("position_count", 0),
        "last_velocity_mps": parsed.get("last_velocity_mps", {}),
        "loss_of_lock_count": parsed.get("loss_of_lock_count", 0),
        "run_time_seconds": parsed.get("run_time_seconds", 0.0),
        "freshness_ms": max(0, ended_ms - started_ms),
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

    limitations = list(identity_errors) + config_errors
    if not capture_observed:
        limitations.append("LIVE_CAPTURE_NOT_OBSERVED")
    if promoted:
        limitations.extend(
            [
                "NO_SENSOR_PRIVATE_KEY_ATTESTATION",
                "NO_INERTIAL_CORROBORATION",
                "LIVE_SOURCE_AUTHENTICITY_BOUND_TO_LOCAL_RUNTIME_NOT_CRYPTOGRAPHIC_ATTESTATION",
                "NO_RAW_SAMPLE_CAPTURE_HASH_RTLTCP_RUNTIME_OUTPUT_BOUND_ONLY",
            ]
        )

    proof_level = "REAL_PASSIVE_GNSS" if promoted else "STRUCTURED_STATE"
    runtime_output_hash = sha256_file(stdout_path) if stdout_path.exists() and stdout_path.stat().st_size else "UNKNOWN"

    envelope = {
        "observation_id": f"live-rtltcp-gnss-sdr-{started_ms}",
        "source_type": "LIVE_RTLTCP_GNSS_SDR_CAPTURE",
        "proof_level": proof_level,
        "eligible_for_physical_claim": promoted,
        "sensor_attestation_proven": False,
        "synthetic": False,
        "dataset_name": "local-live-passive-rtltcp",
        "dataset_version": "p2-rtltcp-v0",
        "license": "LOCAL_OPERATOR",
        "official_url": "LOCAL_RUNTIME",
        "capture_timestamp": str(started_ms),
        "processing_timestamp": str(ended_ms),
        "receiver": {
            **receiver_manifest,
            "identity_verified": receiver_identity_verified,
            "identity_evidence_path": str(receiver_evidence_path),
            "identity_evidence_sha256": sha256_file(receiver_evidence_path)
            if receiver_evidence_path.exists()
            else "UNKNOWN",
        },
        "constellation": ["G"] if parsed.get("tracked_satellites") else [],
        "satellites": parsed.get("tracked_satellites", []),
        "observables": observables,
        "truth_reference": {
            "route_hash": runtime_output_hash,
            "labels_used_by_pipeline": False,
        },
        "input_hash": runtime_output_hash if capture_observed else "UNKNOWN",
        "processor_name": "obsidia-live-rtltcp-docker-gnss-sdr",
        "processor_version": "p2-rtltcp-v0",
        "processor_config_hash": sha256_file(config_file) if config_file.exists() else "UNKNOWN",
        "observables_hash": sha256_obj(observables),
        "domain_state_hash": "UNKNOWN",
        "parent_receipt_id": "UNKNOWN",
        "limitations": sorted(set(limitations)),
        "provenance": {
            "source_transport": "rtl_tcp",
            "source_host_from_windows": "127.0.0.1",
            "source_host_from_container": EXPECTED_CONTAINER_HOST,
            "source_port": EXPECTED_PORT,
            "center_frequency_hz": EXPECTED_FREQ_HZ,
            "sampling_frequency_sps": EXPECTED_SAMPLE_RATE,
            "runtime_output_hash_kind": "GNSS_SDR_STDOUT_SHA256",
            "runtime_output_sha256": runtime_output_hash,
            "raw_sample_capture_sha256": "NOT_CAPTURED",
            "docker_image": docker_image,
            "docker_image_id": docker_image_id,
            "command": command,
            "started_ms": started_ms,
            "ended_ms": ended_ms,
            "return_code": return_code,
            "config_path": str(config_file),
            "config_sha256": sha256_file(config_file) if config_file.exists() else "UNKNOWN",
            "receiver_manifest_path": str(receiver_manifest_path),
            "receiver_manifest_sha256": sha256_file(receiver_manifest_path)
            if receiver_manifest_path.exists()
            else "UNKNOWN",
            "receiver_identity_evidence_path": str(receiver_evidence_path),
            "receiver_identity_evidence_sha256": sha256_file(receiver_evidence_path)
            if receiver_evidence_path.exists()
            else "UNKNOWN",
            "parsed_stdout": parsed,
        },
    }

    gate = physical_reality_gate(envelope)
    payload = observation_to_domain_payload(envelope)
    p4_20 = evaluate_path_fidelity(payload).to_dict()
    x108 = GpsX108Gate().evaluate(payload)
    http_probe = (
        _http_post_json(kernel_endpoint, x108.get("ir_payload", payload))
        if promoted
        else {
            "status_http": "NOT_ATTEMPTED",
            "reason": "P2_CAPTURE_NOT_PROMOTED",
            "payload_sha256": sha256_obj(payload),
        }
    )

    return {
        "mode": "LIVE_RTLTCP_DOCKER_GNSS_SDR_CAPTURE",
        "status": "REAL_PASSIVE_GNSS_CAPTURED" if promoted else "BLOCKED_LIVE_CAPTURE_EVIDENCE",
        "p2_capture_promoted": promoted,
        "proof_level": proof_level,
        "eligible_for_physical_claim": promoted,
        "receiver_identity_verified": receiver_identity_verified,
        "live_capture_observed": capture_observed,
        "source_contract_verified": source_contract_ok,
        "runtime_output_hash": runtime_output_hash,
        "raw_sample_capture_hash": "NOT_CAPTURED",
        "physical_gate": asdict(gate),
        "observation_envelope": envelope,
        "domain_payload": payload,
        "p4_20_evidence": p4_20,
        "x108_result": x108,
        "kernel_http_evidence": http_probe,
    }


def run_capture(args: argparse.Namespace) -> dict[str, Any]:
    config_errors = validate_live_config(args.config_file)
    if config_errors:
        return {
            "mode": "LIVE_RTLTCP_DOCKER_GNSS_SDR_CAPTURE",
            "status": "BLOCKED_INVALID_LIVE_SOURCE_CONFIG",
            "p2_capture_promoted": False,
            "proof_level": "STRUCTURED_STATE",
            "eligible_for_physical_claim": False,
            "source_contract_verified": False,
            "limitations": config_errors,
            "decision_authority": "KX108_ONLY",
        }

    if not tcp_ready(args.host, args.port):
        return {
            "mode": "LIVE_RTLTCP_DOCKER_GNSS_SDR_CAPTURE",
            "status": "BLOCKED_RTLTCP_NOT_LISTENING",
            "p2_capture_promoted": False,
            "proof_level": "STRUCTURED_STATE",
            "eligible_for_physical_claim": False,
            "source_contract_verified": True,
            "limitations": ["RTLTCP_NOT_LISTENING", "LIVE_CAPTURE_NOT_OBSERVED"],
            "decision_authority": "KX108_ONLY",
        }

    try:
        docker_version = subprocess.run(
            ["docker", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return {
            "mode": "LIVE_RTLTCP_DOCKER_GNSS_SDR_CAPTURE",
            "status": "BLOCKED_DOCKER_NOT_AVAILABLE",
            "p2_capture_promoted": False,
            "proof_level": "STRUCTURED_STATE",
            "eligible_for_physical_claim": False,
            "limitations": [f"DOCKER_NOT_AVAILABLE:{exc}"],
            "decision_authority": "KX108_ONLY",
        }

    if docker_version.returncode != 0:
        return {
            "mode": "LIVE_RTLTCP_DOCKER_GNSS_SDR_CAPTURE",
            "status": "BLOCKED_DOCKER_NOT_AVAILABLE",
            "p2_capture_promoted": False,
            "proof_level": "STRUCTURED_STATE",
            "eligible_for_physical_claim": False,
            "limitations": ["DOCKER_NOT_AVAILABLE"],
            "decision_authority": "KX108_ONLY",
        }

    args.capture_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = args.capture_dir / "live_rtltcp_gnss_sdr_stdout.log"

    repo_root = ROOT
    config_rel = args.config_file.resolve().relative_to(repo_root.resolve())
    duration = max(1, int(args.duration_seconds))
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo_root}:/work:ro",
        "-v",
        f"{args.capture_dir.resolve()}:/out",
        "-w",
        "/out",
        args.image,
        "sh",
        "-lc",
        f"timeout {duration}s gnss-sdr --config_file=/work/{config_rel.as_posix()} --log_dir=/out",
    ]

    started_ms = int(time.time() * 1000)
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        timeout=duration + 30,
        check=False,
    )
    ended_ms = int(time.time() * 1000)
    stdout_path.write_text(completed.stdout or "", encoding="utf-8")

    return build_capture_result(
        config_file=args.config_file,
        receiver_manifest_path=args.receiver_manifest,
        receiver_evidence_path=args.receiver_evidence,
        stdout_path=stdout_path,
        started_ms=started_ms,
        ended_ms=ended_ms,
        docker_image=args.image,
        docker_image_id=_docker_image_id(args.image),
        command=command,
        return_code=completed.returncode,
        kernel_endpoint=args.kernel_endpoint,
        config_errors=config_errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file",
        type=Path,
        default=ROOT / "hackathons/nativebuilder-gps-defense/gnss_sdr_rtltcp_gps_l1_live.conf",
    )
    parser.add_argument("--receiver-manifest", type=Path, required=True)
    parser.add_argument("--receiver-evidence", type=Path, required=True)
    parser.add_argument(
        "--capture-dir",
        type=Path,
        default=ROOT / ".local/p2-rtltcp/live_capture",
    )
    parser.add_argument("--duration-seconds", type=int, default=90)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=EXPECTED_PORT)
    parser.add_argument("--image", default="carlesfernandez/docker-gnsssdr:latest")
    parser.add_argument("--kernel-endpoint", default="http://127.0.0.1:3001/kernel/ragnarok")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    result = run_capture(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
