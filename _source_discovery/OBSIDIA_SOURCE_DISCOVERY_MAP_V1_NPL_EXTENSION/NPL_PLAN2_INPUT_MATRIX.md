# NPL_PLAN2_INPUT_MATRIX
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION
# Date: 2026-06-02

> Entrées pour le Plan 2 (rédaction des specs NPL).
> Ne crée aucune spec. Prépare seulement l'input.

---

## Règle absolue NPL pour Plan 2

```
NPL = PERIPHERAL_READONLY
NPL ↛ ACT
NPL ↛ ALLOW / HOLD / BLOCK
NPL → contexte, signal, provenance, hypothèse uniquement
KX108_ONLY pour toute décision
```

---

## P0 — Bloquant avant toute spec NPL

| Plan 2 Spec | Source paths | User source | Status | Must say | Must forbid | Tests futurs | Proof expected |
|-------------|-------------|-------------|--------|----------|-------------|--------------|----------------|
| `specs/npl/NPL_CANONICAL_SPEC.md` | `periphery/x108_ingress/readonly_context_ingress.py`, `periphery/context/context_packet_builder_v2.py`, `docs/PROOF_SCOPE.md` (modèle) | OUI | SPEC_CANDIDATE | PERIPHERAL_READONLY; KX108_ONLY; CONTEXT_ONLY; NO_ACT; NO_VERDICT_FINAL; provenance_uncertainty obligatoire; manipulation_risk_signal obligatoire | no kernel authority; no final truth; no moral verdict; no memory write without gate; no external theory as proof; no diagnosis; no manipulation | test_no_decision_authority, test_npl_never_outputs_verdict | Python test uniquement — FORMAL_PROOF_PENDING |
| `specs/npl/NPL_READONLY_BOUNDARY_SPEC.md` | `periphery/x108_ingress/readonly_context_ingress.py` (lines: can_emit_act=False, can_write_memory=False, assert_readonly()) | OUI | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `can_emit_act=False`; `can_write_memory=False`; `assert_readonly()` doit lever AssertionError si violation | pas de bypass du assert_readonly; pas d'exception silencieuse | test_no_act_emission | existant dans x108_ingress — étendre |
| `specs/npl/NPL_TO_X108_BOUNDARY_SPEC.md` | `periphery/x108_ingress/readonly_context_ingress.py`, `periphery/x108_ingress/x108_context_boundary.py` | OUI | SOURCE_FOUND_UNDER_DIFFERENT_NAME | NPL produit un ContextPacket enrichi — KX108 seul évalue et décide | NPL ne peut pas inclure ALLOW/HOLD/BLOCK dans son output | test_npl_to_x108_context_only | Python test |
| `specs/npl/HUMAN_LOGIC_PACKET_SPEC.md` | `periphery/context/context_packet_builder_v2.py` (champs: decision_authority, allowed_to_decide, allowed_to_act), `periphery/ingestion/document_ingestion_pipeline.py` | OUI | SPEC_CANDIDATE | HumanLogicPacket est une extension de ContextPacket; `provenance_confidence ∈ [0,1]`; `can_decide=False`; `cultural_origin: list[str]` | jamais clamer savoir "ce que pense vraiment l'humain"; jamais diagnostic; jamais certitude | test_npl_packet_schema | JSON schema validation |
| `specs/npl/NARRATIVE_PROVENANCE_PACKET_SPEC.md` | `periphery/ingestion/document_ingestion_pipeline.py` (IngestedDocument: source_class, content_hash), `periphery/ingestion/source_classifier.py` | OUI | SPEC_CANDIDATE | `provenance_chain: list[str]`; `uncertainty_level: float`; `source_class: TRUSTED/UNTRUSTED/UNCLASSIFIED`; content_hash sha256 obligatoire | aucune provenance sans hash; jamais `provenance_confidence=1.0` sans validation humaine | test_npl_packet_schema | Hash sha256 requis |
| `specs/npl/NPL_RSSI_NON_MANIPULATION_SPEC.md` | `periphery/bias/bias_gate.py` (BiasGateResult: bias_detected, bias_validated, gate_result), `periphery/bias/bias_trace.py` | OUI | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `manipulation_risk_signal` obligatoire dans tout packet NPL; si signal > threshold → gate=HOLD automatique; audit trail via BiasTrace | no hidden manipulation field; no silent suppression of risk signal | test_rssi_non_manipulation_gate | Python test + BiasTrace log |

---

## P1 — Nécessaire avant diffusion Plan 2

| Plan 2 Spec | Source paths | User source | Status | Must say | Must forbid | Tests futurs | Notes |
|-------------|-------------|-------------|--------|----------|-------------|--------------|-------|
| `specs/npl/CULTURAL_MATRIX_SPEC.md` | `periphery/OBSIDIA_MMONDE.../ARBRE_19__Arbre_de_la_Culture/activation_rules.md`, `periphery/language/language_router.py` | OUI | SPEC_CANDIDATE | `cultural_matrix_density ∈ [0,1]`; `language_encoding_score ∈ [0,1]`; non_decision_contract respecté (Tree34 ↛ ACT) | jamais hiérarchiser cultures; jamais "culture X est supérieure"; jamais verdict culturel | test_cultural_matrix_no_verdict | Tree19 = récepteur déjà présent |
| `specs/npl/TRUTH_REGIME_SPEC.md` | `.../ARBRE_27__Arbre_de_la_Verite/activation_rules.md`, `periphery/context/context_packet_builder_v2.py` (forbidden_tokens_detected) | OUI | SPEC_CANDIDATE | `truth_regime_confidence ∈ [0,1]`; `truth_regime_type: list[str]`; jamais single truth claim | forbidden_tokens: ALLOW/HOLD/BLOCK/ACT dans output NPL | test_npl_never_outputs_verdict | Foucault = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/ARCHIVE_GAP_SPEC.md` | `.../ARBRE_25__Arbre_de_l_Histoire/activation_rules.md` | OUI | SPEC_CANDIDATE | `archive_gap_score ∈ [0,1]`; gap = signal d'absence documentaire — hypothèse | jamais "absence = preuve de manipulation"; jamais verdict sur qui a effacé | — | Trouillot = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/WINNER_NARRATIVE_SPEC.md` | `.../ARBRE_25__Arbre_de_l_Histoire/`, `.../ARBRE_27__Arbre_de_la_Verite/` | OUI | SPEC_CANDIDATE | `winner_bias_score ∈ [0,1]`; `defeated_memory_residue: float`; CONTEXT_ONLY | winner_bias_score ≠ condamnation; jamais déclarer un récit "faux" | — | Gramsci = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/DEFEATED_MEMORY_SPEC.md` | `.../ARBRE_24__Arbre_de_la_Memoire/`, `.../ARBRE_25__Arbre_de_l_Histoire/` | OUI | SPEC_CANDIDATE | `defeated_memory_signal_score ∈ [0,1]`; signal probabiliste | jamais "cette mémoire est la vraie" | — | Halbwachs = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/EDUCATION_BLOCKAGE_SPEC.md` | `periphery/education/education_score.py` (EducationScore: stability, coherence, memory_reuse, correct_refusal, absence_of_drift) | OUI | SOURCE_FOUND_UNDER_DIFFERENT_NAME | `education_blockage_signal: float`; ADVISORY_ONLY; X108 décide; `needs_human_validation=True` si score BELOW_THRESHOLD | jamais "cet humain est bloqué" comme verdict; jamais diagnostic d'apprentissage | test_education_student_blockage_packet | education_score.py = récepteur existant |

---

## P2 — Utile

| Plan 2 Spec | Source paths | User source | Notes |
|-------------|-------------|-------------|-------|
| `specs/npl/COMMON_SENSE_CAPTURE_SPEC.md` | `periphery/bias/bias_gate.py` | OUI | BiasGate intercepte "bon sens" présenté comme vérité — étendre |
| `specs/npl/HIDDEN_TRANSCRIPT_SPEC.md` | `periphery/context/context_packet_builder_v2.py` (contradictions field) | OUI | hidden_transcript_probability = [0,1] — jamais certitude |
| `specs/npl/CONCEPTUAL_METAPHOR_SPEC.md` | Tree04 Sens + Tree08 Pensée | OUI | metaphor_matrix_count — Lakoff = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/COLLECTIVE_MEMORY_SPEC.md` | Tree24 + `MEMOIRE_PERSONNELLE_OBSIDIA` agent | OUI | Halbwachs/Assmann = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/OFFICIAL_VS_WARM_MEMORY_SPEC.md` | Tree24 Mémoire | OUI | Distinction contextuelle — pas hiérarchisation |

---

## P3 — Annexe

| Plan 2 Spec | Source | Notes |
|-------------|--------|-------|
| `specs/npl/SUBALTERN_VOICE_SPEC.md` | Archive gap + mémoire vaincue | Spivak = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/PARADIGM_FRAME_SPEC.md` | Tree14 + Tree27 | Kuhn = EXTERNAL_REFERENCE_REGISTRY |
| `specs/npl/FUTURES_LOST_SPEC.md` | Tree23 + Tree29 | Concept ouvert — pas de récepteur existant |

---

## Agents 52 impliqués dans NPL (receptor agents)

Ces agents doivent être référencés dans les specs NPL — ils ne doivent pas être modifiés.

| Agent | Rôle NPL | Source |
|-------|----------|--------|
| `MEMOIRE_PERSONNELLE_OBSIDIA` | Récepteur mémoire narrative | `agents_52.registry.json` |
| `VOCABULAIRE_CANONIQUE` | Récepteur encodage linguistique | `agents_52.registry.json` |
| `THEORIE_VIVANTE` | Récepteur théorie culturelle vivante | `agents_52.registry.json` |
| `RECHERCHE_EXTERNE` | Récepteur courants externes (EXTERNAL_REFERENCE_REGISTRY) | `agents_52.registry.json` |
| `FRISE_HUMAINE` | Récepteur timeline humaine / history mapping | `agents_52.registry.json` |
| `HUMAN_HISTORY_MAPPER` | Récepteur cartographie histoire | `agents_52.registry.json` |
| `CARTOGRAPHE_34_ARBRES` | Récepteur activation Tree34 | `agents_52.registry.json` |
| `ONTOLOGUE_OBSIDIA` | Récepteur structure ontologique NPL | `agents_52.registry.json` |
| `DATA_SOVEREIGNTY_GUARD` | Garde données NPL — souveraineté | `agents_52.registry.json` |
| `ANTI_DISPERSION` | Garde contre dilution NPL → kernel | `agents_52.registry.json` |
