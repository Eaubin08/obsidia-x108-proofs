# INVARIANT_TO_LAYER_MAP
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

| Layer | Invariants requis | Sources | Statut | Preuve manquante |
|-------|------------------|---------|--------|-----------------|
| **OS0 kernel** | D1_determinism, E2_no_act_below_threshold, decision_eq_ACT_iff | `Basic.lean` | LEAN_PROVEN | Aucune — complet |
| **OS1 temporal** | X108_no_act_before_tau, X108_after_tau_equals_base, X108_kernel_never_blocks, X108_reversible_equals_base, X108_irreversible_after_tau_equals_base | `TemporalKernel.lean` | LEAN_PROVEN | Aucune — complet |
| **OS1 bridge** | canonicalize_preserves_nonneg, skew_negative_implies_hold | `TemporalBridge.lean` | LEAN_PROVEN | Aucune |
| **OS2 refinement** | Refinement.x108_never_blocks, Refinement.lift_refines, Refinement.refined_not_block | `Refinement.lean` | LEAN_PROVEN | Aucune |
| **OS2 system model** | P17_Determinism, P17_AuditGrowth, P17_AuditLastIsComputed, P17_KernelNeverBlocks | `SystemModel.lean` | LEAN_PROVEN | Aucune |
| **OS3 Merkle/Seal** | P13_Immutability, P15_Immutability_Strong, merkleRoot_change, merkle2_right_mutation, foldl_H_injective, SealAssumptions.combine_inj | `Seal.lean`, `Sensitivity.lean`, `Merkle.lean`, `CryptoAssumptions.lean` | LEAN_PROVEN (sous axiome crypto) | Hypothèse combine_inj = axiome — pas preuve de collision resistance SHA |
| **OS3 Consensus** | aggregate4_fail_closed, aggregate4_unanimous, no_two_distinct_supermajorities_4, TLA SafetyX108 | `Consensus.lean`, `formal/tla/X108.tla` | LEAN_PROVEN + FORMAL_TLA_SPEC | TLC non relancé — TLA_VERIFIED_CURRENTLY_UNKNOWN |
| **OS3 Proof/Replay** | P17_AuditGrowth, OS3ProofTicket sha256 | `SystemModel.lean`, `periphery/os3_ticket.py` | LEAN_PROVEN (audit) + PYTHON_SPEC (ticket) | replay_status = NOT_RUN — à implémenter |
| **OS4 Interface** | [KX108_ONLY boundary contractuelle] | `specs/01_X108_AUTHORITY/` | SPEC_ONLY — PYTHON_TEST_ONLY | Pas de Lean proof pour l'interface API |
| **Sigma** | KX108_ONLY, No ACT from Sigma, readonly=True | `tests/sigma/test_f62_*.py`, `tests/sigma/test_f73_*.py` | PYTHON_TEST_ONLY | Lean proof non existant pour Sigma layer |
| **Bus** | KX108_ONLY, sovereignty | `tests/api/test_f65_*.py` | PYTHON_TEST_ONLY | Lean proof non existant |
| **Brody** | No-ACT, memory_write=False, readonly | `tests/api/test_brody_*.py` | PYTHON_TEST_ONLY | Lean proof non existant |
| **Graphiti** | graphiti_write=False, readonly | `tests/sigma/test_f70_*.py` | PYTHON_TEST_ONLY | Lean proof non existant |
| **Tree34** | non_decision_contract (Tree34 ↛ ACT) | `ARBRE_*/non_decision_contract.md` | DOC_ONLY | Pas de Lean ni Python test pour Tree34 |
| **Agents 52** | AgentPeripheral ↛ ACT, non_decision_contract | `agents_52.registry.json` | SOURCE_CANON (registry) | Pas de test exécutable par agent |
| **Balance/BUV** | Balance pèse, Balance ↛ ALLOW/HOLD/BLOCK | `periphery/gencoin_sandbox/balance_operator.py` | PYTHON_SPEC | FORMAL_PROOF_PENDING |
| **Gencoin** | mint_allowed=False si ¬X108_ALLOW, token_policy BLOCK | `periphery/gencoin.py`, `periphery/blockchain/token_policy.py` | RUNTIME_CODE | Lean proof du ledger non existant |
| **GPS** | GPS ↛ ACT, proposed_verdict only, DRY_RUN | `specs/09_CRITICAL_WORLDS/GPS_NO_ACT_WITHOUT_DECISIONTICKET.md` | SPEC_ONLY + DRY_RUN | Pas de test défense réel |
| **NPL** | PERIPHERAL_READONLY, NO_ACT, NO_VERDICT_FINAL | `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_CANONICAL_SPEC.md` | SPEC_CANDIDATE | Tout à implémenter — récepteurs existent |
| **External Signals** | SIGNAL_ONLY, NO_ACT, skew_negative_implies_hold | `specs/external_signals/F04_EXTERNAL_SIGNALS_BOUNDARY.md` | SPEC_CANDIDATE (F04 importé) | Adapters non créés — C473 non-réautorisation à tester |
