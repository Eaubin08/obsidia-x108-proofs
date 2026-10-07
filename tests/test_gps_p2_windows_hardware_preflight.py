import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p2_windows_hardware_preflight.py"

SPEC = importlib.util.spec_from_file_location("p2_windows_hardware_preflight", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

classify_preflight = MODULE.classify_preflight


def _base():
    return {
        "serial_ports": [],
        "hardware_candidates": [],
        "configured_candidates": [],
        "gnss_sdr_path": "NOT_FOUND",
        "docker_path": r"C:\Program Files\Docker\docker.exe",
        "usbipd_path": "NOT_FOUND",
        "powershell_path": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
    }


def test_no_hardware_stays_structured_state_and_blocked():
    result = classify_preflight(_base())

    assert result["status"] == "NO_RECEIVER_CANDIDATE_DETECTED"
    assert result["proof_level"] == "STRUCTURED_STATE"
    assert result["eligible_for_physical_claim"] is False
    assert result["p2_capture_promoted"] is False
    assert result["live_capture_observed"] is False
    assert "NO_HARDWARE_DETECTED" in result["blockers"]


def test_one_ublox_device_is_candidate_but_not_physical_proof():
    snapshot = _base()
    snapshot["hardware_candidates"] = [
        {
            "name": "u-blox GNSS Receiver",
            "device_id": r"USB\VID_1546&PID_01A8",
            "pnp_class": "Ports",
            "manufacturer": "u-blox",
            "status": "OK",
        }
    ]

    result = classify_preflight(snapshot)

    assert result["status"] == "ONE_RECEIVER_CANDIDATE_DETECTED"
    assert result["hardware_candidate_count"] == 1
    assert result["p2_capture_promoted"] is False
    assert result["receiver_identity_verified"] is False
    assert "NO_HARDWARE_DETECTED" not in result["blockers"]


def test_multiple_sdr_candidates_are_ambiguous_readiness_not_proof():
    snapshot = _base()
    snapshot["hardware_candidates"] = [
        {
            "name": "RTL2832U SDR",
            "device_id": "USB:RTL2832",
            "pnp_class": "USB",
            "manufacturer": "Realtek",
            "status": "OK",
        },
        {
            "name": "HackRF One",
            "device_id": "USB:HACKRF",
            "pnp_class": "USB",
            "manufacturer": "Great Scott Gadgets",
            "status": "OK",
        },
    ]

    result = classify_preflight(snapshot)

    assert result["status"] == "MULTIPLE_RECEIVER_CANDIDATES_DETECTED"
    assert result["hardware_candidate_count"] == 2
    assert result["eligible_for_physical_claim"] is False


def test_configured_env_without_detected_hardware_is_unverified_only():
    snapshot = _base()
    snapshot["configured_candidates"] = [
        {"source": "OBSIDIA_GNSS_DEVICE", "value": "serial://COM9", "verified": False}
    ]

    result = classify_preflight(snapshot)

    assert result["status"] == "CONFIGURED_CANDIDATE_UNVERIFIED"
    assert result["configured_candidate_count"] == 1
    assert result["p2_capture_promoted"] is False
    assert "NO_HARDWARE_DETECTED" not in result["blockers"]


def test_generic_serial_port_does_not_self_promote_to_gnss_candidate():
    snapshot = _base()
    snapshot["serial_ports"] = [
        {
            "Name": "USB Serial Port (COM4)",
            "DeviceID": "COM4",
            "PNPDeviceID": "FTDIBUS\\VID_0403+PID_6001",
            "Description": "USB Serial Port",
            "ProviderType": "RS232",
        }
    ]

    result = classify_preflight(snapshot)

    assert result["hardware_candidate_count"] == 0
    assert result["status"] == "NO_RECEIVER_CANDIDATE_DETECTED"
    assert result["serial_ports"]
    assert result["p2_capture_promoted"] is False
