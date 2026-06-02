# THEOREM_DEPENDENCY_GRAPH
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

Représentation textuelle du graphe de dépendances entre théorèmes.
Statuts : [CONFIRMED] = source lue, [INFERRED] = déduit logiquement, [GAP] = lien non sourcé

---

## Nœud racine — Déterminisme

```
D1_determinism (Basic.lean) [CONFIRMED]
  → E2_no_act_below_threshold (Basic.lean) [CONFIRMED]
  │   → X108_no_act_before_tau (TemporalKernel.lean) [CONFIRMED]
  │   → X108_after_tau_equals_base (TemporalKernel.lean) [CONFIRMED]
  │       → X108_reversible_equals_base (TemporalKernel.lean) [CONFIRMED]
  │       → X108_irreversible_after_tau_equals_base (TemporalKernel.lean) [CONFIRMED]
  │
  → decision_eq_ACT_iff (Basic.lean) [CONFIRMED]
  → decision_eq_HOLD_iff (Basic.lean) [CONFIRMED]
  → P17_Determinism (SystemModel.lean) [CONFIRMED]
```

## Branche Temporalité

```
X108_no_act_before_tau [CONFIRMED]
  → X108_kernel_never_blocks [CONFIRMED]
  │   → Refinement.x108_never_blocks [CONFIRMED]
  │       → Refinement.refined_not_block [CONFIRMED]
  │       → P17_KernelNeverBlocks (SystemModel.lean) [CONFIRMED]
  │
  → TLA SafetyX108 □(irr ∧ elapsed<τ → ¬ACT) [CONFIRMED — spec présente]
  │   [TLC non relancé → TLA_VERIFIED_CURRENTLY_UNKNOWN]
  │
  → skew_negative_implies_hold (TemporalBridge.lean) [CONFIRMED]
      ← canonicalize_preserves_nonneg [CONFIRMED]
      → [External Signals C463 Anti-Replay, C469 Stale Execution] [INFERRED — F04 specs]
```

## Branche Immutabilité / Merkle / Seal

```
SealAssumptions.combine_inj (CryptoAssumptions.lean) [CONFIRMED — axiomatisé]
  → foldl_H_injective [CONFIRMED]
  → merkle2_right_mutation [CONFIRMED]
  │
  └→ merkleRoot_change_if_leaf_change (Sensitivity.lean) [CONFIRMED]
       → P15_Immutability_Strong [CONFIRMED]
       │   → P13_Immutability (Seal.lean) [CONFIRMED]
       │       → [OS3ProofTicket trace_hash, merkle_root] [INFERRED]
       │       → [replay verifier — replay_status] [GAP — non implémenté]
       │
       → P17_SealSensitive (SystemModel.lean) [CONFIRMED]
```

## Branche Consensus / Fail-Closed

```
countDec def (Consensus.lean) [CONFIRMED]
  → aggregate4 def [CONFIRMED]
      → aggregate4_act [CONFIRMED]
      → aggregate4_fail_closed [CONFIRMED]
      │   → [DistributedX108 — N=3f+1] [CONFIRMED — TLA spec]
      │   → [consensus sous perte de quorum → BLOCK] [CONFIRMED]
      │
      → aggregate4_unanimous [CONFIRMED]
      → no_two_distinct_supermajorities_4 [CONFIRMED]
          → [sécurité Byzantine — pas deux décisions contradictoires] [CONFIRMED]
```

## Branche Audit / Système

```
P17_Determinism (SystemModel.lean) [CONFIRMED]
  → P17_AuditLastIsComputed [CONFIRMED]
      → P17_AuditGrowth [CONFIRMED]
          → [audit log croît — base replay] [INFERRED]
          → [OS3ProofTicket replay_status] [GAP — NOT_RUN actuel]
```

## Branche V18_7 — Noncircumvention Python

```
meet lattice ALLOW<HOLD<BLOCK (noncircumvention_checker.py) [CONFIRMED — PYTHON_TEST_ONLY]
  → gate_replay (nonce anti-replay) [CONFIRMED — PYTHON_TEST_ONLY]
  → gate_x108_timelock (irr ∧ elapsed<τ → HOLD) [CONFIRMED — PYTHON_TEST_ONLY]
  → gate_risk (risk > threshold → BLOCK) [CONFIRMED — PYTHON_TEST_ONLY]
  → 200k fuzz iterations PASS [CONFIRMED — PYTHON_TEST_ONLY, pas preuve formelle]
```

## Branche Périphéries — Non-souveraineté (PYTHON_TEST_ONLY)

```
KX108_ONLY (boundary contractuelle) [CONFIRMED — specs Plan 2]
  → No ACT from Sigma [CONFIRMED — Python tests PASS]
  → No ACT from Brody [CONFIRMED — Python tests PASS]
  → graphiti_write=False [CONFIRMED — Python tests PASS]
  → memory_write=False [CONFIRMED — Python tests PASS]
  → readonly=True dans Sigma [CONFIRMED — Python tests PASS]
  │
  → [Lyapunov stabilité] [GAP — PYTHON_SPEC, FORMAL_PROOF_PENDING]
  → [ProofOfGovernance] [GAP — PYTHON_SPEC, FORMAL_PROOF_PENDING]
  → [OS3ProofTicket sha256] [INFERRED — sha256, pas preuve Lean]
```

## Graphe central condensé

```
D1_DETERMINISM
    │
    ├──→ E2_NO_ACT_BELOW_THRESHOLD
    │         │
    │         ├──→ X108_NO_ACT_BEFORE_TAU ──→ X108_KERNEL_NEVER_BLOCKS
    │         │         │                          │
    │         │         ├──→ X108_AFTER_TAU_EQ_BASE│
    │         │         ├──→ skew_negative_HOLD    │
    │         │         └──→ [TLA SafetyX108]      │
    │         │                                    │
    │         └──→ Refinement.x108_never_blocks ←──┘
    │                   │
    │                   └──→ refined_not_block
    │
    ├──→ P17_DETERMINISM → P17_AuditGrowth → [replay base]
    │
SealAssumptions.combine_inj
    │
    ├──→ foldl_H_injective → merkleRoot_change
    │         │
    │         ├──→ P15_IMMUTABILITY_STRONG
    │         └──→ P13_IMMUTABILITY → [Seal/Replay]
    │
    └──→ merkle2_right_mutation → P13
    
aggregate4_FAIL_CLOSED ──→ [DistributedX108 N=3f+1]
    │
    └──→ no_two_distinct_supermajorities ──→ [Byzantine safety]

canonicalize_preserves_nonneg → skew_negative_implies_HOLD
```
