# Obsidia Branching Matrix Draft V0

Mode: READ_ONLY source audit; generated as a draft routing matrix. No runtime files were modified.

## Files
- CSV: `docs/audits/OBSIDIA_BRANCHING_MATRIX_DRAFT_V0.csv`
- Rows: 6155
- PDF named paths detected: 116
- Missing named actionable paths: 103

## Target Layer Counts

| Layer | Count |
|---|---:|
| DOCS | 3967 |
| RUNTIME_WIRING | 679 |
| BRODY | 495 |
| KERNEL | 486 |
| TOOLING | 263 |
| OBSIDURE | 162 |
| SIGMA | 82 |
| CONNECTORS | 15 |
| AGENTIC | 6 |

## Destination Status Counts

| Status | Count |
|---|---:|
| REFERENCE_ONLY | 1768 |
| DOCS_ONLY | 929 |
| ARCHIVE_OR_REFERENCE | 826 |
| SOURCE_CONTEXT_ONLY | 676 |
| ACTIVE_READONLY_PARTIAL | 466 |
| PROTECTED_PROTECTED_CANON_OR_EVIDENCE | 289 |
| SPEC_IMPORTED | 217 |
| REFERENCE_MATH_MEMORY | 162 |
| PROOF_SANDBOX | 152 |
| API_ACTIVE_OR_STUB | 123 |
| MISSING_NAMED_ACTIONABLE | 103 |
| SIGMA_LAYER | 79 |
| UI_SURFACE | 72 |
| PROTECTED_DOCS_ONLY | 71 |
| ACTIVE_DRY_RUN | 62 |
| ARCHIVE_ONLY | 54 |
| PROTECTED_REFERENCE_ONLY | 32 |
| PROTECTED_ACTIVE_READONLY_PARTIAL | 29 |
| PROTECTED_CANON_OR_EVIDENCE | 19 |
| STATIC_OR_DEMO_CONNECTOR | 8 |
| DOMAIN_GATE_LAYER | 6 |
| PROTECTED_API_ACTIVE_OR_STUB | 3 |
| PROTECTED_SOURCE_CONTEXT_ONLY | 3 |
| PROTECTED_SPEC_IMPORTED | 3 |
| SCHEMA_LAYER | 2 |
| PROTECTED_SIGMA_LAYER | 1 |

## Source Pack Counts

| Source pack | Count |
|---|---:|
| repo_tracked | 3738 |
| OBSIDIA_V4_STRUCTURED_FULL | 826 |
| MMONDE_OS_TRAD_34_ARBRES | 679 |
| BRODY_MEMORY_READONLY | 495 |
| PEPITES | 162 |
| LEAN_SANDBOX | 152 |
| PDF_CHECKLIST | 103 |

## Priority Branching Queue

1. Stabilize `BRODY_MEMORY_READONLY` entrypoints already called by `apps/obsidia_api`.
2. Route `MMONDE_OS_TRAD_34_ARBRES` through `runtime_wiring` as context-only, excluding Python runtime imports.
3. Integrate clean spec packs into `specs/*`, especially cognitive/external-signal style content.
4. Reconcile `memory/*` PDF targets with existing `periphery/memory/*` before creating wrappers.
5. Complete Sigma F67/F68 from the existing F66 readonly pattern.
6. Treat `kernel/*` missing targets as a separate high-risk proposal; no direct creation without proof/risk plan.
7. Keep archives/freezes/legacy as evidence only; do not mix into active runtime.

## Missing Named Actionables By Layer

### AGENTIC (6)
- `memory/context_compression_proxy_v1.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]
- `memory/fidelity_registry.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]
- `memory/memory_context_guard.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]
- `memory/readonly_context.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]
- `memory/srl_session_registry.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]
- `memory/x108_readonly_context_candidate.py` -> RECONCILE_WITH_PERIPHERY_MEMORY_OR_CREATE_WRAPPER [LOW]

### CONNECTORS (1)
- `domains/ecom/build_ecom_agents.py` -> VERIFY_CONNECTED_FROM_CONNECTORS_AND_API [LOW]

### DOCS (65)
- `docs/CARTE_IDENTIFICATION_CAUSALE_SPEC.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/CENTRAL_RULES.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/DECISIONAL_FORM_LAYER_SPEC.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/DOMAIN_CALIBRATION_GUIDE.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/BENCH_LANG.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/CODE_SOVEREIGNTY_LEVEL.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/DISPOSABLE_CODE_RECEIPT.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/EPHEMERAL_CODE_SANDBOX.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/MEMORY_ATTESTATION_ONLY.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/PATH_FIDELITY_GUARD.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/PREDICT_UNDERSTAND_DECIDE_ACT.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/REASONING_BOUNDARY.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/SGS_X108_GOVERNED_SELF_PLAY.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/concepts/WORLD_PROTOCOL_ATLAS_PROTOCOL_TYPES.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/governance/DO_NOT_DO_AGENTS.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/governance/DO_NOT_DO_NPL.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/governance/DO_NOT_DO_STRATEGIC.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/paliers/P56_P60_SECURITY_AUDIT_PLAN.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/AI_ACTION_SOVEREIGNTY_SPEC.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/BANK_ACTION_GOVERNANCE_DEMO.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/COMPETITIVE_CONVERGENCE_MAP_V1.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/COMPETITIVE_LANDSCAPE_17_ACTORS.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/CORE_MESSAGES_FROZEN.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/FICHE_PILOTE_FLOW_CRITIQUE.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- `docs/product/FLOW_CATALOG_AGENTIC_B2B.md` -> INDEX_AS_EVIDENCE_OR_BRANCHING_GUIDE [LOW]
- ... 40 more in CSV

### KERNEL (26)
- `kernel/agentic_decision_envelope.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/agentic_security_layer_v0.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/claim_state_machine.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/code_authorization_gate.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/decision_path_guard.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/entropy_hold_rule.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/gardien_amont.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/path_admission.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/pre_action_authorization_gate.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/rpl_x108.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/runtime_behavior_gate.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/signed_decision_receipt.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/temporal_action_authority_layer.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/temporal_policy_layer.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/temporal_zero_trust.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/tls_score.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/trajectory_state.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/trust_boundary_checker.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `kernel/watchtower_observer.py` -> PROPOSE_KERNEL_FILE_BEFORE_CREATE [HIGH]
- `proofs/lean_theorem_external_input_non_sovereignty.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- `proofs/lean_theorem_faithful_path_existence.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- `proofs/lean_theorem_hold_preservation.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- `proofs/lean_theorem_memory_non_sovereignty.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- `proofs/lean_theorem_order_error_prevention.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- `proofs/lean_theorem_pre_cognitive_elimination.lean` -> PROOF_SENTINEL_PROPOSAL_NEW_LEAN_FILE_ONLY [HIGH]
- ... 1 more in CSV

### SIGMA (2)
- `sigma/final_freeze_f68.py` -> CREATE_SIGMA_F67_F68_FROM_F66_PATTERN [HIGH]
- `sigma/live_smoke_f67.py` -> CREATE_SIGMA_F67_F68_FROM_F66_PATTERN [LOW]

### TOOLING (3)
- `cockpit/agentic_security_panel.py` -> CREATE_UI_COCKPIT_SURFACE_AFTER_API_STATUS [LOW]
- `cockpit/combinatorial_panel.py` -> CREATE_UI_COCKPIT_SURFACE_AFTER_API_STATUS [LOW]
- `cockpit/rssi_cockpit.py` -> CREATE_UI_COCKPIT_SURFACE_AFTER_API_STATUS [LOW]

## Notes

- `protected_scope_candidate=true` is conservative: names containing root/seal/hash/anchor/freeze are flagged.
- The matrix is a routing draft, not an approval to edit protected or kernel files.
- Source PDFs are messy; rows with `PDF_CHECKLIST` need human confirmation before creation.
