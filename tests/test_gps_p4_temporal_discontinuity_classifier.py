import json
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gps" / "p4_temporal_discontinuity_classifier.py"
SPEC = importlib.util.spec_from_file_location("p4_temporal_discontinuity_classifier", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

calibrate = MODULE.calibrate
detect = MODULE.detect


def _write_log(path: Path, rows):
    lines = []
    for rx_s, utc, lat, lon, h in rows:
        lines.append(f"Current receiver time: {rx_s} s")
        lines.append(
            f"Position at {utc} UTC using 8 observations is "
            f"Lat = {lat:.6f} [deg], Long = {lon:.6f} [deg], Height = {h:.2f} [m]"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_calibration_never_consumes_truth_or_onset(tmp_path):
    baseline = tmp_path / "baseline.log"
    _write_log(
        baseline,
        [
            (10, "2023-Nov-10 14:05:00.000000", 60.18220, 24.82850, 40.0),
            (11, "2023-Nov-10 14:05:01.000000", 60.18221, 24.82851, 40.5),
            (12, "2023-Nov-10 14:05:02.000000", 60.18222, 24.82852, 41.0),
        ],
    )
    result = calibrate(baseline)
    assert result["truth_or_onset_consumed"] is False
    encoded = json.dumps(result).lower()
    assert "official_attack_onset_seconds" not in encoded
    assert "hostile" not in encoded
    assert "attack_label" not in encoded
    assert result["status"] == "DEVELOPMENT_POST_HOC_NOT_BLIND"


def test_large_space_time_discontinuity_is_anomaly(tmp_path):
    baseline = tmp_path / "baseline.log"
    target = tmp_path / "target.log"

    _write_log(
        baseline,
        [
            (10, "2023-Nov-10 14:05:00.000000", 60.18220, 24.82850, 40.0),
            (11, "2023-Nov-10 14:05:01.000000", 60.18221, 24.82851, 40.2),
            (12, "2023-Nov-10 14:05:02.000000", 60.18222, 24.82852, 40.1),
        ],
    )
    calibration = calibrate(baseline)

    _write_log(
        target,
        [
            (130, "2023-Nov-10 14:06:50.000000", 60.18220, 24.82850, 40.0),
            (132, "2023-Nov-10 14:06:52.000000", 60.18222, 24.82852, 40.0),
            (174, "2023-Nov-10 23:55:24.500000", 60.16674, 24.56665, 0.0),
        ],
    )
    result = detect(target, calibration)

    assert result["overall_classification"] == "ANOMALY"
    assert result["truth_or_onset_consumed"] is False
    assert result["first_anomaly"]["violations"]["ecef_step"] is True
    assert result["first_anomaly"]["violations"]["clock_residual"] is True
    assert result["first_anomaly"]["violations"]["receiver_gap"] is True


def test_single_feature_violation_is_unknown(tmp_path):
    baseline = tmp_path / "baseline.log"
    target = tmp_path / "target.log"

    _write_log(
        baseline,
        [
            (10, "2023-Nov-10 14:05:00.000000", 60.18220, 24.82850, 40.0),
            (11, "2023-Nov-10 14:05:01.000000", 60.18221, 24.82851, 40.0),
            (12, "2023-Nov-10 14:05:02.000000", 60.18222, 24.82852, 40.0),
        ],
    )
    calibration = calibrate(baseline)

    _write_log(
        target,
        [
            (20, "2023-Nov-10 14:05:20.000000", 60.18220, 24.82850, 40.0),
            (21, "2023-Nov-10 14:05:21.000000", 60.18221, 24.82851, 40.0),
            (22, "2023-Nov-10 14:05:22.000000", 60.18222, 25.10000, 40.0),
        ],
    )
    result = detect(target, calibration)

    assert result["overall_classification"] == "UNKNOWN"


def test_bounded_calibration_uses_only_selected_initial_window(tmp_path):
    full = tmp_path / "full.log"
    _write_log(
        full,
        [
            (10, "2023-Nov-10 14:05:00.000000", 60.18220, 24.82850, 40.0),
            (20, "2023-Nov-10 14:05:10.000000", 60.18221, 24.82851, 40.1),
            (30, "2023-Nov-10 14:05:20.000000", 60.18222, 24.82852, 40.2),
            (200, "2023-Nov-10 23:55:00.000000", 60.16670, 24.56660, 0.0),
        ],
    )
    result = calibrate(full, max_receiver_second=30)
    assert result["baseline_position_count"] == 3
    assert result["baseline_max_receiver_second"] == 30
