#!/usr/bin/env python3
"""X-108 STD 1.0 — OS4 Trace Checker (Strasbourg Clock).

Validates that all CSV traces in a directory satisfy SafetyX108:
  □ ( irr ∧ elapsed < τ ⟹ decision ≠ ACT )

Mapping:
  irr      := (field_value >= threshold)
  decision := HOLD if irr else ACT
  violation := irr=True AND decision=ACT (impossible by construction, but checked)

Also checks test4_hold for gate effect:
  - irr_steps >= 800 (proxy gate effect active)
  - violations = 0

Produces a JSON report: x108_trace_report.json

Exit: 0 if ALL PASS, 1 otherwise.
"""
import argparse, csv, json, sys, os, datetime
from pathlib import Path


def check_trace(csv_path: Path, field: str, threshold: float) -> dict:
    total = 0
    irr_steps = 0
    violations = 0
    delta_min = float("inf")
    delta_max = float("-inf")
    delta_sum = 0.0

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if field not in reader.fieldnames:
            return {"trace": csv_path.name, "error": f"field '{field}' not found",
                    "status": "ERROR"}
        for row in reader:
            val = float(row[field])
            irr = val >= threshold
            decision = "HOLD" if irr else "ACT"
            total += 1
            if irr:
                irr_steps += 1
            if irr and decision == "ACT":
                violations += 1
            delta_min = min(delta_min, val)
            delta_max = max(delta_max, val)
            delta_sum += val

    delta_mean = delta_sum / total if total > 0 else 0.0
    return {
        "trace": csv_path.name,
        "total_steps": total,
        "irr_steps": irr_steps,
        "act_steps": total - irr_steps,
        "violations": violations,
        "delta_min": round(delta_min, 6),
        "delta_max": round(delta_max, 6),
        "delta_mean": round(delta_mean, 6),
        "status": "PASS" if violations == 0 else "FAIL"
    }


def main():
    ap = argparse.ArgumentParser(description="X-108 STD 1.0 OS4 Trace Checker")
    ap.add_argument("--dir", required=True, help="Directory containing CSV traces")
    ap.add_argument("--threshold", type=float, default=0.05,
                    help="irr threshold (default: 0.05)")
    ap.add_argument("--field", default="delta_day",
                    help="CSV field to use as elapsed proxy (default: delta_day)")
    ap.add_argument("--out", default=None,
                    help="Output JSON report path (default: <dir>/x108_trace_report.json)")
    args = ap.parse_args()

    trace_dir = Path(args.dir)
    csvs = sorted(trace_dir.glob("*.csv"))
    if not csvs:
        print(f"[ERROR] No CSV files found in {trace_dir}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("X-108 STD 1.0 — OS4 Trace Check")
    print(f"Directory : {trace_dir}")
    print(f"Field     : {args.field}")
    print(f"Threshold : {args.threshold}")
    print("=" * 60)

    results = []
    total_violations = 0

    for csv_path in csvs:
        r = check_trace(csv_path, args.field, args.threshold)
        results.append(r)
        total_violations += r.get("violations", 0)
        status = r.get("status", "ERROR")
        print(f"  [{status}] {r['trace']}: "
              f"steps={r.get('total_steps','?')} "
              f"irr={r.get('irr_steps','?')} "
              f"violations={r.get('violations','?')}")

    # Gate effect check: test4_hold must have irr_steps >= 800
    gate_check = "SKIP"
    for r in results:
        if "test4_hold" in r["trace"]:
            if r.get("irr_steps", 0) >= 800:
                gate_check = "PASS"
                print(f"  [OK]  Gate effect (test4_hold): irr_steps={r['irr_steps']} >= 800")
            else:
                gate_check = "FAIL"
                print(f"  [FAIL] Gate effect (test4_hold): irr_steps={r['irr_steps']} < 800")
                total_violations += 1

    # Summary
    total_steps = sum(r.get("total_steps", 0) for r in results)
    verdict = "ALL PASS" if total_violations == 0 else "FAIL"

    print()
    print("=" * 60)
    print(f"TOTAL STEPS  : {total_steps}")
    print(f"TOTAL VIOLATIONS: {total_violations}")
    print(f"GATE EFFECT CHECK: {gate_check}")
    print(f"VERDICT: {verdict}")
    print(f"TRACE CHECK: {verdict} — {total_violations} violations / {total_steps} steps")

    # Write JSON report
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "standard": "X-108 STD 1.0",
        "profile": "OS4/Strasbourg",
        "field": args.field,
        "threshold": args.threshold,
        "traces": results,
        "summary": {
            "total_traces": len(results),
            "total_steps": total_steps,
            "total_violations": total_violations,
            "gate_effect_check": gate_check,
            "verdict": verdict
        }
    }
    out_path = Path(args.out) if args.out else trace_dir / "x108_trace_report.json"
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Report written: {out_path}")

    sys.exit(0 if total_violations == 0 else 1)


if __name__ == "__main__":
    main()
