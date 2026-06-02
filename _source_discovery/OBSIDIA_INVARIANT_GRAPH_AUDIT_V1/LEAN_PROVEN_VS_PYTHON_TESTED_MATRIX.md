# LEAN_PROVEN_VS_PYTHON_TESTED_MATRIX
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

**Référence :** `external_pack/PROOF_INDEX.md` — audité le 2026-05-30

---

| # | Property | Lean proven | TLA spec present | Python tested | Doc only | Future formal target | Source |
|---|----------|------------|-----------------|---------------|----------|---------------------|--------|
| 1 | Déterminisme de la décision (D1) | ✅ `D1_determinism` | — | ✅ (implicit) | — | — | `Basic.lean` |
| 2 | No ACT en-dessous du seuil θ (E2) | ✅ `E2_no_act_below_threshold` | — | ✅ | — | — | `Basic.lean` |
| 3 | No ACT avant τ écoulé (irréversible) | ✅ `X108_no_act_before_tau` | ✅ `SafetyX108` | ✅ | — | — | `TemporalKernel.lean` + `X108.tla` |
| 4 | Kernel X108 après τ = base | ✅ `X108_after_tau_equals_base` | — | ✅ | — | — | `TemporalKernel.lean` |
| 5 | Kernel jamais BLOCK | ✅ `X108_kernel_never_blocks` | — | ✅ | — | — | `TemporalKernel.lean` |
| 6 | Réversible = base (indépendant de τ) | ✅ `X108_reversible_equals_base` | — | ✅ | — | — | `TemporalKernel.lean` |
| 7 | Irréversible après τ = base | ✅ `X108_irreversible_after_tau_equals_base` | — | ✅ | — | — | `TemporalKernel.lean` |
| 8 | Raffinement jamais BLOCK | ✅ `Refinement.x108_never_blocks` | — | ✅ | — | — | `Refinement.lean` |
| 9 | Raffinement correct (R_decision) | ✅ `Refinement.lift_refines` | — | — | — | — | `Refinement.lean` |
| 10 | Immutabilité Merkle (faible) — feuille change → racine change | ✅ `merkleRoot_change_if_leaf_change` | — | ✅ | — | — | `Sensitivity.lean` |
| 11 | Immutabilité Merkle forte (P15) — repo change → seal change | ✅ `P15_Immutability_Strong` | — | ✅ | — | — | `Sensitivity.lean` |
| 12 | Immutabilité Seal (P13) | ✅ `P13_Immutability` | — | ✅ | — | — | `Seal.lean` |
| 13 | Consensus fail-closed (pas quorum → BLOCK) | ✅ `aggregate4_fail_closed` | ✅ `DistributedX108.tla` | ✅ | — | — | `Consensus.lean` |
| 14 | Pas deux supermajorités distinctes | ✅ `no_two_distinct_supermajorities_4` | — | — | — | — | `Consensus.lean` |
| 15 | Canonicalisation non-négativité | ✅ `canonicalize_preserves_nonneg` | — | ✅ | — | — | `TemporalBridge.lean` |
| 16 | Skew négatif → HOLD | ✅ `skew_negative_implies_hold` | — | ✅ | — | — | `TemporalBridge.lean` |
| 17 | Déterminisme système (P17) | ✅ `P17_Determinism` | — | ✅ | — | — | `SystemModel.lean` |
| 18 | Audit log croît (P17_AuditGrowth) | ✅ `P17_AuditGrowth` | — | ✅ | — | — | `SystemModel.lean` |
| 19 | Kernel institutionnel jamais BLOCK | ✅ `P17_KernelNeverBlocks` | — | ✅ | — | — | `SystemModel.lean` |
| 20 | Noncircumvention V18_7 (lattice, 200k) | ❌ | — | ✅ (fuzz) | — | ✅ (Lean formel futur) | `noncircumvention_checker.py` |
| 21 | TLA SafetyX108 □(irr∧elapsed<τ → ¬ACT) | — | ✅ spec présente | — | — | ⚠️ TLC non relancé | `formal/tla/X108.tla` |
| 22 | TLA Distributed consensus | — | ✅ spec présente | — | — | ⚠️ TLC non relancé | `formal/tla/DistributedX108.tla` |
| 23 | Sigma KX108_ONLY | ❌ Lean | — | ✅ 650+ tests | — | ✅ | `tests/sigma/test_f62_*.py` |
| 24 | Brody No-ACT | ❌ Lean | — | ✅ | — | ✅ | `tests/api/test_brody_authority_escalation_no_act.py` |
| 25 | Graphiti write isolation (graphiti_write=False) | ❌ Lean | — | ✅ | — | ✅ | `tests/sigma/test_f70_*.py` |
| 26 | Memory write isolation (memory_write=False) | ❌ Lean | — | ✅ | — | ✅ | `tests/api/test_no_memory_write_api.py` |
| 27 | Lyapunov stabilité | ❌ Lean | — | ❌ test direct | ✅ Python spec | ✅ PRIORITAIRE | `periphery/math_core/lyapunov.py` |
| 28 | ProofOfGovernance | ❌ Lean | — | ❌ test direct | ✅ Python spec | ✅ PRIORITAIRE | `periphery/math_core/proof_of_governance.py` |
| 29 | P161 energetic calibration | ❌ | — | — | ✅ | ✅ | `docs/` — à localiser |
| 30 | OS3ProofTicket sha256 chain | ❌ Lean | — | ✅ (intégration) | — | ✅ | `periphery/os3_ticket.py` |
| 31 | RFC3161 timestamps | — | ✅ spec présente | ✅ (openssl verify — non relancé) | — | ⚠️ | `formal/tla/RFC3161Spec.tla` |

---

## Légende

| Symbole | Signification |
|---------|--------------|
| ✅ | Présent et confirmé |
| ❌ | Absent pour ce type |
| ⚠️ | Présent mais non vérifié actuellement |
| — | Non applicable |

---

## Observations clés

**Ce qui est solidement LEAN_PROVEN (kernel X108) :**
Propriétés 1-19 — Le cœur temporel, le raffinement, l'immutabilité Merkle/Seal, et le consensus sont prouvés formellement en Lean 4.

**Ce qui est PYTHON_TEST_ONLY (périphéries) :**
Propriétés 23-26 — Non-souveraineté de Sigma, Brody, Graphiti : validés par tests Python, pas par preuves Lean.

**Ce qui est FORMAL_PROOF_PENDING (specs Python en attente) :**
Propriétés 27-28 — Lyapunov et ProofOfGovernance : spécifications Python, pas de Lean proof.

**Ce qui est TLA_VERIFIED_CURRENTLY_UNKNOWN :**
Propriétés 21-22, 31 — TLC n'a pas été relancé dans cette session.
