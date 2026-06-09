# RSSI Evidence Pack — Obsidia X-108

**Généré :** P79 — RSSI Evidence Pack and GitHub Security Audit  
**Date :** 2026-06-09  
**Mode :** AUDIT_AND_DOCS_ONLY — aucune modification runtime

---

## Principe

> **Pack RSSI evidence = preuves techniques vérifiables, non moteur propriétaire complet.**  
> **Public proof ≠ accès runtime.**  
> **Ancre cryptographique = fait établi par tiers (RFC3161 Free TSA).**

Ce répertoire indexe le pack d'evidence RSSI local constitué en P79. Le pack distingue :
- Ce qui est **publiable** (INCLUDE_RSSI_PACK)
- Ce qui est **interne uniquement** (INCLUDE_INTERNAL_RSSI_ONLY)
- Ce qui est **DO_NOT_PUBLISH**

---

## Composants du pack

### Ancres cryptographiques

| Fichier | Description | Vérifiable |
|---|---|---|
| `proofs/merkle_root.json` | Merkle root SHA-256 `b9ac7a047f...` | `python proofs/verify_merkle.py` |
| `proofs/rfc3161_anchor.json` | RFC3161 Free TSA 2026-03-03, serial 0x03572CED | `openssl ts -verify ...` |

### Preuves formelles

| Composant | Type | Statut |
|---|---|---|
| `proofs/lean/` (9 fichiers) | Lean 4 | LEAN_PROVEN |
| `proofs/tla/` (17 fichiers) | TLA+ | TLA_VERIFIED |
| `specs/_invariant_graph/` (10 fichiers) | Graphe invariants | FORMAL_MAP |
| `docs/core_import/P72_*` | Alignement 23 invariants | AUDIT_LEDGER |

### Replay / Vérification

```bash
# Vérification complète
python proofs/verify_all.py

# Vérification Merkle
python proofs/verify_merkle.py

# Vérification décision individuelle
python proofs/verify_decision.py <envelope.json>

# Manifest SHA-256
python scripts/verify_recursive_manifest.py
```

### Specs evidence

| Groupe | Contenu | Entrées |
|---|---|---|
| `specs/00_SCOPE_DISCIPLINE/` | Claims bornés, assertions autorisées | 9 |
| `specs/01_X108_AUTHORITY/` | Autorité GuardX108 | 7 |
| `specs/09_CRITICAL_WORLDS/` | GPS/bank/trading/aviation | 14 |
| `specs/11_PROOF_REPLAY_OS3/` | RFC3161, Merkle replay, attestation | 9 |

---

## Ce qui N'EST PAS dans le pack public

| Zone | Raison |
|---|---|
| `sigma/` | Runtime souverain propriétaire |
| `runtime_wiring/` | Wiring interne |
| `connectors/` | BLOCK_CONNECTOR_RUN P70 |
| `periphery/` | 3278 fichiers propriétaires |
| `audit/world_action_bus.jsonl` | Données runtime souveraines |
| `docs/runtime/` | Archives terrain locales |
| `docs/gencoin/` + `specs/10_*` | Review légale token requise |

---

## Index complet

Voir : `docs/rssi/RSSI_EVIDENCE_INDEX.md`  
Frontières : `docs/rssi/RSSI_EVIDENCE_BOUNDARY.md`  
DO_NOT_PUBLISH : `docs/rssi/RSSI_DO_NOT_PUBLISH.md`

---

**Verdict :** Pack RSSI evidence constitué. 29 groupes INCLUDE_RSSI_PACK. Ancres cryptographiques vérifiées.
