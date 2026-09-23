# RUNTIME_CONTRACTS_FILE_TREE
# runtime_contracts/
# Plan3 Freeze Audit — Arborescence complète
# Date: 2026-06-02
# Total: 109 fichiers — 0 .py — DOCS_ONLY

---

```
runtime_contracts/
│
├── README.md                                                   [P0 — entrypoint]
│
├── boundaries/                                                 [P0/P1 — 13 files]
│   ├── ATLAS_READONLY_ADVISORY_ONLY.md
│   ├── AUDIO_ENTROPY_ADVISORY_ONLY.md
│   ├── COGNITIVE_REINTEGRATION_ADVISORY_ONLY.md
│   ├── EXTERNAL_SIGNALS_SIGNAL_ONLY.md
│   ├── FAIL_CLOSED_PRIORITY.md
│   ├── NO_ACT_FROM_PERIPHERY.md
│   ├── NO_PACKAGES_RUNTIME_BOUNDARY.md
│   ├── NPL_ADVISORY_ONLY.md
│   ├── P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY.md
│   ├── READONLY_CONTEXT_ONLY.md
│   ├── RGPD_COMPLIANCE_SCOPE_GUARD.md
│   ├── RSSI_EVIDENCE_ONLY.md
│   └── X108_GATEWAY_REQUIRED.md
│
├── contracts/                                                  [P0 — 7 files]
│   ├── BoundaryContract.contract.md
│   ├── ContextPacket.contract.md
│   ├── DecisionTicket.contract.md
│   ├── IntentEnvelope.contract.md
│   ├── OS3EvidenceTicket.contract.md
│   ├── PeripheralSignalPacket.contract.md
│   └── RuntimeAdmissionContract.contract.md
│
├── dry_run/                                                    [P0 — 4 files]
│   ├── DRY_RUN_FAILURE_MODES.md
│   ├── DRY_RUN_PIPELINE.md
│   ├── NO_WORLD_ACTION_EXECUTION.md
│   └── X108_GATEWAY_DRY_RUN.md
│
├── schemas/                                                    [P1 — 7 files]
│   ├── boundary_contract.schema.json
│   ├── context_packet.schema.json
│   ├── decision_ticket.schema.json
│   ├── intent_envelope.schema.json
│   ├── os3_evidence_ticket.schema.json
│   ├── peripheral_signal_packet.schema.json
│   └── runtime_admission_contract.schema.json
│
├── reports/                                                    [P0+P1 — 7 files]
│   ├── PLAN3_P0_NEXT_STEPS.md
│   ├── PLAN3_P0_RUNTIME_CONTRACT_SKELETON_REPORT.md           [VERDICT: P0_READY]
│   ├── PLAN3_P0_SCOPE_VERIFICATION.md
│   ├── PLAN3_P1_NEXT_STEPS.md
│   ├── PLAN3_P1_PACKET_SCHEMA_VALIDATION_REPORT.md            [VERDICT: P1_READY]
│   ├── PLAN3_P1_SCOPE_VERIFICATION.md
│   └── PLAN3_P1_SPECIFIC_BOUNDARIES_REPORT.md
│
├── external_signals_dry_run/                                   [P2 — 8 files]
│   ├── failure_modes/
│   │   └── EXTERNAL_SIGNALS_FAILURE_MODES.md
│   ├── mapping/
│   │   └── EXTERNAL_SIGNALS_PACKET_TO_CONTRACT_MAP.md
│   ├── reports/
│   │   ├── PLAN3_P2_CORRECTION_VERIFICATION_REPORT.md         [VERDICT: P2C_READY]
│   │   ├── PLAN3_P2_EXTERNAL_SIGNALS_DRY_RUN_SPEC_REPORT.md  [VERDICT: P2_READY]
│   │   ├── PLAN3_P2_NEXT_STEPS.md
│   │   └── PLAN3_P2_SCOPE_VERIFICATION.md
│   └── specs/
│       ├── EXTERNAL_SIGNALS_DRY_RUN_ADAPTER_SPEC.md
│       └── EXTERNAL_SIGNALS_TO_X108_DRY_RUN_PIPELINE.md
│
├── x108_gateway_dry_run_harness/                               [P3 — 10 files]
│   ├── examples/
│   │   ├── EXAMPLE_BLOCKED_DRY_RUN_INTENT.md
│   │   ├── EXAMPLE_BLOCKED_SOURCE_PACK_IMPORT_ASSUMPTION.md
│   │   └── EXAMPLE_SAFE_DRY_RUN_INTENT.md
│   ├── failure_modes/
│   │   └── X108_GATEWAY_DRY_RUN_HARNESS_FAILURE_MODES.md
│   ├── mapping/
│   │   ├── CONTEXT_SIGNAL_EVIDENCE_BINDING_MAP.md
│   │   └── INTENT_TO_DECISION_TICKET_DRY_RUN_MAP.md
│   ├── reports/
│   │   ├── PLAN3_P3_NEXT_STEPS.md
│   │   ├── PLAN3_P3_SCOPE_VERIFICATION.md
│   │   └── PLAN3_P3_X108_GATEWAY_DRY_RUN_HARNESS_SPEC_REPORT.md  [VERDICT: P3_READY]
│   └── specs/
│       └── X108_GATEWAY_DRY_RUN_HARNESS_SPEC.md
│
├── anti_bypass_tests_spec/                                     [P4 — 8 files]
│   ├── ANTI_BYPASS_TESTS_SPEC.md
│   ├── failure_modes/
│   │   └── ANTI_BYPASS_FAILURE_MODES.md
│   ├── matrices/
│   │   ├── ANTI_BYPASS_TEST_MATRIX.md
│   │   └── SOURCE_PACK_BYPASS_MATRIX.md
│   ├── reports/
│   │   ├── PLAN3_P4_ANTI_BYPASS_TESTS_SPEC_REPORT.md          [VERDICT: P4_READY]
│   │   ├── PLAN3_P4_NEXT_STEPS.md
│   │   └── PLAN3_P4_SCOPE_VERIFICATION.md
│   └── scenarios/
│       └── BYPASS_SCENARIO_CATALOG.md
│
├── os3_evidence_dry_run/                                       [P5 — 11 files]
│   ├── examples/
│   │   ├── EXAMPLE_INVALID_PROOF_CLAIM_BLOCK.md
│   │   ├── EXAMPLE_MISSING_EVIDENCE_BLOCK.md
│   │   └── EXAMPLE_OS3_EVIDENCE_TICKET_THEORETICAL.md
│   ├── failure_modes/
│   │   └── OS3_EVIDENCE_FAILURE_MODES.md
│   ├── mapping/
│   │   ├── DECISION_TICKET_EVIDENCE_BINDING_MAP.md
│   │   └── EVIDENCE_SOURCE_TO_OS3_TICKET_MAP.md
│   ├── reports/
│   │   ├── PLAN3_P5_NEXT_STEPS.md
│   │   ├── PLAN3_P5_OS3_EVIDENCE_DRY_RUN_SPEC_REPORT.md       [VERDICT: P5_READY]
│   │   └── PLAN3_P5_SCOPE_VERIFICATION.md
│   └── specs/
│       ├── OS3_EVIDENCE_TICKET_DRY_RUN_SPEC.md
│       └── REPLAY_HASH_SEAL_MERKLE_PLACEHOLDER_MODEL.md
│
├── readonly_wrappers_spec/                                     [P6 — 14 files]
│   ├── examples/
│   │   ├── EXAMPLE_BLOCKED_READONLY_WRITE_ATTEMPT.md
│   │   ├── EXAMPLE_BRODY_CONTEXT_PACKET.md
│   │   ├── EXAMPLE_GRAPHITI_CONTEXT_PACKET.md
│   │   └── EXAMPLE_NPL_ADVISORY_CONTEXT_PACKET.md
│   ├── failure_modes/
│   │   └── READONLY_WRAPPER_FAILURE_MODES.md
│   ├── mapping/
│   │   ├── READONLY_SOURCE_TO_CONTEXTPACKET_MAP.md
│   │   └── WRAPPER_TO_BOUNDARY_MAP.md
│   ├── reports/
│   │   ├── PLAN3_P6_NEXT_STEPS.md
│   │   ├── PLAN3_P6_READONLY_WRAPPERS_SPEC_REPORT.md          [VERDICT: P6_READY]
│   │   └── PLAN3_P6_SCOPE_VERIFICATION.md
│   └── specs/
│       ├── BRODY_READONLY_WRAPPER_SPEC.md
│       ├── GRAPHITI_READONLY_WRAPPER_SPEC.md
│       ├── NPL_READONLY_WRAPPER_SPEC.md
│       └── READONLY_WRAPPERS_SPEC.md
│
├── education_benchmark_dry_run/                                [P7 — 19 files]
│   ├── anti_bypass/
│   │   └── ANTI_BYPASS_EDUCATION_SPEC.md
│   ├── boundary/
│   │   └── EDUCATION_BOUNDARY_SPEC.md
│   ├── examples/
│   │   └── EDUCATION_BENCHMARK_EXAMPLES.md
│   ├── failure_modes/
│   │   ├── EDUCATION_BENCHMARK_FAILURE_MODES.md               [canonical — 20 FM]
│   │   └── FAILURE_MODES_SPEC.md                              [initial — 10 FM]
│   ├── metrics/
│   │   └── EDUCATION_METRICS_CANDIDATE_SPEC.md
│   ├── os3/
│   │   └── OS3_EVIDENCE_EDUCATION_BINDING_SPEC.md
│   ├── pipeline/
│   │   └── EDUCATION_BENCHMARK_PIPELINE_SPEC.md
│   ├── reports/
│   │   ├── PLAN3_P7_EDUCATION_BENCHMARK_DRY_RUN_SPEC_REPORT.md [VERDICT: P7_READY]
│   │   ├── PLAN3_P7_FILE_RECONCILIATION_MAP.md
│   │   ├── PLAN3_P7_NEXT_STEPS.md
│   │   ├── PLAN3_P7_RECONCILIATION_PATCH_REPORT.md            [VERDICT: P7R_READY]
│   │   ├── PLAN3_P7_SCOPE_VERIFICATION.md
│   │   ├── REPORT_1_ARCHITECTURE.md                           [initial]
│   │   ├── REPORT_2_SCOPE_CHECK.md                            [initial]
│   │   └── REPORT_3_NEXT_STEPS.md                             [initial]
│   ├── scenarios/
│   │   ├── EDUCATION_BENCHMARK_SCENARIO_CATALOG.md            [canonical — 20 scén.]
│   │   └── EDUCATION_SCENARIOS_DRY_RUN.md                     [initial — 7 scén.]
│   └── specs/
│       └── EDUCATION_BENCHMARK_DRY_RUN_SPEC.md
│
└── freeze_audit/                                               [FREEZE_AUDIT — 7 files]
    ├── PLAN3_CLAIM_SCOPE_LOCKS.md
    ├── PLAN3_FILE_INVENTORY.md
    ├── PLAN3_FREEZE_AUDIT_REPORT.md
    ├── PLAN3_FREEZE_SCOPE_VERIFICATION.md
    ├── PLAN3_NEXT_PHASE_GATE.md
    └── PLAN3_READY_STATUS_MATRIX.md
```

---

## Statistiques

```
Total fichiers       : 109 (+ 7 freeze_audit = 116 après ce run)
Total dossiers       : 46
Fichiers .md         : 102
Fichiers .json       : 7
Fichiers .py         : 0
Fichiers exécutables : 0
Runtime actif        : NONE — DOCS_ONLY
```
