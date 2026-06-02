# THEOREM_INVENTORY
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

## Section A — Théorèmes Lean 4 (LEAN_PROVEN)

| # | Theorem / Invariant | Source | Type | Status | Property | Layer | Depends on | Used by | Claim allowed | Claim forbidden |
|---|---------------------|--------|------|--------|----------|-------|------------|---------|---------------|-----------------|
| L1 | `D1_determinism` | `Basic.lean` | Lean | LEAN_PROVEN | `decision m θ = decision m θ` — la fonction de décision est déterministe | OS0/OS1 | `decision` def | L2, L3, L5, P17_Determinism | "La décision de base est déterministe" | "L'architecture entière est déterministe" |
| L2 | `E2_no_act_below_threshold` | `Basic.lean` | Lean | LEAN_PROVEN | Si `θ > m.S` → HOLD (jamais ACT sous le seuil) | OS0/OS1 | D1_determinism | L5, L7 | "Aucun ACT en dessous du seuil θ" | "Aucun ACT sans conditions multiples" |
| L3 | `decision_eq_ACT_iff` | `Basic.lean` | Lean | LEAN_PROVEN | ACT ssi `θ ≤ m.S` — caractérisation exacte | OS0 | Basic defs | L4 | "ACT est caractérisé exactement par θ ≤ S" | "Toute action nécessite ACT" |
| L4 | `decision_eq_HOLD_iff` | `Basic.lean` | Lean | LEAN_PROVEN | HOLD ssi `θ > m.S` | OS0 | Basic defs | L5 | "HOLD est la décision par défaut si seuil non atteint" | — |
| L5 | `X108_no_act_before_tau` | `TemporalKernel.lean:17` | Lean | LEAN_PROVEN | `irr=true ∧ elapsed < τ → decideX108 = HOLD` — jamais ACT avant τ | OS1 TEMPORAL | D1, L2 | L6, L8, TLA SafetyX108 | "X108 ne peut pas ACT avant que τ soit écoulé (irréversible)" | "X108 est temporellement sûr en général" |
| L6 | `X108_after_tau_equals_base` | `TemporalKernel.lean:26` | Lean | LEAN_PROVEN | Après τ, kernel = décision de base | OS1 | L5 | L7, L8 | "Après τ, X108 délègue à la décision de base" | — |
| L7 | `X108_kernel_never_blocks` | `TemporalKernel.lean:37` | Lean | LEAN_PROVEN | `¬(decide3X108 = BLOCK)` — le kernel X108 n'émet jamais BLOCK | OS1 | L5, L6 | Refinement.x108_never_blocks | "X108 n'émet jamais BLOCK" | "X108 ne peut pas bloquer une action" |
| L8 | `X108_reversible_equals_base` | `TemporalKernel.lean:51` | Lean | LEAN_PROVEN | `irr=false → decideX108 = decision` | OS1 | D1 | — | "Les décisions réversibles ne sont pas affectées par τ" | — |
| L9 | `X108_irreversible_after_tau_equals_base` | `TemporalKernel.lean:56` | Lean | LEAN_PROVEN | `τ ≤ elapsed → decideX108_irr_true = decision` | OS1 | L5, L6 | — | "Après τ, même irréversible suit la base" | — |
| L10 | `Refinement.lift_refines` | `Refinement.lean` | Lean | LEAN_PROVEN | `R_decision d (liftDecision d)` — le relèvement raffine | OS1→OS2 | SystemModel | L11 | "Le raffinement est correct" | — |
| L11 | `Refinement.x108_never_blocks` | `Refinement.lean` | Lean | LEAN_PROVEN | Kernel raffiné ne produit jamais BLOCK | OS1→OS2 | L7 | L12 | "Le kernel raffiné ne bloque jamais" | "Tout le système ne peut pas bloquer" |
| L12 | `Refinement.refined_not_block` | `Refinement.lean` | Lean | LEAN_PROVEN | `R_decision d d3 → ¬(d3 = BLOCK)` | OS1→OS2 | L10, L11 | — | "Toute décision raffinée n'est pas BLOCK" | — |
| L13 | `P13_Immutability` | `Seal.lean` | Lean | LEAN_PROVEN | Modification des fichiers → changement du globalSeal | OS3 SEAL | P15, merkle2_right_mutation | replay | "Le seal détecte toute modification de fichiers" | "Le seal garantit l'intégrité sans hypothèse cryptographique" |
| L14 | `P15_Immutability_Strong` | `Sensitivity.lean` | Lean | LEAN_PROVEN | `repo ≠ repo' → globalSeal ≠ globalSeal'` | OS3 MERKLE | merkleRoot_change, SealAssumptions.combine_inj | P13 | "Toute modification du repo est détectée par le seal Merkle" | "P15 prouve l'intégrité sans hypothèse cryptographique" |
| L15 | `merkleRoot_change_if_leaf_change` | `Sensitivity.lean` | Lean | LEAN_PROVEN | Changement feuille → changement racine Merkle | OS3 | foldl_H_injective | P15 | "La racine Merkle est sensible à tout changement de feuille" | — |
| L16 | `merkle2_right_mutation` | `Merkle.lean` | Lean | LEAN_PROVEN | `b≠b' → merkle2 a b ≠ merkle2 a b'` | OS3 | H_injective_right | P13, P15 | "Merkle2 est injectif sur l'argument droit" | — |
| L17 | `foldl_H_injective` | `Merkle.lean` (implied) / `CryptoAssumptions.lean` | Lean | LEAN_PROVEN | H est injectif (sous hypothèse) | OS3 | CryptoAssumptions | L15, L16 | "Le hash H est injectif dans le modèle" | "H est une vraie fonction de hachage cryptographique" |
| L18 | `aggregate4_act` | `Consensus.lean` | Lean | LEAN_PROVEN | 3/4 ACT → aggregate = ACT (supermajorité) | OS3 CONSENSUS | countDec | aggregate4_fail_closed | "3/4 ACT donne ACT" | — |
| L19 | `aggregate4_fail_closed` | `Consensus.lean` | Lean | LEAN_PROVEN | Sans supermajorité → aggregate = BLOCK (fail-closed) | OS3 | L18 | consensus layer | "Le consensus échoue fermé sans quorum" | "Sans quorum le système est sécurisé de toutes les manières" |
| L20 | `aggregate4_unanimous` | `Consensus.lean` | Lean | LEAN_PROVEN | `aggregate4 d d d d = d` | OS3 | — | — | "L'unanimité est préservée" | — |
| L21 | `no_two_distinct_supermajorities_4` | `Consensus.lean` | Lean | LEAN_PROVEN | Pas deux supermajorités distinctes simultanées | OS3 | case analysis | safety | "Deux décisions contradictoires ne peuvent pas avoir supermajorité simultanément" | — |
| L22 | `canonicalize_preserves_nonneg` | `TemporalBridge.lean` | Lean | LEAN_PROVEN | `e ≥ 0 → canonicalize_elapsed e = Int.toNat e` | OS1 BRIDGE | TemporalRaw | L23 | "La canonicalisation préserve la non-négativité" | — |
| L23 | `skew_negative_implies_hold` | `TemporalBridge.lean` | Lean | LEAN_PROVEN | `irr=true ∧ elapsed<0 ∧ τ≥0 → decide_with_skew = HOLD` | OS1 BRIDGE | L22 | External Signals | "Un skew temporel négatif force HOLD (irréversible)" | "Le système est immunisé contre tout skew" |
| L24 | `P17_Determinism` | `SystemModel.lean` | Lean | LEAN_PROVEN | `transition s i = transition s i` | OS2 | D1 | — | "Le système est déterministe à l'état donné" | — |
| L25 | `P17_AuditGrowth` | `SystemModel.lean` | Lean | LEAN_PROVEN | Audit log croît strictement à chaque transition | OS2 | P17_AuditLastIsComputed | replay | "L'audit log ne rétrécit jamais" | — |
| L26 | `P17_AuditLastIsComputed` | `SystemModel.lean` | Lean | LEAN_PROVEN | Le dernier enregistrement d'audit est la décision courante | OS2 | transition def | L25 | "L'audit log est cohérent avec les transitions" | — |
| L27 | `P17_KernelNeverBlocks` | `SystemModel.lean` | Lean | LEAN_PROVEN | L'instance institutionnelle ne BLOCK jamais | OS2 | L7, L11 | — | "Le système institutionnel ne bloque jamais" | — |
| L28 | `SealAssumptions.combine_inj` | `CryptoAssumptions.lean` | Lean | LEAN_PROVEN (sous axiome) | combine est injectif → immutabilité seal | OS3 | axiome cryptographique | P13, P15 | "L'immutabilité repose sur une hypothèse d'injectivité" | "Prouvé sans hypothèse cryptographique" |

---

## Section B — Spécifications TLA+ (FORMAL_TLA_SPEC_PRESENT)

| # | Spec | File | Status | Property | Note |
|---|------|------|--------|----------|------|
| T1 | `SafetyX108` | `formal/tla/X108.tla` | FORMAL_TLA_SPEC_PRESENT | `□(irr ∧ elapsed < τ → decision ≠ ACT)` | TLC non relancé — ne pas clamer "TLA+ vérifié" |
| T2 | Distributed consensus | `formal/tla/DistributedX108.tla` | FORMAL_TLA_SPEC_PRESENT | N=3f+1, consensus sous perte de nœuds | TLC non relancé |
| T3 | RFC3161 spec | `formal/tla/RFC3161Spec.tla` | FORMAL_TLA_SPEC_PRESENT | Horodatage temporel RFC3161 | TLC non relancé |
| T4 | TLA verification spec | `formal/tla/TLAVerificationSpec.tla` | FORMAL_TLA_SPEC_PRESENT | Vérification globale | TLC non relancé |

---

## Section C — Vérificateur Python V18_7 (PYTHON_TEST_ONLY)

| # | Property | Source | Status | Note |
|---|----------|--------|--------|------|
| V1 | Lattice meet ALLOW < HOLD < BLOCK | `proofs/V18_7/checker/noncircumvention_checker.py` | PYTHON_TEST_ONLY | meet(a,b) = max(ORDER[a], ORDER[b]) |
| V2 | Nonce anti-replay gate | `noncircumvention_checker.py` | PYTHON_TEST_ONLY | NonceStore.fresh() |
| V3 | Risk gate | `noncircumvention_checker.py` | PYTHON_TEST_ONLY | risk > threshold → BLOCK |
| V4 | X108 time lock gate | `noncircumvention_checker.py` | PYTHON_TEST_ONLY | irr ∧ elapsed < τ → HOLD |
| V5 | Noncircumvention (200k iterations) | `noncircumvention_checker.py` | PYTHON_TEST_ONLY | Fuzz, pas preuve formelle |

---

## Section D — Python Specs périphériques (PYTHON_SPEC)

| # | Property | Source | Status | Note |
|---|----------|--------|--------|------|
| PS1 | Lyapunov stability | `periphery/math_core/lyapunov.py` | PYTHON_SPEC | FORMAL_PROOF_PENDING |
| PS2 | ProofOfGovernance | `periphery/math_core/proof_of_governance.py` | PYTHON_SPEC | FORMAL_PROOF_PENDING |
| PS3 | Governed state space | `periphery/math_core/governed_state.py` | PYTHON_SPEC | FORMAL_PROOF_PENDING |
| PS4 | OS3ProofTicket sha256 chain | `periphery/os3_ticket.py` | PYTHON_SPEC | sha256 ≠ preuve Lean |
| PS5 | Action lifecycle 10 états | `periphery/action_lifecycle.py` | PYTHON_SPEC | transitions Python |

---

## Section E — Tests Python (PYTHON_TEST_ONLY — production)

| # | Property | Tests | Status |
|---|----------|-------|--------|
| PT1 | KX108_ONLY dans tous packets Sigma | `tests/sigma/test_f62_*.py` | 650+ PASS |
| PT2 | No ACT from Sigma | `tests/sigma/test_f73_*.py` | PASS |
| PT3 | No ACT from Brody | `tests/api/test_brody_authority_escalation_no_act.py` | PASS |
| PT4 | readonly=True dans réponses Sigma | `tests/api/test_f63_*.py` | 195 PASS |
| PT5 | graphiti_write=False | `tests/sigma/test_f70_*.py` | PASS |
| PT6 | memory_write=False | `tests/api/test_no_memory_write_api.py` | PASS |
| PT7 | Bus sovereignty KX108_ONLY | `tests/api/test_f65_*.py` | 85 PASS |
