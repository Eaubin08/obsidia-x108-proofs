# XLSX_PLAN_SUMMARY

## Source
`OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx`

## Sheets detected
| Sheet | Rows |
|-------|------|
| README | 6 |
| SUMMARY | 6 |
| IMPLEMENT_ORDER | 12 |
| FILE_PLAN_ALL | 2740 |
| EXT_SIGNALS | 42 |
| RSSI_SECURITY | 168 |
| COGNITIVE | 514 |
| ATLAS | 1739 |
| RGPD_ISO | 281 |
| ACTION_COUNTS | 44 |

## SUMMARY sheet
| Pack | Source zip | Files | Size KB | SHA256 | Canonical role | Integration stage | Runtime status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EXTERNAL_SIGNALS | OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1(2).zip | 41 | 57.2 | f08ccd6446db616989ef30c8973d5d7f238449b1fa48bf9b4d9c4e1668a3898b | Temporal sidecar / anti-replay / bounded tool-call signals | F04 after authority + audit, before memory/action adapters | Backlog/spec/evidence unless explicitly wired through X108 |
| RSSI_SECURITY | OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1(2).zip | 167 | 445.4 | d1690bce3edcc342f846d0f04ba733b5654c0ed491f37048c67fb280ba6bd4d5 | RSSI security posture, audit narrative, controls, evidence | F03 early OS3 audit/security surface | Backlog/spec/evidence unless explicitly wired through X108 |
| COGNITIVE_REINTEGRATION | OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1)(2).zip | 513 | 827.9 | 7e8308f50e7212b1a4864a1f60ebf7dcbac3cd542cd4a861b4ef61b005a98fa0 | Cognitive components, packets, schemas, metrics, invariants | F07 after memory/atlas boundaries | Backlog/spec/evidence unless explicitly wired through X108 |
| BRANCHABLE_ATLAS | OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS(2).zip | 1738 | 4104.9 | 69d9352ea4a1ae8679bb8663c4e168135aa048976e63bd94a2945cef6f439850 | World/protocol atlas, branchable contexts, Graphiti-ready content | F06 after Graphiti/Brody readonly | Backlog/spec/evidence unless explicitly wired through X108 |
| RGPD_ISO | OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2(1).zip | 280 | 783.5 | 319706db7a2284190286cbd9fcfee03d81cc71c636f357a0324f5290714ce2ef | RGPD / ISO / RSSI readiness and compliance evidence | F03/F10 OS3 compliance readiness + external presentation | Backlog/spec/evidence unless explicitly wired through X108 |

## IMPLEMENT_ORDER (F00-F10)
| Stage | Name | Purpose | Inputs | Outputs | Gate/Boundary | Done when |
| --- | --- | --- | --- | --- | --- | --- |
| F00 | SOURCE FREEZE + LEDGER | Fix origin, hash, no-dedupe ambiguity | 5 canonical zips | SOURCE_PACKS_CANON.md, PACK_INDEX.json | No runtime import | Every file has source_zip + target_location |
| F01 | AUTHORITY CONTRACTS | Lock X108/KX108_ONLY before integration | DecisionTicket, IntentEnvelope, ContextPacket | shared contracts | No peripheral ACT | All packs map to packets/boundaries |
| F02 | CENTRAL REGISTRY | Make 2700+ files tractable | File-level plan | modules/packets/metrics/boundary registries | Registry cannot decide | Every row has OS layer + priority + test |
| F03 | OS3 SECURITY/RGPD/ISO | Install proof/compliance surface early | RSSI Security + RGPD ISO packs | control/risk/evidence/readiness registries | Docs/evidence only | Boundary/no-mutation tests pass |
| F04 | EXTERNAL SIGNALS | Temporal proof, anti-replay, bounded tool-calls | External Signals Patch | temporal packets + prefilters + tests | Signal only, X108 final | No stale/replayed/float-temporal path reaches action |
| F05 | MEMORY READONLY | Connect Graphiti/Brody as context, not authority | Graphiti/Brody + readonly context | ContextPacket exports | memory_decision=false | Memory produces no ACT/verdict |
| F06 | BRANCHABLE ATLAS | Create territory/maps/domains/scenarios | Atlas pack | Atlas registry + Graphiti nodes | Atlas context only | Atlas readonly tests pass |
| F07 | COGNITIVE REINTEGRATION | Import cognitive body as advisory components | Cognitive pack | component specs, packets, metrics | Advisory only | No agent/component emits ACT |
| F08 | NPL PROVENANCE | Add cultural/narrative provenance layer | NPL specs from 3 sources | HumanLogic/NarrativeProvenance packets | Readonly, no truth verdict | NPL never outputs final verdict |
| F09 | EDUCATION VERTICAL | First impact vertical and testbed | Cognition + NPL + memory | student blockage packets, learning reconstruction | No diagnosis/manipulation | Bench cases run vs baseline |
| F10 | BENCHMARKS + DEMO | Quantify and publish | All stable layers | replay reports, public demos, RSSI/education views | Demo cannot bypass kernel | Results reproducible and limits stated |

## ACTION_COUNTS (all)
| Pack | Implementation action | Priority | Files |
| --- | --- | --- | --- |
| BRANCHABLE_ATLAS | IMPORT_AS_REGISTRY_OR_EVIDENCE_AFTER_SCHEMA_CHECK | P4_ATLAS_EVIDENCE_OR_DOCS | 3 |
| BRANCHABLE_ATLAS | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P2_ATLAS_BRANCHING | 3 |
| BRANCHABLE_ATLAS | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P3_ATLAS_CONTENT | 878 |
| BRANCHABLE_ATLAS | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P4_ATLAS_EVIDENCE_OR_DOCS | 764 |
| BRANCHABLE_ATLAS | IMPORT_TESTS_READONLY_THEN_WIRE_TO_REAL_PATHS | P4_ATLAS_EVIDENCE_OR_DOCS | 2 |
| BRANCHABLE_ATLAS | KEEP_AS_EVIDENCE | P2_ATLAS_BRANCHING | 1 |
| BRANCHABLE_ATLAS | KEEP_AS_EVIDENCE | P4_ATLAS_EVIDENCE_OR_DOCS | 45 |
| BRANCHABLE_ATLAS | MANUAL_REVIEW_THEN_ADAPTER_BRANCH | P2_ATLAS_BRANCHING | 15 |
| BRANCHABLE_ATLAS | MERGE_INTO_REGISTRY | P2_ATLAS_BRANCHING | 7 |
| BRANCHABLE_ATLAS | QUARANTINE_DO_NOT_IMPLEMENT | P5_QUARANTINE | 20 |
| COGNITIVE_REINTEGRATION | IMPORT_AS_PROOF_SURFACE | P2_COGNITION_CONTRACTS | 1 |
| COGNITIVE_REINTEGRATION | IMPORT_CONTRACT_SCHEMA_PACKET | P1_CONTRACTS | 13 |
| COGNITIVE_REINTEGRATION | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P1_CONTRACTS | 3 |
| COGNITIVE_REINTEGRATION | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P2_COGNITION_CONTRACTS | 7 |
| COGNITIVE_REINTEGRATION | IMPORT_TESTS_READONLY_THEN_WIRE_TO_REAL_PATHS | P2_COGNITION_CONTRACTS | 1 |
| COGNITIVE_REINTEGRATION | KEEP_AS_EVIDENCE | P2_COGNITION_CONTRACTS | 2 |
| COGNITIVE_REINTEGRATION | MERGE_INTO_REGISTRY_OR_METRICS | P2_COGNITION_CONTRACTS | 3 |
| COGNITIVE_REINTEGRATION | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED | P1_CONTRACTS | 7 |
| COGNITIVE_REINTEGRATION | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED | P2_COGNITION_CONTRACTS | 25 |
| COGNITIVE_REINTEGRATION | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED | P3_COGNITION_SPECS | 451 |
| EXTERNAL_SIGNALS | IMPORT_AS_PROOF_SURFACE | P2_SECURITY_PROOF | 1 |
| EXTERNAL_SIGNALS | IMPORT_CONTRACT_SCHEMA_PACKET | P1_KERNEL_ADJACENT | 2 |
| EXTERNAL_SIGNALS | IMPORT_CONTRACT_SCHEMA_PACKET | P2_SECURITY_PROOF | 1 |
| EXTERNAL_SIGNALS | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P2_SECURITY_PROOF | 2 |
| EXTERNAL_SIGNALS | IMPORT_TESTS_READONLY_THEN_WIRE_TO_REAL_PATHS | P2_SECURITY_PROOF | 1 |
| EXTERNAL_SIGNALS | KEEP_AS_EVIDENCE | P2_SECURITY_PROOF | 2 |
| EXTERNAL_SIGNALS | MERGE_INTO_REGISTRY | P2_SECURITY_PROOF | 5 |
| EXTERNAL_SIGNALS | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED | P1_KERNEL_ADJACENT | 9 |
| EXTERNAL_SIGNALS | REGISTER_SPEC_THEN_IMPLEMENT_ADAPTER_ONLY_IF_NEEDED | P2_SECURITY_PROOF | 18 |
| RGPD_ISO | IMPORT_AS_PROOF_SURFACE | P3_DOCS_EVIDENCE | 2 |
| RGPD_ISO | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P2_COMPLIANCE | 60 |
| RGPD_ISO | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P3_DOCS_EVIDENCE | 167 |
| RGPD_ISO | IMPORT_TESTS_READONLY_THEN_WIRE_TO_REAL_PATHS | P3_DOCS_EVIDENCE | 12 |
| RGPD_ISO | KEEP_AS_EVIDENCE | P3_DOCS_EVIDENCE | 20 |
| RGPD_ISO | MANUAL_REVIEW_THEN_ADAPTER_BRANCH | P3_DOCS_EVIDENCE | 11 |
| RGPD_ISO | MERGE_INTO_REGISTRY | P3_DOCS_EVIDENCE | 8 |
| RSSI_SECURITY | IMPORT_AS_PROOF_SURFACE | P3_DOCS_EVIDENCE | 1 |
| RSSI_SECURITY | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P2_SECURITY | 24 |
| RSSI_SECURITY | IMPORT_DOC_AS_SPEC_OR_READINESS_ARTIFACT | P3_DOCS_EVIDENCE | 106 |
| RSSI_SECURITY | IMPORT_TESTS_READONLY_THEN_WIRE_TO_REAL_PATHS | P3_DOCS_EVIDENCE | 5 |
| RSSI_SECURITY | KEEP_AS_EVIDENCE | P3_DOCS_EVIDENCE | 12 |
| RSSI_SECURITY | MANUAL_REVIEW_THEN_ADAPTER_BRANCH | P3_DOCS_EVIDENCE | 11 |
| RSSI_SECURITY | MERGE_INTO_REGISTRY | P2_SECURITY | 8 |