import csv
import json
import requests
import sys
import os
from pathlib import Path
from collections import Counter, defaultdict

# --- CONFIGURATION DES CHEMINS ---
ROOT = Path(__file__).resolve().parent.parent.parent
PACK_PATH = ROOT / "sigma" / "batches" / "bank_enterprise_pack.json"
OUT_DIR = ROOT / "artifacts" / "p2_bank_enterprise"
URL_RAGNAROK = "http://localhost:3001/kernel/ragnarok"

RANK = {"ALLOW": 0, "HOLD": 1, "BLOCK": 2}

def gate_rank(gate: str) -> int:
    return RANK.get(gate, 99)

def run_case(item: dict) -> dict:
    """Envoie un cas de test au Bridge Node.js (Ragnarok)"""
    payload = {
        "domain": "bank",
        "state": item["payload"]
    }
    
    try:
        # APPEL AU BRIDGE (MODE LIVE)
        response = requests.post(URL_RAGNAROK, json=payload, timeout=30)
        data = response.json()
    except Exception as e:
        return {
            "case_id": item["case_id"],
            "family": item["family"],
            "expected_min_gate": item["expected_min_gate"],
            "ok": False,
            "error": f"Bridge Connection Error: {e}",
        }

    # VALIDATION DES RÉSULTATS
    gate_ok = gate_rank(data.get("x108_gate", "BLOCK")) >= gate_rank(item["expected_min_gate"])
    sigma_ok = bool(data.get("sigma_report", {}).get("pass") is True)

    return {
        "case_id": item["case_id"],
        "family": item["family"],
        "expected_min_gate": item["expected_min_gate"],
        "note": item.get("note"),
        "ok": bool(gate_ok and sigma_ok),
        "gate_ok": gate_ok,
        "sigma_ok": sigma_ok,
        "x108_gate": data.get("x108_gate"),
        "severity": data.get("severity"),
        "reason_code": data.get("reason_code"),
        "decision_id": data.get("decision_id"),
        "trace_id": data.get("trace_id"),
        "attestation_ref": data.get("attestation_ref"),
    }

def main():
    if not PACK_PATH.exists():
        print(f"❌ Erreur : Pack introuvable à {PACK_PATH}")
        sys.exit(1)

    pack = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"🚀 Lancement du Stress-Test Enterprise ({len(pack)} cas)...")

    results = [run_case(item) for item in pack]
    failures = [r for r in results if not r["ok"]]

    # STATISTIQUES
    family_counts = Counter(r["family"] for r in results)
    gate_counts = Counter(r.get("x108_gate", "ERROR") for r in results)
    family_gate_counts = defaultdict(Counter)
    for r in results:
        family_gate_counts[r["family"]][r.get("x108_gate", "ERROR")] += 1

    # EXPORT DES RAPPORTS
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

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\n✅ Terminé. {len(failures)} échecs détectés.")
    sys.exit(1 if failures else 0)

if __name__ == "__main__":
    main()