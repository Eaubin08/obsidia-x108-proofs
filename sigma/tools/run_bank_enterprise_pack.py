import csv
import json
import subprocess
import sys
import os
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
PACK_PATH = ROOT / "sigma" / "batches" / "bank_enterprise_pack.json"
RUN_PIPELINE = ROOT / "sigma" / "run_pipeline.py"
OUT_DIR = ROOT / "artifacts" / "p2_bank_enterprise"

RANK = {"ALLOW": 0, "HOLD": 1, "BLOCK": 2}

def gate_rank(gate: str) -> int:
    return RANK.get(gate, 99)

def _env():
    e = os.environ.copy()
    e["PYTHONUTF8"] = "1"
    e["PYTHONIOENCODING"] = "utf-8"
    e["PYTHONWARNINGS"] = "ignore"
    return e

def run_case(item: dict) -> dict:
    payload = item["payload"]
    p = subprocess.run(
        [sys.executable, str(RUN_PIPELINE), "bank", json.dumps(payload)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=25,
        env=_env(),
    )
    if p.returncode != 0:
        return {
            "case_id": item["case_id"],
            "family": item["family"],
            "expected_min_gate": item["expected_min_gate"],
            "ok": False,
            "error": p.stderr.strip(),
        }

    try:
        data = json.loads(p.stdout)
    except Exception as e:
        return {
            "case_id": item["case_id"],
            "family": item["family"],
            "expected_min_gate": item["expected_min_gate"],
            "ok": False,
            "error": f"JSON parse error: {e}",
        }

    required = ["x108_gate", "decision_id", "trace_id", "attestation_ref", "sigma_report"]
    missing = [k for k in required if k not in data]
    if missing:
        return {
            "case_id": item["case_id"],
            "family": item["family"],
            "expected_min_gate": item["expected_min_gate"],
            "ok": False,
            "error": f"Missing fields: {missing}",
            "raw": data,
        }

    gate_ok = gate_rank(data["x108_gate"]) >= gate_rank(item["expected_min_gate"])
    sigma_ok = bool(data["sigma_report"].get("pass") is True)

    return {
        "case_id": item["case_id"],
        "family": item["family"],
        "expected_min_gate": item["expected_min_gate"],
        "note": item.get("note"),
        "ok": bool(gate_ok and sigma_ok),
        "gate_ok": gate_ok,
        "sigma_ok": sigma_ok,
        "x108_gate": data["x108_gate"],
        "severity": data.get("severity"),
        "reason_code": data.get("reason_code"),
        "decision_id": data.get("decision_id"),
        "trace_id": data.get("trace_id"),
        "attestation_ref": data.get("attestation_ref"),
    }

def main():
    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = [run_case(item) for item in pack]
    failures = [r for r in results if not r["ok"]]

    family_counts = Counter(r["family"] for r in results)
    gate_counts = Counter(r.get("x108_gate", "ERROR") for r in results)
    family_gate_counts = defaultdict(Counter)
    for r in results:
        family_gate_counts[r["family"]][r.get("x108_gate", "ERROR")] += 1

    report_json = OUT_DIR / "bank_enterprise_report.json"
    summary_json = OUT_DIR / "bank_enterprise_summary.json"
    report_csv = OUT_DIR / "bank_enterprise_report.csv"

    report_json.write_text(json.dumps(results, indent=2), encoding="utf-8")

    with report_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case_id", "family", "expected_min_gate", "ok", "gate_ok", "sigma_ok",
                "x108_gate", "severity", "reason_code", "decision_id", "trace_id", "attestation_ref"
            ],
        )
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k) for k in writer.fieldnames})

    summary = {
        "total_cases": len(results),
        "failed_cases": len(failures),
        "families": dict(family_counts),
        "gate_counts": dict(gate_counts),
        "family_gate_counts": {k: dict(v) for k, v in family_gate_counts.items()},
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "report_csv": str(report_csv),
    }
    summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False))
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()
