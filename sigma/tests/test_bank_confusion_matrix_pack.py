import json
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER = ROOT / "sigma" / "tools" / "run_bank_confusion_matrix_pack.py"

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
        timeout=600,
        env=_env(),
    )
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)

def test_runner_passes_and_writes_artifacts():
    s = run_runner()
    assert s["failed_cases"] == 0
    assert Path(s["report_json"]).is_file()
    assert Path(s["summary_json"]).is_file()
    assert Path(s["report_csv"]).is_file()

def test_total_case_count_is_expected():
    s = run_runner()
    assert s["total_cases"] == 177
    assert s["corpus_counts"] == {
        "truth_proxy": 100,
        "regulatory_proxy": 54,
        "bank_robo_benchmark": 23,
    }

def test_confusion_matrix_is_coherent():
    s = run_runner()
    cm = s["confusion_matrix_global"]
    assert (cm["TP"] + cm["TN"] + cm["FP"] + cm["FN"]) == s["total_cases"]

def test_no_softer_cases():
    s = run_runner()
    assert s["softer_cases"] == 0
    assert s["gap_counts"].get("SOFTER_THAN_BUSINESS", 0) == 0

def test_harder_cases_are_present():
    s = run_runner()
    assert s["harder_cases"] >= 6

def test_by_corpus_contains_three_views():
    s = run_runner()
    by = s["confusion_matrix_by_corpus"]
    assert set(by.keys()) == {"truth_proxy", "regulatory_proxy", "bank_robo_benchmark"}
