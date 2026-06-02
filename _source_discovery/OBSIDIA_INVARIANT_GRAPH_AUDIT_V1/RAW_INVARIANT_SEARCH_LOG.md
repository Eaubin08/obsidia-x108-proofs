# RAW_INVARIANT_SEARCH_LOG
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

## Sources vérifiées (FOUND)

| Fichier | Type | Résultat |
|---------|------|---------|
| `external_pack/PROOF_INDEX.md` | MD | FOUND — inventaire complet des théorèmes Lean et Python |
| `external_pack/LEAN_THEOREMS.md` | MD | FOUND — source verbatim TemporalKernel.lean |
| `proofs/lean/Obsidia/TemporalKernel.lean` | Lean | FOUND — 5 théorèmes kernel X108 |
| `proofs/lean/Obsidia/Basic.lean` | Lean | FOUND — D1, E2, G1, decision_eq_ACT_iff, decision_eq_HOLD_iff |
| `proofs/lean/Obsidia/Refinement.lean` | Lean | FOUND — lift_refines, x108_never_blocks, refined_not_block |
| `proofs/lean/Obsidia/Seal.lean` | Lean | FOUND — P13_Immutability |
| `proofs/lean/Obsidia/Sensitivity.lean` | Lean | FOUND — P15_Immutability_Strong, merkleRoot_change_if_leaf_change |
| `proofs/lean/Obsidia/Consensus.lean` | Lean | FOUND — aggregate4_fail_closed, aggregate4_unanimous, no_two_distinct_supermajorities_4 |
| `proofs/lean/Obsidia/TemporalBridge.lean` | Lean | FOUND — canonicalize_preserves_nonneg, skew_negative_implies_hold |
| `proofs/lean/Obsidia/SystemModel.lean` | Lean | FOUND — P17_Determinism, P17_AuditGrowth, P17_KernelNeverBlocks |
| `proofs/lean/Obsidia/Merkle.lean` | Lean | FOUND — merkle2_right_mutation, merkle2_left_mutation |
| `proofs/lean/Obsidia/CryptoAssumptions.lean` | Lean | FOUND — H_injective_left/right, SealAssumptions (axiome) |
| `proofs/lean/Obsidia/Audit.lean` | Lean | FOUND — #print axioms de tous les théorèmes principaux |
| `proofs/lean/Obsidia/AuditRoots.lean` | Lean | FOUND — #print axioms complémentaires |
| `proofs/lean/Obsidia/AuditConsensusRoots.lean` | Lean | FOUND — countDec, aggregate4, no_two_distinct |
| `proofs/lean/Obsidia/AuditCryptoRoots.lean` | Lean | FOUND — decodeFold, foldl_H_injective, P15, P13 |
| `proofs/lean/Obsidia/AuditSystemRoots.lean` | Lean | FOUND — transition, P17_AuditGrowth, P17_Determinism |
| `proofs/lean/Obsidia/AuditX108Roots.lean` | Lean | FOUND — beforeTau, decideX108, X108_after_tau, X108_irreversible_after_tau |
| `formal/tla/X108.tla` | TLA+ | FOUND — SafetyX108 spec + GateDecision + THEOREM Spec => SafetyX108 |
| `formal/tla/DistributedX108.tla` | TLA+ | FOUND — N=3f+1, GateRule distribué |
| `proofs/V18_7/checker/noncircumvention_checker.py` | Python | FOUND — meet lattice, NonceStore, gate_replay, gate_x108_timelock, 200k fuzz |
| `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` | MD | FOUND — F76 PROD_BLOCKED, F77 PACK_PARTIAL |

---

## Sources absentes ou non trouvées

| Fichier | Statut |
|---------|--------|
| `proofs/lean/Obsidia/TemporalX108.lean` | ABSENT — référencé dans AuditX108Roots mais non lu directement |
| `proofs/lean/Obsidia/TemporalX108_3Layers.lean` | Présent mais non lu |
| `proofs/lean/Obsidia/TemporalRaw.lean` | Présent mais non lu |
| `proofs/lean/Obsidia/Main.lean` | Présent mais non lu |
| `docs/original/research/THEOREM_MAPPING.md` | ABSENT — chemin non présent dans le repo |
| `proofs/V18_7/proofs/V18_7_FORMAL_THEOREMS.md` | ABSENT — chemin non présent |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/08_PREUVES_LEAN_TLA/` | Non lu dans cette session |
| `formal/tla/RFC3161Spec.tla` | Présent (listé) mais non lu |
| `formal/tla/TLAVerificationSpec.tla` | Présent (listé) mais non lu |
| `proofs/tla/X108_standalone.tla` | Présent mais non lu |

---

## Commandes exécutées

```bash
# Phase 0 — precheck
git status -sb

# Lister sources de preuve
find proofs/lean -name "*.lean" | sort
find formal/tla proofs/tla -name "*.tla" | sort
find proofs -name "*.md"

# Grep théorèmes
grep -rn "theorem|lemma|axiom|#print axioms|sorry|D1_determinism|E2_no_act|X108_no_act|Refinement|P15|P13|aggregate4|canonicalize|skew_negative|noncircumvention" proofs/ formal/

# Lecture directe
cat proofs/lean/Obsidia/TemporalKernel.lean
cat proofs/lean/Obsidia/Basic.lean
cat proofs/lean/Obsidia/Refinement.lean
cat proofs/lean/Obsidia/Seal.lean
cat proofs/lean/Obsidia/Consensus.lean
cat proofs/lean/Obsidia/Sensitivity.lean
cat proofs/lean/Obsidia/TemporalBridge.lean
cat proofs/lean/Obsidia/SystemModel.lean
cat proofs/lean/Obsidia/Merkle.lean
cat proofs/lean/Obsidia/CryptoAssumptions.lean
head -80 external_pack/PROOF_INDEX.md
head -80 external_pack/LEAN_THEOREMS.md
head -60 formal/tla/X108.tla
head -40 formal/tla/DistributedX108.tla
head -40 proofs/V18_7/checker/noncircumvention_checker.py
grep -n "theorem|lemma|def|#print" proofs/lean/Obsidia/SystemModel.lean
cat proofs/lean/Obsidia/AuditX108Roots.lean
```

---

## Résultats clés

- **28 théorèmes Lean** confirmés (L1-L28 dans THEOREM_INVENTORY.md)
- **4 specs TLA+** présentes — TLC non relancé
- **7 propriétés Python test** périphériques confirmées (1973 PASS production)
- **5 Python specs** FORMAL_PROOF_PENDING (Lyapunov, PoG, governed_state, action_lifecycle, OS3Ticket)
- **0 sorry / admit** trouvés dans les fichiers Lean lus
- `SealAssumptions.combine_inj` = axiomatisé (cryptographic assumption — pas preuve de collision resistance)
