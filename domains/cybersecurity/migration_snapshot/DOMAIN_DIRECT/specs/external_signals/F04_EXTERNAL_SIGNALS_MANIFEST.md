# F04_EXTERNAL_SIGNALS_MANIFEST

**Date :** 2026-06-02
**Source :** `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip`
**Authority :** KX108_ONLY
**Import type :** READONLY_SOURCE_IMPORT — SPEC_ONLY

---

| # | Imported file | Target path | Role | Boundary | Runtime status |
|---|---------------|-------------|------|----------|----------------|
| 1 | README.md | `docs/source_packs/external_signals/README.md` | Description du pack | DOC_ONLY | DOC_ONLY |
| 2 | MERGE_INSTRUCTIONS.md | `docs/source_packs/external_signals/MERGE_INSTRUCTIONS.md` | Instructions de merge | DOC_ONLY | DOC_ONLY |
| 3 | SHA256SUMS.txt | `docs/source_packs/external_signals/SHA256SUMS.txt` | Hashes intégrité | EVIDENCE_ONLY | DOC_ONLY |
| 4 | VALIDATION_REPORT.yaml | `docs/source_packs/external_signals/VALIDATION_REPORT.yaml` | Rapport de validation | EVIDENCE_ONLY | DOC_ONLY |
| 5 | C459_timeverse_temporal_sidecar.yaml | `specs/external_signals/component_specs/C459_...` | Temporal Sidecar spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 6 | C460_temporal_context_header.yaml | `specs/external_signals/component_specs/C460_...` | Context Header spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 7 | C461_tick_canonical_validation.yaml | `specs/external_signals/component_specs/C461_...` | Tick Validation spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 8 | C462_no_float_temporal_math.yaml | `specs/external_signals/component_specs/C462_...` | No-Float Math spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 9 | C463_anti_replay_horizon.yaml | `specs/external_signals/component_specs/C463_...` | Anti-Replay Horizon | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 10 | C464_temporal_challenge.yaml | `specs/external_signals/component_specs/C464_...` | Temporal Challenge | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 11 | C465_time_bounded_tool_call_check.yaml | `specs/external_signals/component_specs/C465_...` | Tool Call Check | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 12 | C466_temporal_receipt_metadata.yaml | `specs/external_signals/component_specs/C466_...` | Receipt Metadata | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 13 | C467_TSAE_receipt_model.yaml | `specs/external_signals/component_specs/C467_...` | TSAE Receipt Model | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 14 | C468_receipt_anchor_hash.yaml | `specs/external_signals/component_specs/C468_...` | Receipt Anchor Hash | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 15 | C469_stale_execution_detection.yaml | `specs/external_signals/component_specs/C469_...` | Stale Execution | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 16 | C470_temporal_zero_trust_positioning.yaml | `specs/external_signals/component_specs/C470_...` | Zero Trust Position | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 17 | C471_gateway_before_endpoint_prefilter.yaml | `specs/external_signals/component_specs/C471_...` | Gateway Prefilter | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 18 | C472_consequence_boundary_enrichment.yaml | `specs/external_signals/component_specs/C472_...` | Consequence Boundary | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 19 | C473_wrapper_non_reauthoring_law.yaml | `specs/external_signals/component_specs/C473_...` | Non-Reauthoring Law | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 20 | C474_law_state_input_replay_triplet.yaml | `specs/external_signals/component_specs/C474_...` | Replay Triplet | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 21 | C475_corridor_packaging_registry.yaml | `specs/external_signals/component_specs/C475_...` | Corridor Registry | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 22 | C476_refusal_preserves_structure.yaml | `specs/external_signals/component_specs/C476_...` | Refusal Structure | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 23 | C477_protected_consequence_could_not_bind.yaml | `specs/external_signals/component_specs/C477_...` | Protected Consequence | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 24 | C478_executable_standing_check.yaml | `specs/external_signals/component_specs/C478_...` | Standing Check | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 25 | C479_continuation_legitimacy_check.yaml | `specs/external_signals/component_specs/C479_...` | Legitimacy Check | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 26 | C480_consequence_binding_status_extended.yaml | `specs/external_signals/component_specs/C480_...` | Binding Status | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 27 | C481_visible_enforcement_surface.yaml | `specs/external_signals/component_specs/C481_...` | Enforcement Surface | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 28 | C482_intent_effect_receipt_separation.yaml | `specs/external_signals/component_specs/C482_...` | Intent/Effect Sep. | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 29 | 46_external_category_signals.spec.yaml | `specs/external_signals/family_specs/46_...` | Family 46 spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 30 | 47_timeverse_temporal_sidecar.spec.yaml | `specs/external_signals/family_specs/47_...` | Family 47 spec (37KB) | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 31 | 48_consequence_boundary_enrichment.spec.yaml | `specs/external_signals/family_specs/48_...` | Family 48 spec | REGISTER_SPEC_FIRST | SPEC_CANDIDATE |
| 32 | 51_temporal_context_header.packet.yaml | `specs/external_signals/packets/51_...` **[D1]** | Temporal Context Packet | SPEC_ONLY_PACKET_CONTRACT | SPEC_CANDIDATE |
| 33 | 52_temporal_receipt.packet.yaml | `specs/external_signals/packets/52_...` **[D1]** | Temporal Receipt Packet | SPEC_ONLY_PACKET_CONTRACT | SPEC_CANDIDATE |
| 34 | 53_consequence_boundary.packet.yaml | `specs/external_signals/packets/53_...` **[D1]** | Consequence Boundary Packet | SPEC_ONLY_PACKET_CONTRACT | SPEC_CANDIDATE |
| 35 | 06_COMPONENT_INDEX_APPEND.csv | `specs/external_signals/appendices/06_...` | Component Index | SOURCE_REGISTRY_APPEND | DOC_ONLY |
| 36 | 08_METRIC_DICTIONARY_APPEND.yaml | `specs/external_signals/appendices/08_...` | Metric Dictionary | SOURCE_REGISTRY_APPEND | DOC_ONLY |
| 37 | 09_FORMULA_DICTIONARY_APPEND.md | `specs/external_signals/appendices/09_...` | Formula Dictionary | SOURCE_REGISTRY_APPEND | DOC_ONLY |
| 38 | 10_INVARIANTS_APPEND.md | `specs/external_signals/appendices/10_...` | Invariants Append | SOURCE_REGISTRY_APPEND | DOC_ONLY |
| 39 | 53_EXTERNAL_SIGNALS_PROOF_ARTIFACTS.md | `specs/external_signals/proof/53_...` | Proof artifacts | EVIDENCE_ONLY | DOC_ONLY |
| 40 | 52_EXTERNAL_SIGNALS_TEST_MATRIX.md | `specs/external_signals/test_matrix/52_...` | Test matrix | READONLY_THEN_WIRE | DOC_ONLY |

---

## Fichier exclu (D4)

| Fichier | Raison | Statut |
|---------|--------|--------|
| `07_COMPONENT_SPEC_MATRIX_APPEND.csv` | D4 — 53KB — human review required before merge | `SOURCE_REGISTRY_APPEND_PENDING_REVIEW` — reste dans raw/ uniquement |

---

## D1 appliquée — Redirection packets

Les 3 fichiers packets (51, 52, 53) étaient ciblés vers `packages/shared/packets/external_signals/`.
Ce chemin est **interdit** (`packages/` absent du repo).
Ils ont été importés dans `specs/external_signals/packets/` conformément à la décision D1.

**Statut :** `SPEC_ONLY_PACKET_CONTRACT`
