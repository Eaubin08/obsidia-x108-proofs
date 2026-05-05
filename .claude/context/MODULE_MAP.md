# Module Map (compact)

> Compact overview. Drill down only when needed. Keep this file ≤ 200 lines.

## Top-level structure

```
proofs/                Core proof corpus
  lean/                Lean 4 (Obsidia.lean, ObsidiaCore.lean, ObsidiaAuditRoots.lean) — PROTECTED
  tla/                 TLA+ reference specs (X108.tla, X108_MC.tla, DistributedX108.tla) — PROTECTED
  V18_3_1/  V18_7/     Versioned proof bundles — PROTECTED (freeze)
  V18_8/
  verify_all.py        Public audit verifier
  verify_decision.py   Verifies a single envelope
  verify_merkle.py     Verifies Merkle inclusion
  merkle_root.json     CRYPTO ANCHOR — PROTECTED
  merkle_seal.json     CRYPTO ANCHOR — PROTECTED
  rfc3161_anchor.json  TSA ANCHOR — PROTECTED
  PROOFKIT_REPORT.json Status report (currently FAIL on V18_3_1)

formal/tla/            TLA+ specs run by CI — PROTECTED (mirrors with proofs/tla/)

sigma/                 Sigma orchestration / periphery / QA
  tests/               pytest suite (~20 files: bank, GPS, trading, pipeline, monitor)
  contracts.broken-ragnarok.py   INTENTIONAL negative fixture — DO NOT FIX

qa/cross-platform/     RFC3161 schema + cross-platform compatibility tests

connectors/            Domain connectors (bank, trading, gps_defense_aviation)

MonProjet/             JSON payload inputs for domain scenario runs

artifacts/             Generated run outputs (scale, fuzz, adversarial, regulatory, etc.)

audit/                 Regression matrices, audit logs, formal stack validation reports
  local/               LOCAL ONLY — never commit (gitignored)

RECUPE_SCORING/        Frozen scoring scripts — PROTECTED
  aggregation_stable.py   CI does py_compile only — logic regressions NOT caught
  contracts_stable.py     same

staging/runtime_candidates/   Pre-production runtime builds

tools/bank_robo_real/  Bank robo tooling

docs/                  SIGMA.md, KERNEL_OVERVIEW.md, AUDIT_GUIDE.md, CI_POLICY.md, LIMITS.md, etc.

.github/workflows/verify-proofs.yml   Single CI workflow
```

## Root-level files (notable)

```
run_all_proofs.ps1        Master proof runner (PowerShell)
run_bank_*.ps1            Bank scenario packs
audit_merkle.py           Merkle audit helper
view_integrity.py         Integrity viewer
merkle_root.json          (root copy — PROTECTED)
merkle_seal.json          (root copy — PROTECTED)
server.kernel.sealed.cjs  Express bridge — SEALED, never edit
package.json              Node deps
requirements.txt          Python deps (pytest, cryptography, pyopenssl, requests, pyyaml)
P1_FREEZE_NOTE.md         Freeze status doc — PROTECTED
PUBLIC_STATUS.md          Public status — PROTECTED
PROOF_INDEX.md            Proof inventory
REPO_MAP.md               Long form repo map (this file is the compact view)
SECURITY.md               Security policy
LICENSE
```

## Vendored (do not move)

```
System.*/              Vendored .NET runtime deps
Google.Protobuf.*/     Vendored .NET deps
vendor/wheels/         Python offline wheels
node_modules/          Node deps (gitignored)
```

## Build / test / verify commands (canonical, do not auto-run)

```powershell
# Python verification
python proofs/verify_all.py
python proofs/verify_decision.py <envelope.json>
python proofs/verify_merkle.py

# Sigma tests
python -m pytest sigma/tests -v

# RFC3161 QA
python -m pytest qa/cross-platform/test_rfc3161_anchor_schema.py -v
python -m pytest qa/cross-platform/test_rfc3161_cross_platform.py -v

# RECUPE_SCORING (CI does syntax only)
python -m py_compile RECUPE_SCORING/aggregation_stable.py

# Lean 4
cd proofs/lean
lake build

# TLA+ (requires tla2tools.jar locally)
java -jar tla2tools.jar -config formal/tla/X108_MC.cfg formal/tla/X108_MC.tla

# Node bridge (read-only execution; the file is sealed)
node server.kernel.sealed.cjs

# PowerShell runners
./run_all_proofs.ps1
./run_bank_test_pack.ps1     # + other run_bank_*.ps1 variants
```

**Run only when explicitly requested.** No auto-run.

## Quick "where is X" cheatsheet

| Question | Look first |
|---|---|
| Lean theorem / invariant | `proofs/lean/Obsidia*.lean`, `lakefile.lean` |
| TLA+ spec | `formal/tla/<spec>.tla` (CI) AND `proofs/tla/<spec>.tla` (reference) — both may exist |
| Sigma test | `sigma/tests/test_*.py` |
| RFC3161 / cross-platform | `qa/cross-platform/test_rfc3161_*.py` |
| Connector logic | `connectors/<domain>/` |
| Scoring / aggregation (frozen) | `RECUPE_SCORING/` |
| Domain payload | `MonProjet/*.json` |
| PowerShell runner | `run_*.ps1` at repo root |
| Past run output | `artifacts/<pack-type>/` |
| Status report | `proofs/PROOFKIT_REPORT.json` |
