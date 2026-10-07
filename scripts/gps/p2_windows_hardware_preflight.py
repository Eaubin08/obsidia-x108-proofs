#!/usr/bin/env python3
"""Windows P2 hardware preflight for passive GNSS/SDR readiness.

This script inventories local hardware and tooling only. It never promotes
configuration or enumeration into REAL_PASSIVE_GNSS proof.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


HARDWARE_PATTERNS = (
    r"\bgnss\b",
    r"\bgps\b",
    r"\bu[- ]?blox\b",
    r"\brtl[- ]?sdr\b",
    r"\brtlsdr\b",
    r"\brtl2832[a-z0-9]*\b",
    r"\bhackrf\b",
    r"\bairspy\b",
    r"\bbladerf\b",
    r"\blime(?:sdr)?\b",
    r"\busrp\b",
    r"\bettus\b",
    r"\bsdrplay\b",
    r"\badalm[- ]?pluto\b",
    r"\bplutosdr\b",
    r"\bnovatel\b",
    r"\bseptentrio\b",
    r"\btrimble\b",
)


def _run(command: list[str], timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "returncode": completed.returncode,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
        }
    except Exception as exc:
        return {"returncode": "ERROR", "stdout": "", "stderr": str(exc)}


def _powershell_json(script: str) -> list[dict[str, Any]]:
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        return []
    wrapped = (
        "$ErrorActionPreference='SilentlyContinue'; "
        + script
        + " | ConvertTo-Json -Depth 6 -Compress"
    )
    result = _run([ps, "-NoProfile", "-Command", wrapped])
    if result["returncode"] != 0 or not result["stdout"].strip():
        return []
    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    return []


def _normalize_device(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(entry.get("Name") or entry.get("FriendlyName") or ""),
        "device_id": str(entry.get("DeviceID") or entry.get("InstanceId") or ""),
        "pnp_class": str(entry.get("PNPClass") or entry.get("Class") or ""),
        "manufacturer": str(entry.get("Manufacturer") or ""),
        "status": str(entry.get("Status") or ""),
    }


def _looks_like_receiver(device: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(device.get(key, ""))
        for key in ("name", "device_id", "pnp_class", "manufacturer")
    ).lower()
    return any(re.search(pattern, haystack) for pattern in HARDWARE_PATTERNS)


def classify_preflight(snapshot: dict[str, Any]) -> dict[str, Any]:
    explicit = [
        x
        for x in snapshot.get("configured_candidates", [])
        if str(x.get("value", "")).strip()
    ]
    hw = [
        x
        for x in snapshot.get("hardware_candidates", [])
        if _looks_like_receiver(x)
    ]

    if len(hw) == 1:
        status = "ONE_RECEIVER_CANDIDATE_DETECTED"
    elif len(hw) > 1:
        status = "MULTIPLE_RECEIVER_CANDIDATES_DETECTED"
    elif explicit:
        status = "CONFIGURED_CANDIDATE_UNVERIFIED"
    else:
        status = "NO_RECEIVER_CANDIDATE_DETECTED"

    blockers = ["LIVE_CAPTURE_NOT_OBSERVED", "RECEIVER_IDENTITY_NOT_VERIFIED"]
    if not hw and not explicit:
        blockers.insert(0, "NO_HARDWARE_DETECTED")
    if snapshot.get("gnss_sdr_path") in {None, "", "NOT_FOUND"}:
        blockers.append("GNSS_SDR_NATIVE_NOT_FOUND")
    if snapshot.get("docker_path") in {None, "", "NOT_FOUND"}:
        blockers.append("DOCKER_NOT_FOUND")

    return {
        "artifact": "gps_p2_windows_hardware_preflight",
        "status": status,
        "proof_level": "STRUCTURED_STATE",
        "eligible_for_physical_claim": False,
        "p2_capture_promoted": False,
        "live_capture_observed": False,
        "receiver_identity_verified": False,
        "decision_authority": "KX108_ONLY",
        "emits_verdict": False,
        "hardware_candidate_count": len(hw),
        "configured_candidate_count": len(explicit),
        "hardware_candidates": hw,
        "configured_candidates": explicit,
        "tooling": {
            "gnss_sdr_path": snapshot.get("gnss_sdr_path", "NOT_FOUND"),
            "docker_path": snapshot.get("docker_path", "NOT_FOUND"),
            "usbipd_path": snapshot.get("usbipd_path", "NOT_FOUND"),
            "powershell_path": snapshot.get("powershell_path", "NOT_FOUND"),
        },
        "serial_ports": snapshot.get("serial_ports", []),
        "blockers": list(dict.fromkeys(blockers)),
        "next_gate": (
            "Bind exactly one real receiver identity + config, then perform bounded passive live capture."
            if hw or explicit
            else "Connect a passive GNSS/SDR receiver, then rerun this preflight."
        ),
        "claim_boundary": (
            "Hardware enumeration and configuration are readiness evidence only; "
            "REAL_PASSIVE_GNSS requires observed live GNSS output."
        ),
    }


def collect_windows_snapshot() -> dict[str, Any]:
    serial = _powershell_json(
        "Get-CimInstance Win32_SerialPort | "
        "Select-Object Name,DeviceID,PNPDeviceID,Description,ProviderType"
    )

    pnp = _powershell_json(
        "Get-CimInstance Win32_PnPEntity | "
        "Where-Object {$_.Status -eq 'OK'} | "
        "Select-Object Name,DeviceID,PNPClass,Manufacturer,Status"
    )
    normalized = [_normalize_device(x) for x in pnp]
    candidates = [x for x in normalized if _looks_like_receiver(x)]

    configured = []
    for env_name in ("OBSIDIA_GNSS_DEVICE", "OBSIDIA_SDR_DEVICE"):
        value = os.environ.get(env_name, "")
        if value:
            configured.append(
                {"source": env_name, "value": value, "verified": False}
            )

    return {
        "platform": platform.platform(),
        "serial_ports": serial,
        "hardware_candidates": candidates,
        "configured_candidates": configured,
        "gnss_sdr_path": shutil.which("gnss-sdr") or "NOT_FOUND",
        "docker_path": shutil.which("docker") or "NOT_FOUND",
        "usbipd_path": shutil.which("usbipd") or "NOT_FOUND",
        "powershell_path": shutil.which("powershell") or shutil.which("pwsh") or "NOT_FOUND",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    if os.name != "nt":
        result = {
            "artifact": "gps_p2_windows_hardware_preflight",
            "status": "UNSUPPORTED_PLATFORM_FOR_WINDOWS_PREFLIGHT",
            "proof_level": "STRUCTURED_STATE",
            "eligible_for_physical_claim": False,
            "p2_capture_promoted": False,
            "decision_authority": "KX108_ONLY",
            "emits_verdict": False,
            "blockers": ["WINDOWS_REQUIRED_FOR_THIS_PREFLIGHT"],
        }
    else:
        result = classify_preflight(collect_windows_snapshot())

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
