import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "hackathons" / "nativebuilder-gps-defense" / "physical_signal_periphery.py"
SAMPLE = ROOT / "hackathons" / "nativebuilder-gps-defense" / "samples" / "synthetic_observation.json"
BENCH = ROOT / "hackathons" / "nativebuilder-gps-defense" / "samples" / "blind_manifest.json"
REAL_RINEX = ROOT / "hackathons" / "nativebuilder-gps-defense" / "data" / "rinex" / "noaa_ab02_2026_210" / "ab022100.26o.gz"
REAL_STATION_LOG = ROOT / "hackathons" / "nativebuilder-gps-defense" / "data" / "rinex" / "noaa_ab02_2026_210" / "ab02.log.txt"
REAL_RF_RUN = ROOT / "hackathons" / "nativebuilder-gps-defense" / "runs" / "iq_cttc_2013_04_04"


def load_module():
    spec = importlib.util.spec_from_file_location("physical_signal_periphery", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_synthetic_observation_is_not_eligible_for_physical_claim():
    mod = load_module()
    envelope = mod.load_observation(SAMPLE)
    gate = mod.physical_reality_gate(envelope)

    assert envelope["proof_level"] == "SYNTHETIC_TEST_ONLY"
    assert envelope["eligible_for_physical_claim"] is False
    assert gate.emits_verdict is False
    assert "SYNTHETIC_TEST_ONLY_NOT_PHYSICAL" in gate.reason_codes


def test_physical_observation_can_reach_p3_05_but_remains_claim_bounded():
    mod = load_module()
    result = mod.run_observation(SAMPLE)

    assert result["physical_gate"]["decision_authority"] == "KX108_ONLY"
    assert result["physical_gate"]["emits_verdict"] is False
    assert result["x108_result"]["domain"] == "gps_defense_aviation"
    assert result["x108_result"]["receipt"]["os3_ticket"]["replay_status"] == "NOT_RUN"


def test_live_passive_without_hardware_is_blocked_not_mocked():
    mod = load_module()
    result = mod.run_live_passive()

    assert result["mode"] == "LIVE_PASSIVE_ADAPTER"
    if result["blocked"]:
        assert result["status"] == "NO_HARDWARE_DETECTED"
        assert result["envelope"]["eligible_for_physical_claim"] is False
        assert "NO_HARDWARE_DETECTED" in result["physical_gate"]["reason_codes"]


def test_blind_benchmark_keeps_truth_out_of_pipeline():
    mod = load_module()
    result = mod.run_blind_benchmark(BENCH)

    assert result["mode"] == "BLIND_BENCHMARK"
    assert result["truth_manifest_used_by_pipeline"] is False
    assert result["case_count"] == 1


def test_real_rinex_parser_extracts_noaa_ab02_observations_when_present():
    if not REAL_RINEX.exists():
        return
    mod = load_module()
    parsed = mod.parse_rinex_observation_file(REAL_RINEX, REAL_STATION_LOG)

    assert parsed["header"]["marker_name"] == "AB02"
    assert parsed["epoch_count"] > 0
    assert "G" in parsed["observed_constellations"]
    assert len(parsed["unique_satellites"]) > 0


def test_real_gnss_sdr_stdout_parser_extracts_rf_observables_when_present():
    stdout = REAL_RF_RUN / "gnss_sdr_run_stdout_modern.log"
    if not stdout.exists():
        return
    mod = load_module()
    parsed = mod.parse_gnss_sdr_stdout(stdout)

    assert parsed["run_time_seconds"] > 0
    assert parsed["position_count"] > 0
    assert len(parsed["tracked_satellites"]) >= 5
    assert parsed["avg_cn0_dbhz"] > 0


def test_live_receiver_env_configuration_is_not_promoted_to_real_passive_claim(monkeypatch):
    mod = load_module()
    monkeypatch.setenv("OBSIDIA_GNSS_DEVICE", "serial://COM9")
    detection = mod.detect_live_passive_receiver()

    assert detection["receiver_candidate_detected"] is True
    assert detection["status"] == "RECEIVER_CANDIDATE_CONFIGURED_UNVERIFIED"
    assert detection["proof_level"] == "STRUCTURED_STATE"
    assert detection["eligible_for_physical_claim"] is False
    assert detection["live_capture_observed"] is False
    assert detection["receiver_identity_verified"] is False
    assert detection["sensor_attestation_proven"] is False
    assert "LIVE_CAPTURE_NOT_OBSERVED" in detection["limitations"]


def test_live_passive_with_configured_candidate_still_blocks_until_capture(monkeypatch):
    mod = load_module()
    monkeypatch.setenv("OBSIDIA_SDR_DEVICE", "rtl-sdr://0")
    result = mod.run_live_passive()

    assert result["status"] == "RECEIVER_CANDIDATE_CONFIGURED_UNVERIFIED"
    assert result["blocked"] is True
    assert result["envelope"]["proof_level"] == "STRUCTURED_STATE"
    assert result["envelope"]["eligible_for_physical_claim"] is False
    assert "Configuration alone is not proof" in result["next_human_action"]


def test_physical_claim_eligibility_does_not_imply_sensor_attestation():
    mod = load_module()
    envelope = {
        "observation_id": "recorded-real-no-attestation",
        "source_type": "RINEX_OBSERVATION_FILE",
        "proof_level": "RECORDED_REAL_GNSS",
        "eligible_for_physical_claim": True,
        "capture_timestamp": "2026-10-07T00:00:00Z",
        "processing_timestamp": "2026-10-07T00:00:01Z",
        "input_hash": "abc",
        "processor_name": "test",
        "processor_config_hash": "cfg",
        "observables_hash": mod.sha256_obj({"freshness_ms": 0}),
        "observables": {"freshness_ms": 0},
        "limitations": ["NO_SENSOR_PRIVATE_KEY_ATTESTATION"],
    }
    payload = mod.observation_to_domain_payload(envelope)

    assert payload["sensor_attested"] is False
    assert payload["attestation_ready"] is False


def test_explicit_sensor_attestation_can_be_carried_without_changing_authority():
    mod = load_module()
    envelope = {
        "observation_id": "live-attested",
        "source_type": "LIVE_PASSIVE_RECEIVER",
        "proof_level": "REAL_PASSIVE_GNSS",
        "eligible_for_physical_claim": True,
        "sensor_attestation_proven": True,
        "capture_timestamp": "2026-10-07T00:00:00Z",
        "processing_timestamp": "2026-10-07T00:00:01Z",
        "input_hash": "abc",
        "processor_name": "test",
        "processor_config_hash": "cfg",
        "observables_hash": mod.sha256_obj({"freshness_ms": 0}),
        "observables": {"freshness_ms": 0},
        "limitations": [],
    }
    payload = mod.observation_to_domain_payload(envelope)

    assert payload["sensor_attested"] is True
    assert payload["attestation_ready"] is True



def _live_stdout_fixture():
    return "\n".join([
        "Tracking of GPS L1 C/A signal started on channel 0 for satellite GPS PRN 3",
        "New GPS NAV message received for GPS PRN 3 CN0=40.0 dB-Hz",
        "First position fix at 2026-10-07 10:00:00 UTC is Lat = 48.0 [deg], Long = 4.0 [deg], Height = 100.0 [m], with GDOP = 1.2",
        "Position at 2026-10-07 10:00:01 UTC using 5 observations is Lat = 48.1 [deg], Long = 4.1 [deg], Height = 101.0 [m]",
        "Velocity: East: 1.0 [m/s], North: 2.0 [m/s], Up = 0.0 [m/s]",
        "Total GNSS-SDR run time: 2.0 [seconds]",
    ])


def _write_receiver_identity_files(mod, tmp_path):
    evidence = tmp_path / "receiver-evidence.txt"
    evidence.write_text("USB\\VID_0BDA&PID_2838 RTL-SDR receiver 00000001", encoding="utf-8")
    manifest = tmp_path / "receiver-manifest.json"
    manifest.write_text(
        __import__("json").dumps({
            "receiver_id": "rtl-sdr-00000001",
            "manufacturer": "test-manufacturer",
            "model": "test-model",
            "interface": "USB",
            "identity_evidence_sha256": mod.sha256_file(evidence),
        }),
        encoding="utf-8",
    )
    return manifest, evidence


def test_p2_live_capture_promotes_only_runtime_observed_bound_receiver(monkeypatch, tmp_path):
    mod = load_module()
    fake_bin = tmp_path / "gnss-sdr"
    fake_bin.write_text("binary-placeholder", encoding="utf-8")
    config = tmp_path / "live.conf"
    config.write_text("SignalSource.implementation=TestSource", encoding="utf-8")
    manifest, evidence = _write_receiver_identity_files(mod, tmp_path)

    monkeypatch.setattr(mod.shutil, "which", lambda name: str(fake_bin) if name == "gnss-sdr" else None)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *args, **kwargs: mod.subprocess.CompletedProcess(args=args[0], returncode=0, stdout=_live_stdout_fixture()),
    )
    monkeypatch.setattr(
        mod,
        "_http_post_json",
        lambda url, payload: {"status_http": "TEST_NOT_SENT", "payload_sha256": mod.sha256_obj(payload)},
    )

    result = mod.run_live_gnss_sdr_capture(
        config,
        manifest,
        evidence,
        tmp_path / "capture",
        5,
        "http://127.0.0.1:3001/kernel/ragnarok",
    )

    assert result["p2_capture_promoted"] is True
    assert result["proof_level"] == "REAL_PASSIVE_GNSS"
    assert result["eligible_for_physical_claim"] is True
    assert result["live_capture_observed"] is True
    assert result["receiver_identity_verified"] is True
    assert result["observation_envelope"]["input_hash"] != "UNKNOWN"
    assert result["observation_envelope"]["sensor_attestation_proven"] is False
    assert result["physical_gate"]["decision_authority"] == "KX108_ONLY"


def test_p2_live_capture_identity_hash_mismatch_blocks_promotion(monkeypatch, tmp_path):
    mod = load_module()
    fake_bin = tmp_path / "gnss-sdr"
    fake_bin.write_text("binary-placeholder", encoding="utf-8")
    config = tmp_path / "live.conf"
    config.write_text("SignalSource.implementation=TestSource", encoding="utf-8")
    manifest, evidence = _write_receiver_identity_files(mod, tmp_path)
    evidence.write_text("different receiver evidence", encoding="utf-8")

    monkeypatch.setattr(mod.shutil, "which", lambda name: str(fake_bin) if name == "gnss-sdr" else None)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *args, **kwargs: mod.subprocess.CompletedProcess(args=args[0], returncode=0, stdout=_live_stdout_fixture()),
    )

    result = mod.run_live_gnss_sdr_capture(
        config,
        manifest,
        evidence,
        tmp_path / "capture",
        5,
        "http://127.0.0.1:3001/kernel/ragnarok",
    )

    assert result["p2_capture_promoted"] is False
    assert result["proof_level"] == "STRUCTURED_STATE"
    assert result["eligible_for_physical_claim"] is False
    assert result["receiver_identity_verified"] is False
    assert "RECEIVER_IDENTITY_EVIDENCE_HASH_MISMATCH" in result["observation_envelope"]["limitations"]
    assert result["kernel_http_evidence"]["status_http"] == "NOT_ATTEMPTED"


def test_p2_live_capture_empty_runtime_output_blocks_promotion(monkeypatch, tmp_path):
    mod = load_module()
    fake_bin = tmp_path / "gnss-sdr"
    fake_bin.write_text("binary-placeholder", encoding="utf-8")
    config = tmp_path / "live.conf"
    config.write_text("SignalSource.implementation=TestSource", encoding="utf-8")
    manifest, evidence = _write_receiver_identity_files(mod, tmp_path)

    monkeypatch.setattr(mod.shutil, "which", lambda name: str(fake_bin) if name == "gnss-sdr" else None)
    monkeypatch.setattr(
        mod.subprocess,
        "run",
        lambda *args, **kwargs: mod.subprocess.CompletedProcess(args=args[0], returncode=0, stdout=""),
    )

    result = mod.run_live_gnss_sdr_capture(
        config,
        manifest,
        evidence,
        tmp_path / "capture",
        5,
        "http://127.0.0.1:3001/kernel/ragnarok",
    )

    assert result["p2_capture_promoted"] is False
    assert result["live_capture_observed"] is False
    assert result["proof_level"] == "STRUCTURED_STATE"
    assert "LIVE_CAPTURE_NOT_OBSERVED" in result["observation_envelope"]["limitations"]
