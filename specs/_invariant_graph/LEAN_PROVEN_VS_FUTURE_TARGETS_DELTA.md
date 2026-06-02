# LEAN_PROVEN_VS_FUTURE_TARGETS_DELTA

Status: DOCUMENTATION
Authority: KX108_ONLY
Runtime Status: DOC_ONLY
Date: 2026-06-02

---

## Source

Audit : `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX.md`
Audit : `_source_discovery/OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1/P107_P161_FORMAL_TARGET_REPORT.md`

---

## Scope

Matrice de comparaison entre les 28 théorèmes Lean-proven et les cibles formelles futures.
Permet d'identifier exactement ce qui est prouvé vs ce qui reste à faire.

---

## COLONNE A — Lean-proven (28 théorèmes)

Ces théorèmes compilent sous `lake build` dans `proofs/lean/`.

| # | Théorème | Fichier Lean | Groupe |
|---|----------|-------------|--------|
| L1 | `D1_determinism` | `Basic.lean` | Déterminisme |
| L2 | `E2_no_act_below_threshold` | `Basic.lean` | Gate |
| L3 | `decision_eq_ACT_iff` | `Basic.lean` | Caractérisation |
| L4 | `decision_eq_HOLD_iff` | `Basic.lean` | Caractérisation |
| L5 | `X108_no_act_before_tau` | `TemporalKernel.lean` | Gate temporelle |
| L6 | `X108_after_tau_equals_base` | `TemporalKernel.lean` | Libération |
| L7 | `X108_kernel_never_blocks` | `TemporalKernel.lean` | Non-blocage |
| L8 | `X108_reversible_equals_base` | `TemporalKernel.lean` | Réversibilité |
| L9 | `X108_irreversible_after_tau_equals_base` | `TemporalKernel.lean` | Irréversibilité |
| L10 | `Refinement.lift_refines` | `Refinement.lean` | Raffinement |
| L11 | `Refinement.x108_never_blocks` | `Refinement.lean` | Non-blocage raffiné |
| L12 | `Refinement.refined_not_block` | `Refinement.lean` | Raffinement |
| L13 | `P13_Immutability` | `Seal.lean` | Immutabilité Seal |
| L14 | `P15_Immutability_Strong` | `Sensitivity.lean` | Sensibilité |
| L15 | `merkleRoot_change_if_leaf_change` | `Merkle.lean` | Merkle |
| L16 | `merkle2_right_mutation` | `Merkle.lean` | Merkle |
| L17 | `foldl_H_injective` | `Merkle.lean` | Merkle |
| L18 | `aggregate4_act` | `Consensus.lean` | Consensus |
| L19 | `aggregate4_fail_closed` | `Consensus.lean` | Consensus |
| L20 | `aggregate4_unanimous` | `Consensus.lean` | Consensus |
| L21 | `no_two_distinct_supermajorities_4` | `Consensus.lean` | Consensus |
| L22 | `canonicalize_preserves_nonneg` | `TemporalBridge.lean` | Bridge temporel |
| L23 | `skew_negative_implies_hold` | `TemporalBridge.lean` | Bridge temporel |
| L24 | `P17_Determinism` | `SystemModel.lean` | Système |
| L25 | `P17_AuditGrowth` | `SystemModel.lean` | Système |
| L26 | `P17_AuditLastIsComputed` | `SystemModel.lean` | Système |
| L27 | `P17_KernelNeverBlocks` | `SystemModel.lean` | Système |
| L28 | `SealAssumptions.combine_inj` | `CryptoAssumptions.lean` | Crypto (axiome) |

**Claim autorisé :** "28 théorèmes Lean 4 prouvent le kernel X-108, le consensus, l'immutabilité Merkle/Seal et le bridge temporel."

---

## COLONNE B — Python-tested (périphéries, pas Lean)

| Propriété | Tests | Claim autorisé | Claim interdit |
|-----------|-------|----------------|----------------|
| KX108_ONLY dans Sigma | 650+ PASS | "validé par tests Python" | "prouvé Lean" |
| No ACT from Brody | PASS | "validé par tests Python" | "prouvé Lean" |
| readonly=True | 195 PASS | "validé par tests Python" | "prouvé Lean" |
| graphiti_write=False | PASS | "validé par tests Python" | "prouvé Lean" |
| memory_write=False | PASS | "validé par tests Python" | "prouvé Lean" |
| Bus sovereignty KX108_ONLY | 85 PASS | "validé par tests Python" | "prouvé Lean" |

---

## COLONNE C — TLA_SPEC_PRESENT (TLC non relancé)

| Spec | Fichier | Note |
|------|---------|------|
| SafetyX108 | `formal/tla/X108.tla` | TLC non relancé — ne pas clamer "vérifié" |
| Distributed consensus | `formal/tla/DistributedX108.tla` | TLC non relancé |
| RFC3161 | `formal/tla/RFC3161Spec.tla` | TLC non relancé |

---

## COLONNE D — FUTURE_FORMAL_TARGETS (pas encore prouvés)

| Propriété | Statut actuel | Plan de formalisation |
|-----------|--------------|----------------------|
| P107 Lyapunov stability | LEAN_SKELETON_ONLY / DOC_ONLY | Plan 4+ |
| P161 Energetic calibration | LEAN_SKELETON_ONLY / DOC_ONLY | Plan 4+ |
| NPL provenance layer | SPEC_FUTURE | Plan 2 → Plan 4+ éventuel |
| Thermodynamique cognitive | THEORY_ONLY | Plan 4+ éventuel |
| ProofOfGovernance | PYTHON_SPEC | Plan 4+ |
| Gate G1 (P36+P107+P161) | PARTIAL | Plan 4+ |
| Gate G5 | NON FRANCHISSABLE | dépend de Gate G1 |

---

## Résumé

| Catégorie | Nombre | Status |
|-----------|--------|--------|
| Lean-proven | 28 | FORMAL — lake build ✅ |
| Python-tested uniquement | 7+ | PYTHON_TEST_ONLY |
| TLA spec présente | 4 | TLC non relancé |
| Future formal targets | 7 | À formaliser Plan 4+ |

---

## Invariants

- 28 théorèmes Lean = socle formel immuable du kernel
- P107, P161, NPL ∉ 28 théorèmes
- Gate G1 = PARTIAL → Gate G5 non franchissable
- TLA+ = présent mais TLC non relancé — ne pas clamer "model-checked"

## X108 Boundary

KX108_ONLY

## Claim-Scope Notes

Ce fichier est la source de vérité pour distinguer ce qui EST prouvé de ce qui NE L'EST PAS.
Mettre à jour dès qu'un FUTURE_FORMAL_TARGET est prouvé en Lean.
