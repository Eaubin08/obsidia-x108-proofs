# INVENTAIRE DES THÉORÈMES LEAN 4 — Obsidia X-108
**Source :** `BUREAU_OBSIDIA_2026/1_AUDITS_TECHNIQUES/x108_current_lean_theorems.txt`  
**Statut :** `FREEZE_CONFIRMED` — DO_NOT_TOUCH sans approbation ROLE_005

---

## Basic.lean — Lois fondamentales du Kernel

| Théorème | Signification |
|---|---|
| `decision_eq_ACT_iff` | Condition nécessaire et suffisante pour ACT |
| `decision_eq_HOLD_iff` | Condition nécessaire et suffisante pour HOLD |
| `D1_determinism` | Le Kernel est déterministe — même input → même output |
| `G1_act_above_threshold` | ACT ssi theta ≤ S (seuil) |
| `E2_no_act_below_threshold` | Pas d'ACT si theta > S |
| `G2_boundary_inclusive` | Borne inclusive (theta = S → ACT) |
| `G3_monotonicity` | Monotonie de la décision par rapport aux métriques |
| `L11_3_no_block` | X-108 n'émet jamais BLOCK nativement (L11.3) |
| `L11_3_act` | ACT quand theta ≤ S — cas Lean |
| `L11_3_hold` | HOLD quand theta > S — cas Lean |
| `decision_not_both` | Impossibilité de décision contradictoire simultanée |

---

## Consensus.lean — Supermajorité 4 agents

| Théorème | Signification |
|---|---|
| `aggregate4_act` | Condition ACT sur 4 agents |
| `aggregate4_fail_closed` | Fail-closed sans supermajorité |
| `aggregate4_unanimous` | Consensus unanime |
| `no_act_and_hold_supermajority_4_aux` | Incompatibilité ACT+HOLD en supermajorité (auxiliaire) |
| `no_act_and_block_supermajority_4_aux` | Incompatibilité ACT+BLOCK (auxiliaire) |
| `no_hold_and_block_supermajority_4_aux` | Incompatibilité HOLD+BLOCK (auxiliaire) |
| `no_act_and_hold_supermajority_4` | Théorème principal ACT∧HOLD |
| `no_act_and_block_supermajority_4` | Théorème principal ACT∧BLOCK |
| `no_hold_and_block_supermajority_4` | Théorème principal HOLD∧BLOCK |
| `no_two_distinct_supermajorities_4` | Unicité de la supermajorité — pas deux décisions différentes |

---

## Sensitivity.lean — Immutabilité forte

| Théorème | Signification |
|---|---|
| `merkleRoot_change_if_leaf_change` | Changement feuille → changement racine Merkle |
| `globalSeal_change_if_root_change` | Changement racine → changement sceau global |
| `P15_Immutability_Strong` | P15 : immutabilité forte — toute modification est détectable |

---

## Seal.lean

| Théorème | Signification |
|---|---|
| `P13_Immutability` | P13 : immutabilité par sceau Merkle |

---

## SystemModel.lean — Modèle système

| Théorème | Signification |
|---|---|
| `P17_KernelNeverBlocks` | Le Kernel ne bloque pas son propre fonctionnement |
| `P17_Determinism` | Déterminisme du modèle système |
| `P17_SealSensitive` | Sensibilité au sceau |
| `P17_AuditLastIsComputed` | Le dernier audit est toujours calculé |
| `auditLog_append_singleton_length` | Longueur du log après ajout |
| `P17_AuditGrowth` | Croissance monotone du log d'audit |
| `P17_TransitionFstIsDecide` | La première projection de la transition est la décision |

---

## TemporalKernel.lean — Noyau temporel

| Théorème | Signification |
|---|---|
| `X108_no_act_before_tau` | Pas d'ACT avant le délai tau |
| `X108_after_tau_equals_base` | Après tau, retour à l'état de base |
| `X108_kernel_never_blocks` | Le kernel temporel ne bloque jamais |
| `X108_reversible_equals_base` | Action réversible = état de base |
| `X108_irreversible_after_tau_equals_base` | Irréversible après tau = état de base |

---

## TemporalBridge.lean

| Théorème | Signification |
|---|---|
| `canonicalize_preserves_nonneg` | Canonicalisation préserve la non-négativité |
| `skew_negative_implies_hold` | Skew négatif implique HOLD (biais sécuritaire) |

---

## Refinement.lean

| Théorème | Signification |
|---|---|
| `lift_refines` | Le lift raffine la décision |
| `x108_is_lift` | X-108 est le lift |
| `x108_never_blocks` | X-108 ne bloque jamais (raffinement) |
| `refined_not_block` | Décision raffinée ≠ BLOCK natif |

---

## Merkle.lean

| Théorème | Signification |
|---|---|
| `merkle2_left_mutation` | Mutation feuille gauche → mutation racine |
| `merkle2_right_mutation` | Mutation feuille droite → mutation racine |

---

## CryptoAssumptions.lean — Hypothèses cryptographiques

| Théorème | Signification |
|---|---|
| `H_injective_left` | Hash injectif à gauche |
| `H_injective_right` | Hash injectif à droite |
| `decodeFold_H_of_decodable` | decodeFold sur hash décodable |
| `append_nil_local` | Append avec liste vide = identité |
| `append_assoc_local` | Associativité de l'append |
| `decodeFold_foldl_of_decodable` | decodeFold comme foldl |
| `decodeFold_foldl_neutral` | Neutralité de decodeFold avec foldl |
| `foldl_H_injective` | foldl avec H est injectif |
| `fileHash_inj` | fileHash est injectif |
| `combine_inj` | combine est injectif |

---

## ConsensusScratch.lean (wip)

| Théorème | Signification |
|---|---|
| `fold_count_succ` | Comptage avec succ |
| `countDec_cons_same` | Comptage d'une décision identique dans une liste |

---

## Fichiers TLA+

| Spec | Localisation | Rôle |
|---|---|---|
| `X108.tla` | `formal/tla/` + `proofs/tla/` | Spécification core X-108 |
| `X108_MC.tla` | `formal/tla/` | Model-checker X-108 |
| `DistributedX108.tla` | `proofs/tla/` | Kernel distribué |
| `DistributedX108_MC.tla` | `proofs/tla/` | MC distribué |
| `ObsidiaDistX108A11.tla` | `proofs/tla/` | Variante A11 |
| `ObsidiaDistX108A12.tla` | `proofs/tla/` | Variante A12 |

---

## Preuves périphériques (bundles V3)

| Fichier | Théorème | Statut |
|---|---|---|
| `P107.lean` | Stabilité de Lyapunov δ-ε | `A_PROUVER` via sandbox |
| `P161.lean` | Calibration énergétique temporelle | `A_PROUVER` via sandbox |
| `P36.lean` | Quintuplet d'état canonique (S,I,L) | `A_PROUVER` via sandbox |

Localisation : `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/`
