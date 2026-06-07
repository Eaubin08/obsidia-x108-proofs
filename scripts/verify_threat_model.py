#!/usr/bin/env python3
"""
OBSIDIA — Phase 16A — Threat Model Verifier
============================================
Charge docs/security/threat_manifest_v16.json et vérifie :
  1. Que chaque artifact path existe dans le repo.
  2. (Optionnel) Exécute les tests associés à chaque claim.

Sortie : docs/security/THREAT_MODEL_REPORT_v16.json
"""
import sys
import os
import json
import subprocess
import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "docs" / "security" / "threat_manifest_v16.json"
REPORT_PATH = REPO_ROOT / "docs" / "security" / "THREAT_MODEL_REPORT_v16.json"

# Tests à exécuter automatiquement pour chaque claim (chemin relatif au repo)
RUNNABLE_TESTS = {
    "TM-01": "tools/adversarial/test_seal_tamper.py",
    "TM-02": "tools/adversarial/test_merkle_collision.py",
    "TM-03": "tools/adversarial/test_consensus_split.py",
    "TM-04": "tools/adversarial/test_signature_tamper.py",
    "TM-06": "tools/adversarial/test_monotonic_break.py",
    "TM-07": "tools/adversarial/test_threshold_fuzz.py",
}

def check_artifacts(claim: dict, repo_root: Path) -> list:
    """Vérifie que tous les artifacts d'un claim existent."""
    missing = []
    for artifact in claim.get("artifacts", []):
        path = repo_root / artifact
        if not path.exists():
            missing.append(artifact)
    return missing

def run_test(script: str, repo_root: Path) -> tuple:
    """Exécute un script de test et retourne (exit_code, output)."""
    script_path = repo_root / script
    if not script_path.exists():
        return -1, f"Script not found: {script}"
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True, cwd=repo_root, timeout=120
    )
    return result.returncode, (result.stdout + result.stderr).strip()[-500:]

def main():
    print(f"[16A] Threat Model Verifier")
    print(f"  Manifest : {MANIFEST_PATH}")
    print(f"  Repo root: {REPO_ROOT}")
    print()

    if not MANIFEST_PATH.exists():
        print(f"FAIL — Manifest not found: {MANIFEST_PATH}")
        sys.exit(1)

    manifest = json.loads(MANIFEST_PATH.read_text())
    claims = manifest.get("claims", [])
    print(f"  Claims to verify: {len(claims)}")
    print()

    results = []
    global_pass = True

    for claim in claims:
        cid = claim["id"]
        claim_text = claim["claim"]
        print(f"  [{cid}] {claim_text[:70]}...")

        result = {
            "id": cid,
            "claim": claim_text,
            "status": "UNKNOWN",
            "artifact_check": "PASS",
            "test_run": "SKIPPED",
            "missing_artifacts": [],
            "test_output": None,
        }

        # 1. Vérification des artifacts
        missing = check_artifacts(claim, REPO_ROOT)
        if missing:
            result["artifact_check"] = "FAIL"
            result["missing_artifacts"] = missing
            result["status"] = "FAIL"
            global_pass = False
            print(f"    ARTIFACT FAIL — missing: {missing}")
        else:
            result["artifact_check"] = "PASS"
            print(f"    Artifacts: OK ({len(claim.get('artifacts', []))} files)")

        # 2. Exécution du test si disponible
        if cid in RUNNABLE_TESTS:
            script = RUNNABLE_TESTS[cid]
            print(f"    Running test: {script} ...", end=" ", flush=True)
            try:
                code, output = run_test(script, REPO_ROOT)
                if code == 0:
                    result["test_run"] = "PASS"
                    print("PASS")
                else:
                    result["test_run"] = "FAIL"
                    result["status"] = "FAIL"
                    global_pass = False
                    print("FAIL")
                result["test_output"] = output[-200:] if output else None
            except subprocess.TimeoutExpired:
                result["test_run"] = "TIMEOUT"
                result["status"] = "FAIL"
                global_pass = False
                print("TIMEOUT")
        else:
            result["test_run"] = "SKIPPED"

        # Statut final du claim
        if result["artifact_check"] == "PASS" and result["test_run"] in ("PASS", "SKIPPED"):
            result["status"] = "PASS"
        elif result["status"] == "UNKNOWN":
            result["status"] = "FAIL"

        results.append(result)
        print()

    # Résumé
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  Claims verified: {len(results)}")
    print(f"  PASS: {passed}  FAIL: {failed}")

    # Rapport JSON
    report = {
        "version": manifest.get("version", "v16"),
        "phase": "16A",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "tag": manifest.get("tag"),
        "commit": manifest.get("commit"),
        "global_seal_hash": manifest.get("global_seal_hash"),
        "total_claims": len(results),
        "passed": passed,
        "failed": failed,
        "global_status": "PASS" if global_pass else "FAIL",
        "claims": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\n  Report written: {REPORT_PATH}")

    if global_pass:
        print(f"\nPASS — All {passed} claims verified")
        sys.exit(0)
    else:
        print(f"\nFAIL — {failed} claim(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
