import json
import subprocess
import sys
import os
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent
PACK_PATH = ROOT / "sigma" / "batches" / "bank_truth_proxy_pack.json"
RUNNER = ROOT / "sigma" / "tools" / "run_bank_truth_proxy_pack.py"

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
        timeout=240,
        env=_env(),
    )
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)

def test_pack_has_100_cases():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    assert len(pack) == 100

def test_pack_has_expected_family_distribution():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    c = Counter(item["family"] for item in pack)
    assert c == Counter({"normal": 40, "review": 30, "blocked": 30})

def test_pack_case_ids_unique():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    ids = [item["case_id"] for item in pack]
    assert len(ids) == len(set(ids))

def test_runner_passes_and_writes_artifacts():
    s = run_runner()
    assert s["total_cases"] == 100
    assert s["failed_cases"] == 0
    assert Path(s["report_json"]).is_file()
    assert Path(s["summary_json"]).is_file()
    assert Path(s["report_csv"]).is_file()

def test_no_false_negative_and_no_softer_gap():
    s = run_runner()
    cm = s["confusion_matrix"]
    assert (cm["TP"] + cm["TN"] + cm["FP"] + cm["FN"]) == 100
    assert cm["FN"] == 0
    assert s["gap_counts"].get("SOFTER_THAN_BUSINESS", 0) == 0
