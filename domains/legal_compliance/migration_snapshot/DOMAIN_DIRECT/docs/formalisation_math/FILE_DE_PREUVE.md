# FILE DE FORMALISATION ET DE PREUVE — V3.2
**Source :** `V3_2_ACTIONABLE_ARCHITECTURE_GUIDE/08_FORMALIZATION_AND_PROOF_QUEUE.md` (2026-06-21)  
**Règle absolue : ne jamais compiler avec `sorry`. Un théorème incomplet reste TO_PROVE.**

```
ALREADY_PROVEN      = prouvé formellement (Lean compile sans sorry)
TO_FORMALIZE        = concept mathématique solide, pas encore en Lean/TLA
TO_PROVE            = formulation Lean proposée, à écrire et valider
TO_TEST_LATER       = logique testée en code, pas en preuve formelle
TO_KEEP_AS_RESEARCH = idée intéressante, pas mûre
DO_NOT_PROVE_NOW    = intentionnellement différé
```

---

## SECTION 1 — DÉJÀ PROUVÉ (ALREADY_PROVEN)

| ID | Concept | Fichier Lean | Statut | Règle |
|---|---|---|---|---|
| AP-01 | Lean proofs V18_3_1 (ensemble) | `proofs/V18_3_1/` | PASS sans sorry | DO_NOT_TOUCH |
| AP-02 | Lean proofs V18_7 (ensemble) | `proofs/V18_7/` | PASS sans sorry | DO_NOT_TOUCH |
| AP-03 | Lean proofs V18_8 (ensemble) | `proofs/V18_8/` | PASS sans sorry | DO_NOT_TOUCH |
| AP-04 | BLOCK > HOLD > ALLOW — invariant | Lean 57 existants | EXISTS_CONFIRMED | Ne jamais inverser |
| AP-05 | Lyapunov dL/dt ≤ 0 — stabilité | Lean 57 existants | EXISTS_CONFIRMED | DO_NOT_TOUCH |
| AP-06 | PoG(x) — proof of governance | Lean 57 existants | EXISTS_CONFIRMED | DO_NOT_TOUCH |
| AP-07 | G5 — scrub_secret_token_sequence | sigma/ tests 15/15 | RESOLVED | Ne pas réouvrir |
| AP-08 | TOP4 (V1/V2/V3/V4) | sigma/ tests PASS | RESOLVED | Ne pas réouvrir sans régression |

---

## SECTION 2 — À FORMALISER MATHÉMATIQUEMENT (TO_FORMALIZE)

11 concepts avec structure mathématique identifiée en V3. Doivent être exprimés formellement avant Lean.

| ID | Concept | Structure math | Fichier cible | Priorité | Couche |
|---|---|---|---|---|---|
| TF-01 | TrajectoryState | `{past_trace, current_state, intended_action, projected_future}` | `kernel/trajectory_state.py` | P4 | KERNEL_X108 |
| TF-02 | TLS — Temporal Legitimacy Score | `{past_coherence, present_stability, future_risk, irreversibility_weight, proof_readiness}` ∈ [0,1]^5 | `kernel/tls_score.py` | P4 | KERNEL_X108 |
| TF-03 | Gardien Amont — IR/CIZ/ΔTSG | `IR(C)=0 ∧ CIZ(C)=0 ∧ ΔTSG(C)<0 → ADMIT_PATH \| REFUSE_PATH \| ESCALATE` | `kernel/gardien_amont.py` | P4 | KERNEL_X108 |
| TF-04 | RPL_X108 — pipeline claim | `candidate → upper-bound → underdetermined → restricted → blocked → rejected → admissible` | `kernel/rpl_x108.py` | P4 | KERNEL_X108 |
| TF-05 | RULE_NPL_001-006 | 6 règles de provenance narrative — NO_ACT invariant | `research/npl/rules_formalization.py` | P7 | NPL_NARRATIVE_PROVENANCE |
| TF-06 | Temporal Action Authority Layer | `Plan valid ≠ Action authorized — INVARIANT_AGENTIC_CODE_AUTHORITY_001` | `kernel/temporal_action_authority_layer.py` | P4 | KERNEL_X108 |
| TF-07 | Thermodynamic Path Engine — 6 coûts | `{latency_cost, memory_cost, token_cost, proof_cost, entropy_score, dissipation_score}` | `research/thermo/path_compute_v0.py` | P7 | THERMO_PATH_ENGINE |
| TF-08 | LOI_DE_FERTILITÉ_PAR_FRICTION | `CONTRAINTE→FRICTION→RYTHME→FORME→FREEZE — FFS states` | `research/friction_law.py` | P7 | THERMO_PATH_ENGINE |
| TF-09 | Lyapunov étendu V3 | `L(x) = α·ΔE + β·ΔC + γ·V_inst + δ·Δτ + η·I_ctrl — pondération à confirmer` | `proofs/lyapunov_ext_v3.lean` | P4 | LEAN_TLA_PROOF |
| TF-10 | X108_READONLY_CONTEXT_CANDIDATE | Conditions d'admission comme contexte kernel readonly | `memory/readonly_context.py` | P5 | GRAPHITI_MEMORY |
| TF-11 | GuardX108 seuils — justification formelle | `min_confidence_allow=0.72, hold_floor=0.45, max_unknowns=1, max_contradictions=2` | `kernel/guard_x108_proof.lean` | P4 | KERNEL_X108 |

---

## SECTION 3 — À PROUVER EN LEAN (TO_PROVE)

7 théorèmes identifiés en V3. Formulations pseudo-Lean indicatives.

**Ordre suggéré :** TP-03 et TP-04 → TP-01 → TP-05 → TP-02, TP-06, TP-07.

| ID | Théorème | Formulation pseudo-Lean | Fichier cible | Priorité | Dépend de |
|---|---|---|---|---|---|
| TP-01 | Faithful Path Existence | `theorem faithful_path_exists (ctx : Context) (h : IR(ctx)=0 ∧ CIZ(ctx)=0 ∧ ΔTSG(ctx)<0) : ∃ path, PathAdmission(path) = ADMIT_PATH` | `proofs/lean_theorem_faithful_path.lean` | P4 | TF-03 + D13+D14 |
| TP-02 | Pre-Cognitive Elimination | `theorem pre_cognitive_elimination (θ : State) (h : J_Θ(θ) ∉ Ω) : ∀ action, Authorized(action, θ) = false` | `proofs/lean_theorem_pre_cognitive.lean` | P4 | D14 |
| TP-03 | Memory Non-Sovereignty | `theorem memory_not_sovereign (m : Memory) : ∀ decision, Decision(decision) ≠ Authority(m)` | `proofs/lean_theorem_memory_non_sovereign.lean` | P4 | Lean 57 + D13 |
| TP-04 | HOLD Preservation | `theorem hold_preserved (x : State) (h : HOLD(x)) : ∀ t, t > 0 → ¬ACT_without_X108(x, t)` | `proofs/lean_theorem_hold_preservation.lean` | P4 | Lean 57 + D13 |
| TP-05 | Stability Before Action | `theorem stability_before_action (x : State) (h : dL_dt(x) > 0) : ∀ action, Authorized(action, x) = false` | `proofs/lean_theorem_stability_before_action.lean` | P4 | TF-09 + D14 |
| TP-06 | Order Error Prevention | `theorem order_error_prevented (seq : ActionSequence) (h : ¬ValidOrder(seq)) : X108_blocks(seq)` | `proofs/lean_theorem_order_error_prevention.lean` | P4 | TP-01→TP-04 + D14 |
| TP-07 | External Input Non-Sovereignty | `theorem ext_input_not_sovereign (input : ExternalInput) : ∀ decision, Decision(decision) ≠ Authority(input)` | `proofs/lean_theorem_ext_input_non_sovereign.lean` | P4 | TP-01→TP-05 + D14 |

---

## SECTION 4 — À TESTER EN CODE (TO_TEST_LATER)

| ID | Concept | Test cible | Priorité | Couche |
|---|---|---|---|---|
| TT-01 | SRL Session Registry Layer (5 états) | `memory/test_srl.py` | P5 | GRAPHITI_MEMORY |
| TT-02 | BrodyDisclosureGuard (4 filtres) | `brody/test_disclosure_guard.py` | P6 | BRODY |
| TT-03 | Nuisance Registry Bank/Trading/GPS | `domains/*/test_nuisance_registry.py` | P3 | DOMAIN_* |
| TT-04 | Bank/Trading/GPS x108 gates | `domains/*/test_x108_gate.py` | P3 | DOMAIN_* |
| TT-05 | ChatView.tsx POST | test UI Workbench | P2 | OS4_INTERFACE |
| TT-06 | Agentic Security Panel | `cockpit/test_agentic_panel.py` | P2 | COCKPIT |
| TT-07 | RSSI_COCKPIT (RSSI/RGPD/ISO) | `cockpit/test_rssi_cockpit.py` | P2 | COCKPIT |
| TT-08 | MEMORY_CONTEXT_GUARD | `memory/test_context_guard.py` | P4 | GRAPHITI_MEMORY |
| TT-09 | CodeAuthorizationGate (TEST_PASS ≠ AUTHORIZED) | `kernel/test_code_auth_gate.py` | P4 | KERNEL_X108 |
| TT-10 | P56-P69 audit plans (boundary/auth/filesystem/network) | `sigma/test_p56_p69.py` | P1 | SIGMA |

---

## SECTION 5 — GARDER EN RECHERCHE (TO_KEEP_AS_RESEARCH)

| ID | Concept | Raison du report |
|---|---|---|
| KR-01 | SGS-X108 sandbox loop (Conjecturer→Solver→Guide→Verifier→X108) | AutoForge réservé — D23 |
| KR-02 | Physical Signal World Model | Domaine non créé |
| KR-03 | Spiral-Time Governor | Référence robotique — non intégrée |
| KR-04 | Krüger OFG/RPL analogues | Inspiré — partiellement mappé |
| KR-05 | Gencoin V(x)∝1/(L(x)+ε) | Modèle économique — DO_NOT_PROMOTE — D27 |
| KR-06 | AutoGenesis / AutoForge | Réservé — ne pas déployer — D29 |
| KR-07 | Combinatorial Coverage Layer full | Si D07=TO_DEFER — D30 |

---

## SECTION 6 — NE PAS PROUVER MAINTENANT (DO_NOT_PROVE_NOW)

| ID | Concept | Condition de levée |
|---|---|---|
| DNP-01 | PoG étendu avec TLS | TF-02 + TF-03 créés d'abord |
| DNP-02 | Lean sur NPL RULE_NPL_001-006 | D21=TO_CREATE + N01-N04 créés |
| DNP-03 | Lean sur Thermo Path Engine | D22=TO_CREATE + TF-07 formalisé |
| DNP-04 | Lean sur Combinatorial Coverage | D07 décidé + structure créée |
| DNP-05 | Lean sur ExternalAgentProfile | D10 décidé + implémentation complète |

---

## TABLEAU DE BORD

| Catégorie | Nombre |
|---|---|
| ALREADY_PROVEN (Lean) | 57 preuves + 8 refs |
| TO_FORMALIZE | 11 concepts |
| TO_PROVE (nouveaux théorèmes Lean) | 7 théorèmes |
| TO_TEST_LATER | 10 items |
| TO_KEEP_AS_RESEARCH | 7 concepts |
| DO_NOT_PROVE_NOW | 5 items |
| **Total identifiés** | **98+** |
