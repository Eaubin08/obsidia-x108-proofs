# Obsidia X-108 - External Pack

> Date: 2026-05-30 | Milestone: F77 | Status: READY_FOR_REVIEW | Authority: KX108_ONLY

## What this is

Obsidia X-108 is a deterministic governance kernel with a single decision authority: **KX108_ONLY**. This pack provides external reviewers with the documentation, proof index, and compliance evidence needed to audit the system independently.

## Pack contents

| File | Purpose |
|---|---|
| [SOVEREIGNTY_MANIFEST.md](SOVEREIGNTY_MANIFEST.md) | Formal declaration of KX108_ONLY authority and verifiable output invariants |
| [PROOF_INDEX.md](PROOF_INDEX.md) | Index of all formal proofs and test validation artefacts |
| [LEAN_THEOREMS.md](LEAN_THEOREMS.md) | Verbatim Lean 4 theorems from `TemporalKernel.lean` |
| [COMPLIANCE_CHECKLIST.md](COMPLIANCE_CHECKLIST.md) | Reproducibility and environment checklist |
| [KNOWN_LIMITS.md](KNOWN_LIMITS.md) | Known limitations - explicitly declared, not hidden |
| [SECURITY_SURFACE.md](SECURITY_SURFACE.md) | Security posture: what is protected and what is pending |
| [DEFERRED_PHASES.md](DEFERRED_PHASES.md) | Phases explicitly deferred - not claimed as complete |
| [DOCKER_GUIDE.md](DOCKER_GUIDE.md) | Container build and deployment guide |
| [ENV_REFERENCE.md](ENV_REFERENCE.md) | Environment variable reference (no secrets included) |
| [RELEASE_NOTES_F77.md](RELEASE_NOTES_F77.md) | F74->F77 milestone summary and validation state |

## Decision authority

All outputs from this system are **read-only advisory signals**. The sole decision authority is **KX108_ONLY**. No sub-component - Brody, Sigma, Bus, Blockchain classifiers - can emit ACT, VERDICT, or mutate state. This is enforced by code at every API output boundary.

```
GET /api/health
-> {"status": "ok", "decision_authority": "KX108_ONLY", "readonly": true, "emits_act": false}
```

## Test validation

Full tests/api: **1973 PASS, 0 failed** (2026-05-30, 8566.23s / 2:22:46). Targeted non-regression: **1203 PASS, 0 failed** (2026-05-30, 196.49s).

## What this pack does NOT claim

- This system is not production-deployed in any cloud environment.
- This system does not claim AGI, consciousness, or general reasoning capabilities.
- Sigma, Bus, and Brody sovereignty properties are validated by Python tests - not by Lean formal proofs.
- TLA+ specifications exist but TLC was not re-executed in this session.
- Merkle seals exist but were not re-verified in this session.
- Authentication is implemented for local validation; external cloud deployment is not active.
- This repository is not the full proprietary production engine.

## Security contact

Security disclosures: **security@obsidia.io**
Audit requests (NDA): **contact@obsidia.io**

