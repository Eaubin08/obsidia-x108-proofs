import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p2_rtltcp_docker_capture.py"
CONFIG_PATH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "gnss_sdr_rtltcp_gps_l1_live.conf"

SPEC = importlib.util.spec_from_file_location("p2_rtltcp_docker_capture", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def _identity(tmp_path: Path):
    evidence = tmp_path / "receiver-evidence.txt"
    evidence.write_text(
        "PnP: RTLSDRBlog V3 R860; interface=USB; serial=test-device-001\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    manifest = tmp_path / "receiver-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "receiver_id": "rtl-sdr-test-001",
                "manufacturer": "RTLSDRBlog",
                "model": "V3 R860",
                "interface": "USB",
                "identity_evidence_sha256": digest,
            }
        ),
        encoding="utf-8",
    )
    return manifest, evidence


def _stdout(tmp_path: Path, with_observation: bool = True):
    path = tmp_path / "live_rtltcp_gnss_sdr_stdout.log"
    if with_observation:
        path.write_text(
            "Tracking of GPS L1 C/A signal started on channel 0 for satellite GPS PRN 3\n"
            "New GPS NAV message received in channel 0: GPS L1 C/A, GPS PRN 3, CN0=39.5 dB-Hz\n"
            "First position fix at 2026-Oct-07 12:00:00.000000 UTC is Lat = 49.000000 [deg], Long = 4.000000 [deg], Height = 150.00 [m], with GDOP = 2.0\n"
            "Position at 2026-Oct-07 12:00:01.000000 UTC using 6 observations is Lat = 49.000010 [deg], Long = 4.000010 [deg], Height = 150.10 [m]\n"
            "Velocity: East: 0.01 [m/s], North: 0.02 [m/s], Up = 0.00 [m/s]\n"
            "Total GNSS-SDR run time: 60.0 [seconds]\n",
            encoding="utf-8",
        )
    else:
        path.write_text("GNSS-SDR started but no satellites were tracked.\n", encoding="utf-8")
    return path


def test_canonical_rtltcp_config_is_live_source_contract():
    assert MODULE.validate_live_config(CONFIG_PATH) == []


def test_file_signal_source_is_refused(tmp_path):
    bad = tmp_path / "bad.conf"
    bad.write_text(
        "[GNSS-SDR]\n"
        "SignalSource.implementation=File_Signal_Source\n"
        "SignalSource.address=host.docker.internal\n"
        "SignalSource.port=1234\n"
        "SignalSource.freq=1575420000\n"
        "SignalSource.sampling_frequency=2000000\n"
        "SignalSource.samples=0\n",
        encoding="utf-8",
    )
    errors = MODULE.validate_live_config(bad)
    assert "LIVE_SOURCE_NOT_RTLTCP" in errors
    assert "OFFLINE_FILE_SOURCE_FORBIDDEN" in errors


def test_observed_rtltcp_runtime_plus_identity_can_promote(tmp_path):
    manifest, evidence = _identity(tmp_path)
    stdout = _stdout(tmp_path, True)

    result = MODULE.build_capture_result(
        config_file=CONFIG_PATH,
        receiver_manifest_path=manifest,
        receiver_evidence_path=evidence,
        stdout_path=stdout,
        started_ms=1000,
        ended_ms=61000,
        docker_image="test-image",
        docker_image_id="sha256:test",
        command=["docker", "run"],
        return_code=124,
        kernel_endpoint="http://127.0.0.1:9/unreachable",
        config_errors=[],
    )

    assert result["p2_capture_promoted"] is True
    assert result["proof_level"] == "REAL_PASSIVE_GNSS"
    assert result["live_capture_observed"] is True
    assert result["receiver_identity_verified"] is True
    assert result["source_contract_verified"] is True
    assert result["runtime_output_hash"] != "UNKNOWN"
    assert result["raw_sample_capture_hash"] == "NOT_CAPTURED"


def test_empty_runtime_output_never_promotes(tmp_path):
    manifest, evidence = _identity(tmp_path)
    stdout = _stdout(tmp_path, False)

    result = MODULE.build_capture_result(
        config_file=CONFIG_PATH,
        receiver_manifest_path=manifest,
        receiver_evidence_path=evidence,
        stdout_path=stdout,
        started_ms=1000,
        ended_ms=61000,
        docker_image="test-image",
        docker_image_id="sha256:test",
        command=["docker", "run"],
        return_code=124,
        kernel_endpoint="http://127.0.0.1:9/unreachable",
        config_errors=[],
    )

    assert result["p2_capture_promoted"] is False
    assert result["proof_level"] == "STRUCTURED_STATE"
    assert result["live_capture_observed"] is False
    assert "LIVE_CAPTURE_NOT_OBSERVED" in result["observation_envelope"]["limitations"]


def test_identity_hash_mismatch_never_promotes(tmp_path):
    manifest, evidence = _identity(tmp_path)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["identity_evidence_sha256"] = "0" * 64
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    stdout = _stdout(tmp_path, True)

    result = MODULE.build_capture_result(
        config_file=CONFIG_PATH,
        receiver_manifest_path=manifest,
        receiver_evidence_path=evidence,
        stdout_path=stdout,
        started_ms=1000,
        ended_ms=61000,
        docker_image="test-image",
        docker_image_id="sha256:test",
        command=["docker", "run"],
        return_code=124,
        kernel_endpoint="http://127.0.0.1:9/unreachable",
        config_errors=[],
    )

    assert result["p2_capture_promoted"] is False
    assert result["receiver_identity_verified"] is False
    assert "RECEIVER_IDENTITY_EVIDENCE_HASH_MISMATCH" in result["observation_envelope"]["limitations"]
