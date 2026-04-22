#!/usr/bin/env python3
"""
OBSIDIA PUBLIC PROOFKIT — verify_all.py
Runs:
- V18.3.1 seal_verify.py + root_hash_verify.py
- V18.7 checker (200k) and validates invariants
- V18.8 checker and validates G1..G4

Outputs:
- PROOFKIT_REPORT.json
Exit code:
- 0 PASS
- 1 FAIL

Usage:
  python3 proofs/verify_all.py
"""
import os, sys, json, subprocess, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd, timeout=600):
    try:
        out = subprocess.check_output(
            cmd, cwd=cwd, stderr=subprocess.STDOUT, text=True, timeout=timeout
        )
        return True, out
    except subprocess.CalledProcessError as e:
        return False, e.output
    except Exception as e:
        return False, str(e)


def main():
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    report = {"timestamp": ts, "checks": {}, "overall": "FAIL"}

    # ── V18.3.1 — Root Seal ──────────────────────────────────────────────────
    # Real path in this repo: proofs/V18_3_1/
    v183 = os.path.join(ROOT, "V18_3_1")
    ok1, out1 = run([sys.executable, "seal_verify.py"], cwd=v183)
    ok2, out2 = run([sys.executable, "root_hash_verify.py"], cwd=v183)
    report["checks"]["V18_3_1_seal_verify"] = {"pass": ok1, "stdout": out1[-2000:]}
    report["checks"]["V18_3_1_root_hash_verify"] = {"pass": ok2, "stdout": out2[-2000:]}

    # ── V18.7 — Non-circumvention (200k fuzz) ────────────────────────────────
    # Real path in this repo: proofs/V18_7/
    v187 = os.path.join(ROOT, "V18_7")
    os.makedirs(os.path.join(v187, "results"), exist_ok=True)
    res_path = os.path.join(v187, "results", "results_v18_7.json")
    ok3, out3 = run(
        [sys.executable, os.path.join("checker", "noncircumvention_checker.py"),
         "--N", "200000", "--out", res_path],
        cwd=v187,
    )
    report["checks"]["V18_7_checker_run"] = {"pass": ok3, "stdout": out3[-2000:]}
    v187_ok = False
    if ok3 and os.path.exists(res_path):
        data = json.load(open(res_path, "r", encoding="utf-8"))
        v187_ok = (
            data.get("fuzz", {})
                .get("violations", {})
                .get("E2_no_allow_before_tau", 1) == 0
        )
    report["checks"]["V18_7_invariants"] = {"pass": v187_ok}

    # ── V18.8 — Convergence & Stability ──────────────────────────────────────
    # Real path in this repo: proofs/V18_8/
    v188 = os.path.join(ROOT, "V18_8")
    os.makedirs(os.path.join(v188, "results"), exist_ok=True)
    res_path2 = os.path.join(v188, "results", "results_v18_8.json")
    ok4, out4 = run(
        [sys.executable, os.path.join("checker", "convergence_checker.py"),
         "--out", res_path2],
        cwd=v188,
    )
    report["checks"]["V18_8_checker_run"] = {"pass": ok4, "stdout": out4[-2000:]}
    v188_ok = False
    if ok4 and os.path.exists(res_path2):
        d = json.load(open(res_path2, "r", encoding="utf-8"))
        v188_ok = all([
            d.get("G1_determinism"),
            d.get("G2_no_allow_before_tau"),
            d.get("G3_convergence_at_tau"),
            d.get("G4_no_oscillation_without_boundary"),
        ])
    report["checks"]["V18_8_invariants"] = {"pass": v188_ok}

    overall = ok1 and ok2 and ok3 and v187_ok and ok4 and v188_ok
    report["overall"] = "PASS" if overall else "FAIL"
    open(os.path.join(ROOT, "PROOFKIT_REPORT.json"), "w", encoding="utf-8").write(
        json.dumps(report, indent=2)
    )
    print(report["overall"])
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()
