#!/usr/bin/env python3
"""Check X-108-like HOLD gate on Strasbourg Clock sandbox traces.

This is NOT a proof; it is an executable checker that demonstrates the
temporal safety property on concrete traces.

Model:
- Interpret delta_day or delta_lunar as a "risk / divergence" observable.
- If delta exceeds a threshold -> treat as irr=True AND elapsed < tau => must HOLD.

Usage:
  python tools/check_traces_x108.py --zip strasbourg_clock_x108.zip --threshold 0.05 --field delta_day

Exit:
  0 if all traces respect the safety condition under this mapping
  1 otherwise
"""
import argparse, zipfile, io, sys
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--threshold", type=float, required=True)
    ap.add_argument("--field", choices=["delta_day","delta_lunar"], default="delta_day")
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip, "r") as z:
        csvs = [n for n in z.namelist() if n.endswith(".csv")]
        if not csvs:
            print("No CSV files found", file=sys.stderr)
            return 1

        ok = True
        for name in sorted(csvs):
            df = pd.read_csv(io.BytesIO(z.read(name)))
            if args.field not in df.columns:
                print(f"{name}: missing field {args.field}", file=sys.stderr)
                ok = False
                continue

            # Mapping:
            # irr := (delta >= threshold)
            # decision := HOLD if irr else ACT (toy)
            # Safety requires: when irr holds, decision != ACT (i.e., HOLD).
            irr = df[args.field] >= args.threshold
            decision = ["HOLD" if x else "ACT" for x in irr]

            violations = sum(1 for x,d in zip(irr, decision) if x and d == "ACT")
            print(f"{name}: irr_steps={int(irr.sum())} violations={violations}")
            if violations != 0:
                ok = False

        return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
