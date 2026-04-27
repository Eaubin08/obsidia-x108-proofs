import json
import subprocess
import sys
import os
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent.parent
PACK_PATH = ROOT / "sigma" / "batches" / "bank_enterprise_pack.json"
RUNNER = ROOT / "sigma" / "tools" / "run_bank_enterprise_pack.py"

def _env():
    e = os.environ.copy()
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONWARNINGS"] = "ignore"
    return e

def test_pack_has_60_cases():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    assert len(pack) == 60

def test_pack_has_balanced_families():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    c = Counter(item["family"] for item in pack)
    assert c == Counter({"normal": 20, "suspicious": 20, "blocked": 20})

def test_pack_case_ids_unique():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    ids = [item["case_id"] for item in pack]
    assert len(ids) == len(set(ids))

def test_enterprise_runner_passes():
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
    summary = json.loads(p.stdout)

    assert summary["total_cases"] == 60
    assert summary["failed_cases"] == 0
    assert summary["families"] == {"normal": 20, "suspicious": 20, "blocked": 20}

    assert Path(summary["report_json"]).is_file()
    assert Path(summary["summary_json"]).is_file()
    assert Path(summary["report_csv"]).is_file()

    family_gate_counts = summary["family_gate_counts"]

    assert family_gate_counts["blocked"].get("BLOCK", 0) == 20
    assert family_gate_counts["suspicious"].get("ALLOW", 0) == 0
    assert family_gate_counts["normal"].get("ALLOW", 0) >= 16
