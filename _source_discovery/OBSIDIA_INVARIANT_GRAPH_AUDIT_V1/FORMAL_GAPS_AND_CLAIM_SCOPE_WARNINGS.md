# FORMAL_GAPS_AND_CLAIM_SCOPE_WARNINGS
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02
# Source principale : external_pack/PROOF_INDEX.md (audité 2026-05-30)

---

## 1. Ce qui est LEAN_PROVEN (kernel X108)

Les 19 propriétés suivantes sont formellement prouvées en Lean 4 et compilent sous `lake build` :

- `D1_determinism` — déterminisme de la décision de base
- `E2_no_act_below_threshold` — no ACT sous seuil θ
- `decision_eq_ACT_iff` / `decision_eq_HOLD_iff` — caractérisation exacte
- `X108_no_act_before_tau` — gate temporelle principale
- `X108_after_tau_equals_base` — libération contrôlée
- `X108_kernel_never_blocks` — kernel jamais BLOCK
- `X108_reversible_equals_base` / `X108_irreversible_after_tau_equals_base`
- `Refinement.x108_never_blocks` / `Refinement.lift_refines` / `Refinement.refined_not_block`
- `P13_Immutability` (Seal) / `P15_Immutability_Strong` (Sensitivity)
- `merkleRoot_change_if_leaf_change` / `merkle2_right_mutation` / `foldl_H_injective`
- `aggregate4_fail_closed` / `aggregate4_unanimous` / `no_two_distinct_supermajorities_4`
- `canonicalize_preserves_nonneg` / `skew_negative_implies_hold`
- `P17_Determinism` / `P17_AuditGrowth` / `P17_AuditLastIsComputed` / `P17_KernelNeverBlocks`

**Claim autorisé :** "Le kernel X108, les propriétés de raffinement, l'immutabilité Merkle/Seal et le consensus Obsidia sont prouvés formellement en Lean 4."

---

## 2. Ce qui est TLA_SPEC_PRESENT mais TLC non relancé

- `formal/tla/X108.tla` — SafetyX108 `□(irr∧elapsed<τ→¬ACT)`
- `formal/tla/DistributedX108.tla` — consensus distribué N=3f+1
- `formal/tla/RFC3161Spec.tla` — RFC3161 horodatage
- `formal/tla/TLAVerificationSpec.tla` — vérification globale

**Note de PROOF_INDEX.md :** *"TLC was not re-executed in this session. Do not claim 'TLA+ verified' without re-running TLC."*

**Claim autorisé :** "Les specs TLA+ sont présentes dans le repo."
**Claim interdit :** "TLA+ vérifié" / "model-checking validé" sans relancer TLC.

---

## 3. Ce qui est PYTHON_TEST_ONLY (périphéries)

- KX108_ONLY dans tous packets Sigma (650+ tests PASS)
- No ACT from Sigma (tests PASS)
- No ACT from Brody (tests PASS)
- graphiti_write=False (tests PASS)
- memory_write=False (tests PASS)
- Bus sovereignty KX108_ONLY (85 tests PASS)
- V18_7 noncircumvention (200k fuzz PASS)

**Claim autorisé :** "Les propriétés de non-souveraineté des couches périphériques sont validées par des tests Python."
**Claim interdit :** "Brody / Sigma / Graphiti sont formellement prouvés non-souverains" (Lean proof absent).

---

## 4. Ce qui est PYTHON_SPEC (en attente de formalisation Lean)

- `periphery/math_core/lyapunov.py` — Lyapunov stability
- `periphery/math_core/proof_of_governance.py` — ProofOfGovernance
- `periphery/math_core/governed_state.py` — état gouverné
- `periphery/energy_thermo.py` — dette thermodynamique

**Claim autorisé :** "Obsidia calcule Lyapunov, PoG et l'état gouverné comme approximations Python."
**Claim interdit :** "Lyapunov est formellement prouvé" / "La stabilité gouvernée est Lean-prouvée."

---

## 5. Ce qui est DOC_ONLY

- Tree34 non_decision_contract — présent dans chaque arbre comme Markdown
- NPL specs Plan 2 — contractuelles mais pas implémentées
- F77 external_pack — PACK_PARTIAL, 9 fichiers manquants

**Claim autorisé :** "Les contrats de non-décision Tree34 sont documentés."
**Claim interdit :** "Tree34 est formellement prouvé non-décisionnel."

---

## 6. Ce qui est FUTURE_FORMAL_TARGET

| Target | Priorité | Note |
|--------|----------|------|
| Lean proof Lyapunov | HAUTE | FORMAL_PROOF_PENDING dans `03_ENTROPY_DISCIPLINE/` |
| Lean proof ProofOfGovernance | HAUTE | FORMAL_PROOF_PENDING |
| Lean proof non-souveraineté Sigma | MOYENNE | Actuellement PYTHON_TEST_ONLY |
| TLC re-run pour X108.tla + DistributedX108.tla | HAUTE | TLA_VERIFIED_CURRENTLY_UNKNOWN |
| RFC3161 openssl verify re-run | MOYENNE | Non relancé |
| Merkle verify_merkle.py re-run | MOYENNE | Non relancé |
| Lean proof OS3ProofTicket chain | BASSE | sha256 actuel |

---

## 7. Interdictions publiques

| Claim interdit | Raison |
|----------------|--------|
| "Le système complet est formellement prouvé" | Seul le kernel X108 est LEAN_PROVEN — les périphéries sont PYTHON_TEST_ONLY |
| "Lyapunov est Lean-prouvé" | Python spec uniquement — FORMAL_PROOF_PENDING |
| "Sigma / Brody / Graphiti sont Lean-prouvés non-souverains" | PYTHON_TEST_ONLY |
| "TLA+ vérifié current" | TLC non relancé — spec présente uniquement |
| "RFC3161 current" | openssl verify non relancé |
| "Merkle current" | verify_merkle.py non relancé |
| "Produit certifié" | Aucune certification externe existante |
| "AGI-ready" | HORS_SCOPE — explicitement interdit dans F74_F77 |
| "Production-ready" | F76 PROD_BLOCKED — 4 bloqueurs actifs |
| "NPL prouve la provenance d'une pensée" | PERIPHERAL_READONLY — signal probabiliste uniquement |
| "External Signals remplace X108" | SIGNAL_ONLY — skew_negative_implies_hold protège X108 |

---

## 8. Ce que PROOF_INDEX.md dit explicitement

> "These theorems are present in the repo and compile under `lake build`. They constitute the formal foundation of the X108 kernel."

Cette formulation est exacte et autorisée. Elle ne dit pas "tout le système est prouvé" — elle dit que le **kernel** est prouvé.
