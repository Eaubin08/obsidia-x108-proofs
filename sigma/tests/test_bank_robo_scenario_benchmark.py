import json
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER = ROOT / "sigma" / "tools" / "run_bank_robo_scenario_benchmark.py"
SOURCE = ROOT / "docs" / "sources" / "bank-robo" / "scenarios.ts"

def _env():
    e = os.environ.copy()
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONWARNINGS"] = "ignore"
    return e

def run_runner():
    p = subprocess.run(
        [sys.executable, str(RUNNER)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        env=_env(),
    )
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)

def test_source_file_exists():
    assert SOURCE.is_file()

def test_runner_passes():
    s = run_runner()
    assert s["total_cases"] == 23
    assert s["failed_cases"] == 0

def test_business_distribution():
    s = run_runner()
    assert s["business_counts"]["AUTORISER"] == 19
    assert s["business_counts"]["ANALYSER"] == 3
    assert s["business_counts"]["BLOQUER"] == 1

def test_report_shape():
    s = run_runner()
    report = json.loads(Path(s["report_json"]).read_text(encoding="utf-8"))
    assert len(report) == 23

    names = set()
    for row in report:
        assert "scenario_name" in row
        assert "business_expected_decision" in row
        assert "x108_gate_observed" in row
        assert "severity" in row
        assert "reason_code" in row
        assert "gap_status" in row
        names.add(row["scenario_name"])

    assert len(names) == 23