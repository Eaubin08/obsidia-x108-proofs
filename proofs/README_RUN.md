# OBSIDIA_PUBLIC_PROOFKIT_v1

This is a minimal public verification kit (no marketing, only proofs).

## Run
```bash
python verify_all.py
```
Expected:
- prints `PASS`
- writes `PROOFKIT_REPORT.json`

## Included proofs
- V18.3.1 ROOT SEAL: integrity + root hash
- V18.7 Non-circumvention: E1–E4 + checker (200k)
- V18.8 Convergence/Stability: G1–G4 + checker
