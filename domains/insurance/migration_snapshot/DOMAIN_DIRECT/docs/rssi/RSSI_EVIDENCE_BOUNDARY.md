# RSSI Evidence Boundary — Obsidia X-108

**Généré :** P79  
**Date :** 2026-06-09

---

## Frontière : ce qui entre dans le pack RSSI

```
RSSI EVIDENCE PACK (publiable)
├── Ancres cryptographiques
│   ├── proofs/merkle_root.json          SHA-256 b9ac7a...
│   └── proofs/rfc3161_anchor.json       RFC3161 Free TSA 2026-03-03
│
├── Preuves formelles
│   ├── proofs/lean/                     9 théorèmes LEAN_PROVEN
│   ├── proofs/tla/                      17 specs TLA+
│   ├── specs/_invariant_graph/          10 fichiers graphe invariants
│   └── docs/core_import/P72_*           23 invariants alignés
│
├── Vérificateurs
│   ├── proofs/verify_all.py
│   ├── proofs/verify_decision.py
│   ├── proofs/verify_merkle.py
│   ├── scripts/generate_recursive_manifest.py
│   ├── scripts/verify_recursive_manifest.py
│   └── tools/anchor_merkle_root.py + verify_chain_anchor.py
│
├── Specs evidence
│   ├── specs/00_SCOPE_DISCIPLINE/       Claims bornés
│   ├── specs/01_X108_AUTHORITY/         GuardX108 LEAN_PROVEN
│   ├── specs/09_CRITICAL_WORLDS/        GPS/bank/trading/aviation
│   └── specs/11_PROOF_REPLAY_OS3/       Replay/attestation
│
├── Audit trail
│   └── docs/core_import/P56D_SIGMA_*   Gel permanent Sigma veto
│
└── Boundary docs
    ├── docs/public/README_PUBLIC_BOUNDARY.md
    ├── docs/proof/README_PROOF_BOUNDARY.md
    └── SECURITY.md

RSSI EVIDENCE INTERNE SEULEMENT
├── docs/core_import/                    82 fichiers P56A→P78
├── audit/sovereign_tickets.jsonl        Tickets souverains
└── proofs/PROOFKIT_REPORT.json         (gitignore conflict — revue)

HORS PACK (DO_NOT_PUBLISH)
├── sigma/                              Runtime souverain KX108_ONLY
├── runtime_wiring/                     Wiring interne
├── connectors/                         BLOCK_CONNECTOR_RUN P70
├── periphery/                          3278 fichiers propriétaires
├── audit/world_action_bus.jsonl        Données runtime souveraines
└── (+ tout DO_NOT_PUBLISH P78)
```

---

## Invariants pack RSSI

| Invariant | Statut | Fichier |
|---|---|---|
| `GUARD_X108_FINAL_AUTHORITY` | LEAN_PROVEN | `proofs/lean/GuardX108.lean` |
| `NO_ACT_BEFORE_TAU` | LEAN_PROVEN | `proofs/lean/TemporalBridge.lean` |
| `DETERMINISM` | LEAN_PROVEN | `proofs/lean/` |
| `SIGMA_POST_GUARD_VETO_ONLY` | P56D GEL PERMANENT | `docs/core_import/P56D_*` |
| `FAIL_CLOSED_GPS` | PYTHON_TESTED | `specs/09_CRITICAL_WORLDS/` |
| `MERKLE_HASH_VERIFIED` | CRYPTOGRAPHIC | `proofs/merkle_root.json` |
| `RFC3161_TIMESTAMP_ANCHORED` | CRYPTOGRAPHIC | `proofs/rfc3161_anchor.json` |
