# Proof Boundary — Obsidia X-108

**Généré :** P78 — Presentation Proof Public Private Split  
**Date :** 2026-06-09  
**Mode :** DOC_INDEX_ONLY — aucune modification runtime

---

## Principe

> **Preuve technique = liée à tests, commits, manifests, hashes.**  
> **Preuve formelle ≠ approximation runtime.**

Ce répertoire indexe les preuves techniques et formelles du repo. Les preuves sont de deux types (P72) :

| Type | Exemples | Statut |
|---|---|---|
| `LEAN_PROVEN` | `guard_x108`, `temporal_gate_valid`, `canonicalize_preserves_nonneg` | Prouvé formellement en Lean |
| `PYTHON_TESTED` | GPS fail-closed, bank scenarios, trading gate | Testé en Python avec Sigma |

---

## Surface proof technique (public safe)

### Preuves formelles Lean/TLA+

| Composant | Fichier | Type |
|---|---|---|
| GuardX108 final authority | `proofs/lean/Obsidia/GuardX108.lean` | LEAN_PROVEN |
| Temporal gate valid | `proofs/lean/Obsidia/TemporalBridge.lean` | LEAN_PROVEN |
| X108 kernel never blocks | `proofs/lean/Obsidia/X108.lean` | LEAN_PROVEN |
| Sigma contracts | `proofs/tla/` | TLA+ |
| OS2 bounds | `proofs/tla/` | TLA+ |

### Ancres cryptographiques

| Ancre | Fichier | Usage |
|---|---|---|
| Merkle root | `proofs/merkle_root.json` | Hash tree du repo |
| RFC3161 timestamp | `proofs/rfc3161_anchor.json` | Horodatage cryptographique |
| ProofKit report | `proofs/PROOFKIT_REPORT.json` | Rapport complet |

### Vérificateurs

| Script | Usage |
|---|---|
| `proofs/verify_all.py` | Vérifie toutes les preuves |
| `proofs/verify_decision.py` | Vérifie décision individuelle |
| `proofs/verify_merkle.py` | Vérifie Merkle root |

---

## Invariants formels P72

Source : `docs/core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.*`

| Invariant | Statut |
|---|---|
| `GUARD_X108_FINAL_AUTHORITY` | LEAN_PROVEN |
| `NO_ACT_BEFORE_TAU` | LEAN_PROVEN |
| `SIGMA_POST_GUARD_VETO_ONLY` | P56D gel permanent |
| `DETERMINISM` | LEAN_PROVEN |
| `NO_KERNEL_MUTATION_FROM_PERIPHERY` | LEAN_PROVEN |
| `NO_MEMORY_WRITE_WITHOUT_GATE` | PYTHON_TESTED |
| `NETWORK_EGRESS_REVIEW_REQUIRED` | PYTHON_TESTED |

---

## Audit ledger paliers P56→P77

Source : `docs/core_import/` (80 fichiers)

Paliers validés par commit/test :
- P56A→P56E : Sigma gamma proof, post-guard veto
- P57→P62 : Core import triage, batches
- P63→P67 : Fusion, OS adapters, SRL, boundary
- P68→P71 : API, filesystem, network, source packs
- P72 : Invariant graph formal proof alignment
- P73→P77 : Agents, Sigma evolution, GPS, runtime, wording

---

## RSSI Evidence Pack candidates (P79)

| Candidat | Raison |
|---|---|
| `proofs/merkle_root.json` | Ancre cryptographique |
| `proofs/rfc3161_anchor.json` | Timestamp RFC3161 |
| `proofs/PROOFKIT_REPORT.json` | Rapport complet |
| `specs/00_SCOPE_DISCIPLINE/` | Claims bornés |
| `specs/01_X108_AUTHORITY/` | Autorité GuardX108 |
| `specs/09_CRITICAL_WORLDS/` | GPS/bank/trading |
| `specs/11_PROOF_REPLAY_OS3/` | Replay/attestation |
| `specs/_invariant_graph/` | Graphe invariants |
| `docs/core_import/P72_*` | Alignement formel |
| `docs/core_import/P56D_SIGMA_*` | Sigma veto boundary |
| `audit/sovereign_tickets.jsonl` | Tickets souverains |

---

**Verdict :** Surface proof identifiée. Pack RSSI evidence préparé pour P79.
