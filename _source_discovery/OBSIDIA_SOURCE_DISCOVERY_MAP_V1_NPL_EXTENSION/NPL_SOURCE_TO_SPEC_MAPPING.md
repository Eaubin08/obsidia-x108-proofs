# NPL_SOURCE_TO_SPEC_MAPPING
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION
# Date: 2026-06-02

> Table de correspondance : concept NPL → source utilisateur → récepteur Obsidia existant → spec future.

---

## Bloc A — NPL Core

| NPL Concept | Source utilisateur | Source GitHub/local | Statut | Spec future | Plan 2 folder | Priority | Claim-scope |
|-------------|-------------------|---------------------|--------|-------------|---------------|----------|-------------|
| NPL_CANONICAL_SPEC | USER_PROVIDED_SOURCE_ONLY | ABSENT | ABSENT_UNDER_THIS_NAME | `specs/npl/NPL_CANONICAL_SPEC.md` | `specs/npl/` | P0 | PERIPHERAL_READONLY absolu — jamais kernel |
| NPL_READONLY_BOUNDARY | USER_PROVIDED_SOURCE_ONLY | `periphery/x108_ingress/readonly_context_ingress.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `specs/npl/NPL_READONLY_BOUNDARY_SPEC.md` | `specs/npl/` | P0 | `can_emit_act=False`, `can_write_memory=False` |
| NPL_TO_X108_BOUNDARY | USER_PROVIDED_SOURCE_ONLY | `periphery/x108_ingress/x108_context_boundary.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `specs/npl/NPL_TO_X108_BOUNDARY_SPEC.md` | `specs/npl/` | P0 | KX108_ONLY — NPL produit contexte seulement |
| NPL_AUTHORITY_BOUNDARY | USER_PROVIDED_SOURCE_ONLY | `periphery/reverse_os/action_projection_readonly.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | inclus dans NPL_CANONICAL_SPEC | `specs/npl/` | P0 | NO_ACT, NO_VERDICT_FINAL |
| NPL_RSSI_NON_MANIPULATION | USER_PROVIDED_SOURCE_ONLY | `periphery/bias/bias_gate.py` (partiel) | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `specs/npl/NPL_RSSI_NON_MANIPULATION_SPEC.md` | `specs/npl/` | P0 | manipulation_risk_signal obligatoire dans chaque packet |

---

## Bloc B — Packets

| NPL Concept | Source utilisateur | Source GitHub/local | Statut | Spec future | Plan 2 folder | Priority | Claim-scope |
|-------------|-------------------|---------------------|--------|-------------|---------------|----------|-------------|
| HUMAN_LOGIC_PACKET | USER_PROVIDED_SOURCE_ONLY | `periphery/context/context_packet_builder_v2.py` (récepteur) | SPEC_CANDIDATE | `specs/npl/HUMAN_LOGIC_PACKET_SPEC.md` | `specs/npl/packets/` | P0 | Hypothèse de provenance — jamais certitude |
| NARRATIVE_PROVENANCE_PACKET | USER_PROVIDED_SOURCE_ONLY | `periphery/ingestion/document_ingestion_pipeline.py` (récepteur partiel) | SPEC_CANDIDATE | `specs/npl/NARRATIVE_PROVENANCE_PACKET_SPEC.md` | `specs/npl/packets/` | P0 | `provenance_confidence` ∈ [0,1] — obligatoire |
| CULTURAL_MATRIX_PACKET | USER_PROVIDED_SOURCE_ONLY | Tree19 Culture `activation_rules.md` (récepteur) | SPEC_CANDIDATE | `specs/npl/CULTURAL_MATRIX_SPEC.md` | `specs/npl/packets/` | P1 | cultural_matrix_density ≠ verdict culturel |
| ARCHIVE_GAP_PACKET | USER_PROVIDED_SOURCE_ONLY | Tree25 Histoire (récepteur) | SPEC_CANDIDATE | `specs/npl/ARCHIVE_GAP_SPEC.md` | `specs/npl/packets/` | P1 | archive_gap_score = signal d'absence — hypothèse |
| TRUTH_REGIME_PACKET | USER_PROVIDED_SOURCE_ONLY | Tree27 Vérité (récepteur) | SPEC_CANDIDATE | `specs/npl/TRUTH_REGIME_SPEC.md` | `specs/npl/packets/` | P1 | truth_regime_confidence ≠ vérité absolue |
| DEFEATED_MEMORY_SIGNAL | USER_PROVIDED_SOURCE_ONLY | Tree24 Mémoire + Tree25 Histoire | SPEC_CANDIDATE | `specs/npl/DEFEATED_MEMORY_SPEC.md` | `specs/npl/packets/` | P1 | defeated_memory_signal_score = probabiliste |
| HIDDEN_TRANSCRIPT_PACKET | USER_PROVIDED_SOURCE_ONLY | `context_packet_builder_v2.py` (contradictions field) | SPEC_CANDIDATE | `specs/npl/HIDDEN_TRANSCRIPT_SPEC.md` | `specs/npl/packets/` | P2 | hidden_transcript_probability — jamais verdict |
| METAPHOR_MATRIX_PACKET | USER_PROVIDED_SOURCE_ONLY | Tree04 Sens + Tree08 Pensée | SPEC_CANDIDATE | `specs/npl/CONCEPTUAL_METAPHOR_SPEC.md` | `specs/npl/packets/` | P2 | metaphor_matrix_count = signal cognitif — pas preuve |
| EDUCATION_BLOCKAGE_PACKET | USER_PROVIDED_SOURCE_ONLY | `periphery/education/education_score.py` (récepteur) | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `specs/npl/EDUCATION_BLOCKAGE_SPEC.md` | `specs/npl/packets/` | P1 | education_blockage ≠ jugement de l'humain |

---

## Bloc C — Concepts

| NPL Concept | Source utilisateur | Source GitHub/local | Statut | Spec future | Plan 2 folder | Priority | Claim-scope |
|-------------|-------------------|---------------------|--------|-------------|---------------|----------|-------------|
| LOGIC_AS_CULTURE_COMPRESSED | USER_PROVIDED_SOURCE_ONLY | Tree19 Culture + Tree10 Langage | SPEC_CANDIDATE | inclus dans CULTURAL_MATRIX_SPEC | `specs/npl/` | P0 | Explain without judging — NO_VERDICT_FINAL |
| HUMAN_THINKS_FROM_A_WORLD | USER_PROVIDED_SOURCE_ONLY | Tree01 Humain + Tree06 Compréhension | SPEC_CANDIDATE | inclus dans HUMAN_LOGIC_PACKET_SPEC | `specs/npl/` | P1 | Signal provenance — pas diagnostic |
| WINNER_HISTORY_AND_DEFEATED_MEMORY | USER_PROVIDED_SOURCE_ONLY | Tree25 Histoire + Tree27 Vérité | SPEC_CANDIDATE | `specs/npl/WINNER_NARRATIVE_SPEC.md` | `specs/npl/` | P1 | winner_bias_score = signal — jamais condamnation |
| ARCHIVE_GAP_AS_CONTEXT_SIGNAL | USER_PROVIDED_SOURCE_ONLY | Tree25 Histoire | SPEC_CANDIDATE | inclus dans ARCHIVE_GAP_SPEC | `specs/npl/` | P1 | Absence de source ≠ preuve de manipulation |
| COMMON_SENSE_AS_CAPTURED_NARRATIVE | USER_PROVIDED_SOURCE_ONLY | `bias_gate.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `specs/npl/COMMON_SENSE_CAPTURE_SPEC.md` | `specs/npl/` | P2 | BiasGate intercepte le "bon sens" non validé |
| LANGUAGE_AS_CULTURAL_ENCODING | USER_PROVIDED_SOURCE_ONLY | `language_router.py` + Tree10 Langage | SOURCE_FOUND_UNDER_DIFFERENT_NAME | inclus dans CULTURAL_MATRIX_SPEC | `specs/npl/` | P1 | language_encoding_score ≠ jugement de valeur |
| FUTURES_LOST_BY_HISTORY | USER_PROVIDED_SOURCE_ONLY | Tree23 Temps + Tree29 Finalité | SPEC_CANDIDATE | `specs/npl/FUTURES_LOST_SPEC.md` | `specs/npl/` | P3 | Possibles non actualisés — hypothèse ouverte |
| OFFICIAL_ARCHIVE_AND_WARM_MEMORY | USER_PROVIDED_SOURCE_ONLY | Tree24 Mémoire | SPEC_CANDIDATE | `specs/npl/OFFICIAL_VS_WARM_MEMORY_SPEC.md` | `specs/npl/` | P2 | Distinction contextuelle — pas hiérarchisation |

---

## Bloc D — Courants externes (EXTERNAL_REFERENCE_REGISTRY)

| Courant | Source utilisateur | Source GitHub | Statut | Usage autorisé | Interdit |
|---------|-------------------|---------------|--------|----------------|---------|
| Berger-Luckmann (Social Reality) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer la spec — DOC_ONLY | Preuve algorithmique, décision |
| Lakoff-Johnson (Conceptual Metaphors) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer METAPHOR_MATRIX_PACKET | Autorité décisionnelle |
| Foucault (Truth Regimes) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer TRUTH_REGIME_PACKET | Verdict de vérité |
| Gramsci (Cultural Hegemony) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer WINNER_NARRATIVE_SPEC | Hiérarchiser les cultures |
| Trouillot (Archive Silences) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer ARCHIVE_GAP_SPEC | Confirmer manipulation |
| Halbwachs / Assmann (Collective Memory) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer COLLECTIVE_MEMORY_SPEC | Décision mémoire |
| James Scott (Hidden Transcripts) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer HIDDEN_TRANSCRIPT_SPEC | Verdict sur intention |
| Edward Said (External Gaze) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer external_power_gaze_score | Juger une culture |
| Spivak (Subaltern) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer SUBALTERN_VOICE_SPEC | Parler "à la place de" |
| Kuhn (Paradigm Shifts) | USER_PROVIDED_SOURCE_ONLY | ABSENT | EXTERNAL_REFERENCE_REGISTRY | Informer PARADIGM_FRAME_SPEC | Autorité scientifique |

> **Règle absolue** : ces courants sont `DOC_ONLY`, `NO_AUTHORITY`, `NO_DECISION`. Ils informent la rédaction des specs — ils ne fondent pas le runtime.

---

## Bloc E — Branchements NPL → Obsidia

| NPL Branch | Récepteur Obsidia | Source récepteur | Statut | Boundary |
|------------|------------------|------------------|--------|---------|
| NPL_TO_GRAPHITI | Graphiti readonly bridge | `sigma/graphiti_readonly_bridge.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | NO_GRAPHITI_WRITE sans gate humain |
| NPL_TO_BRODY | Brody context query | `periphery/brody/brody_context_query.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | Brody = signal contextuel uniquement |
| NPL_TO_OS_TRAD | Language router + OS Trad IR | `periphery/language/language_router.py`, `apps/obsidia-workbench/OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | IR candidate = readonly |
| NPL_TO_SIGMA | Sigma pipeline | `sigma/run_pipeline.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | CONTEXT_ONLY — pas de verdict Sigma |
| NPL_TO_TREE34 | Trees 10,17,18,19,24,25,27 | `04_ARBRES_34_TENSOR_MATRIX/ARBRE_*/activation_rules.md` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | non_decision_contract présent pour tous |
| NPL_TO_EDUCATION | Education score | `periphery/education/education_score.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | ADVISORY_ONLY — X108 décide |
| NPL_TO_X108 | X108 context ingress | `periphery/x108_ingress/readonly_context_ingress.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | CONTEXT_ONLY — KX108_ONLY |
| NPL_TO_RSSI_NON_MANIPULATION | Bias gate + language router | `periphery/bias/bias_gate.py` | SOURCE_FOUND_UNDER_DIFFERENT_NAME | manipulation_risk_signal obligatoire |

---

## Bloc F — Métriques NPL

| Métrique | Source utilisateur | Récepteur Obsidia | Spec future | Claim-scope |
|----------|-------------------|-------------------|-------------|-------------|
| cultural_matrix_density | USER_PROVIDED | Tree19 activation_rules.md | CULTURAL_MATRIX_SPEC | Score [0,1] — pas verdict culturel |
| language_encoding_score | USER_PROVIDED | `language_router.py` | inclus dans CULTURAL_MATRIX_SPEC | Encodage détecté — pas jugement |
| truth_regime_confidence | USER_PROVIDED | Tree27 activation | TRUTH_REGIME_SPEC | Confidence [0,1] — pas vérité |
| archive_gap_score | USER_PROVIDED | Tree25 activation | ARCHIVE_GAP_SPEC | Signal d'absence — hypothèse |
| winner_bias_score | USER_PROVIDED | Tree27 + Tree25 | WINNER_NARRATIVE_SPEC | Probabiliste — jamais condamnation |
| defeated_memory_signal_score | USER_PROVIDED | Tree24 + Tree25 | DEFEATED_MEMORY_SPEC | Signal — pas preuve de suppression |
| common_sense_capture_score | USER_PROVIDED | `bias_gate.py` | COMMON_SENSE_CAPTURE_SPEC | Biais possible — pas confirmation |
| hidden_transcript_probability | USER_PROVIDED | `context_packet_builder_v2.py` contradictions | HIDDEN_TRANSCRIPT_SPEC | Probabilité [0,1] — jamais certitude |
| external_power_gaze_score | USER_PROVIDED | Source classifier TRUSTED/UNTRUSTED | SUBALTERN_VOICE_SPEC | Signal de cadrage externe |
| metaphor_matrix_count | USER_PROVIDED | Tree04 Sens + Tree08 Pensée | CONCEPTUAL_METAPHOR_SPEC | Comptage — pas interprétation finale |
| provenance_uncertainty | USER_PROVIDED | ContextPacket V2 risk_flags | NPL_CANONICAL_SPEC | Obligatoire dans chaque packet |
| manipulation_risk_signal | USER_PROVIDED | `bias_gate.py` + BiasTrace | NPL_RSSI_NON_MANIPULATION_SPEC | Toujours exposé — jamais masqué |

---

## Bloc G — Tests futurs

| Test | Statut | Spec source | Note |
|------|--------|-------------|------|
| test_no_decision_authority | ABSENT — à créer | NPL_CANONICAL_SPEC | Vérifier `can_decide=False` pour tout packet NPL |
| test_no_act_emission | ABSENT — à créer | NPL_READONLY_BOUNDARY_SPEC | Vérifier `can_emit_act=False` |
| test_npl_packet_schema | ABSENT — à créer | HUMAN_LOGIC_PACKET_SPEC | Schéma JSON valide avec provenance_uncertainty |
| test_graphiti_readonly_adapter | ABSENT — à créer | NPL_TO_GRAPHITI | NO_GRAPHITI_WRITE vérifiable |
| test_brody_npl_context | ABSENT — à créer | NPL_TO_BRODY | Brody reçoit contexte NPL — ne décide pas |
| test_npl_to_x108_context_only | ABSENT — à créer | NPL_TO_X108_BOUNDARY_SPEC | X108 reçoit NPL comme input — pas comme verdict |
| test_npl_never_outputs_verdict | ABSENT — à créer | NPL_CANONICAL_SPEC | Aucun packet NPL ne contient ALLOW/HOLD/BLOCK |
| test_education_student_blockage_packet | Partiellement existant | `tests/periphery/test_education_score.py` | Étendre pour NPL education_blockage |
