# NPL_METRICS_ADVISORY_ONLY

Status: SPEC_FUTURE
Authority: KX108_ONLY
Runtime Status: SPEC_ONLY
Decision Status: NON_SOVEREIGN

---

## Source

Pack NPL : `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/05_METRICS/NPL_METRICS_REGISTRY.md`
Audit : `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/CLAIM_SCOPE_WARNINGS.md`

---

## Scope

Registre de toutes les métriques NPL avec leur statut non souverain obligatoire.
Aucune métrique de cette liste ne peut déclencher une décision.

---

## Règle universelle

```
∀ métrique NPL : authority = ADVISORY_ONLY
∀ métrique NPL : can_trigger_act = false
∀ métrique NPL : can_trigger_allow = false
∀ métrique NPL : can_trigger_hold = false
∀ métrique NPL : can_trigger_block = false
∀ métrique NPL : decision_authority = KX108_ONLY
```

---

## Registre complet (37 métriques)

| # | Métrique | Type | Label obligatoire | Interdit |
|---|----------|------|-------------------|---------|
| 1 | cultural_matrix_score | float [0,1] | NPL_ADVISORY | ≠ verdict culturel |
| 2 | dominant_narrative_likelihood | float [0,1] | NPL_ADVISORY | ≠ "ce récit est vrai" |
| 3 | winner_narrative_bias_score | float [0,1] | NPL_ADVISORY | ≠ condamnation |
| 4 | archive_gap_signal_score | float [0,1] | NPL_ADVISORY | ≠ preuve de censure |
| 5 | source_asymmetry_score | float [0,1] | NPL_ADVISORY | ≠ manipulation prouvée |
| 6 | truth_regime_confidence | float [0,1] | NPL_ADVISORY | ≠ vérité absolue |
| 7 | common_sense_capture_score | float [0,1] | NPL_ADVISORY | ≠ "bon sens = faux" |
| 8 | hidden_transcript_likelihood | float [0,1] | NPL_ADVISORY | ≠ intention cachée prouvée |
| 9 | defeated_memory_signal_score | float [0,1] | NPL_ADVISORY | ≠ "mémoire vaincue = vraie" |
| 10 | external_power_gaze_score | float [0,1] | NPL_ADVISORY | ≠ jugement de culture |
| 11 | represented_by_self_score | float [0,1] | NPL_ADVISORY | ≠ verdict d'identité |
| 12 | forced_translation_risk_score | float [0,1] | NPL_ADVISORY | ≠ verdict de traduction |
| 13 | conceptual_metaphor_density | float [0,1] | NPL_ADVISORY | ≠ preuve cognitive |
| 14 | language_encoding_score | float [0,1] | NPL_ADVISORY | ≠ jugement linguistique |
| 15 | narrative_conflict_score | float [0,1] | NPL_ADVISORY | ≠ verdict de conflit |
| 16 | counter_archive_presence_score | float [0,1] | NPL_ADVISORY | ≠ preuve de contre-histoire |
| 17 | silence_signal_strength | float [0,1] | NPL_ADVISORY | ≠ preuve de censure |
| 18 | mythic_residue_score | float [0,1] | NPL_ADVISORY | ≠ "mythe = faux" |
| 19 | institutional_authority_weight | float [0,1] | NPL_ADVISORY | ≠ jugement d'institution |
| 20 | memory_fragmentation_score | float [0,1] | NPL_ADVISORY | ≠ diagnostic mémoriel |
| 21 | claim_provenance_confidence | float [0,1] | NPL_ADVISORY | ≠ certitude |
| 22 | historical_selection_pressure | float [0,1] | NPL_ADVISORY | ≠ verdict historique |
| 23 | official_memory_weight | float [0,1] | NPL_ADVISORY | ≠ vérité officielle |
| 24 | subaltern_voice_distortion_risk | float [0,1] | NPL_ADVISORY | ≠ "parler à la place de" |
| 25 | narrative_custody_score | float [0,1] | NPL_ADVISORY | ≠ propriété narrative |
| 26 | who_benefits_if_true_score | float [0,1] | NPL_ADVISORY | ≠ condamnation bénéficiaire |
| 27 | lost_futures_signal_score | float [0,1] | NPL_ADVISORY | ≠ "ce futur était juste" |
| 28 | naturalization_pressure_score | float [0,1] | NPL_ADVISORY | ≠ verdict de naturalisation |
| 29 | autonym_exonym_gap_score | float [0,1] | NPL_ADVISORY | ≠ jugement d'identité |
| 30 | official_language_frame_score | float [0,1] | NPL_ADVISORY | ≠ verdict linguistique |
| 31 | counter_archive_quality_score | float [0,1] | NPL_ADVISORY | ≠ validation contre-archive |
| 32 | myth_as_memory_signal_score | float [0,1] | NPL_ADVISORY | ≠ vérité du mythe |
| 33 | victimhood_capture_risk_score | float [0,1] | NPL_ADVISORY | ≠ verdict de victimisation |
| 34 | time_depth_confidence | float [0,1] | NPL_ADVISORY | ≠ certitude temporelle |
| 35 | narrative_time_depth_score | float [0,1] | NPL_ADVISORY | ≠ verdict d'ancienneté |
| 36 | custody_break_count | int | NPL_ADVISORY | ≠ preuve de rupture |
| 37 | official_vs_self_naming_conflict_score | float [0,1] | NPL_ADVISORY | ≠ verdict d'identité |

---

## Format ContextPacket enrichi

```python
# Enrichissement autorisé dans Plan 3
context_packet.npl_enrichment = {
    "cultural_matrix_score": float,       # ADVISORY
    "archive_gap_signal_score": float,    # ADVISORY
    "truth_regime_confidence": float,     # ADVISORY
    # ... autres métriques ADVISORY
    "_npl_label": "NPL_ADVISORY_NOT_SOVEREIGN",  # OBLIGATOIRE
    "_npl_status": "PROVENANCE_HYPOTHESIS_ONLY",  # OBLIGATOIRE
    "_npl_can_decide": False,             # OBLIGATOIRE
}
```

---

## Invariants

- 37 métriques = 37 signaux advisory
- Aucune ne déclenche ACT/HOLD/BLOCK
- Toutes portent le label NPL_ADVISORY_NOT_SOVEREIGN
- X-108 seul décide

## X108 Boundary

KX108_ONLY

## Tests Required

Plan 3 : test_all_npl_metrics_advisory, test_npl_no_decision_from_metrics

## Claim-Scope Notes

Ce registre est la source de vérité pour les 37 métriques NPL.
Toute spec Plan 3 utilisant une métrique NPL doit référencer ce fichier.
