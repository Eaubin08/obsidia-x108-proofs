# NPL_TO_PLAN3_CONSTRAINTS

Status: SPEC_FUTURE
Authority: KX108_ONLY
Runtime Status: SPEC_ONLY
Decision Status: NON_SOVEREIGN
Memory Write Status: FORBIDDEN
Graphiti Write Status: FORBIDDEN

---

## Source

Audit : `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/AUDIO_ENTROPY_TO_PLAN3_CONSTRAINTS.md`
Pack NPL : `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX.zip` (103 fichiers, SPEC_FUTURE/KX108_ONLY)

---

## Scope

Définir comment Plan 3 (Runtime Contract Skeleton) doit traiter NPL.
NPL ne peut influencer Plan 3 que comme contexte enrichi — jamais comme autorité.

---

## Allowed dans Plan 3

```yaml
narrative_provenance_packet:
  type: NarrativeProvenancePacket
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY
  readonly: true
  emits_act: false
  emits_verdict: false
  memory_write: false
  graphiti_write: false
  decision_authority: KX108_ONLY
  label: PROVENANCE_HYPOTHESIS_ONLY

context_packet_npl_enriched:
  type: ContextPacket
  enrichments_allowed:
    - cultural_matrix_score: float [0,1]    # ADVISORY
    - dominant_narrative_likelihood: float  # ADVISORY
    - archive_gap_signal_score: float       # ADVISORY
    - source_asymmetry_score: float         # ADVISORY
    - truth_regime_confidence: float        # ADVISORY
    - narrative_custody_score: float        # ADVISORY
    - who_benefits_if_true_score: float     # ADVISORY
    - victimhood_capture_risk_score: float  # ADVISORY
  authority: ADVISORY_ONLY
  label: NPL_ADVISORY_NOT_SOVEREIGN
```

## Forbidden dans Plan 3

```
NPL ↛ ACT
NPL ↛ ALLOW
NPL ↛ HOLD
NPL ↛ BLOCK
NPL ↛ truth_final
NPL ↛ historical_truth_final
NPL ↛ moral_verdict
NPL ↛ memory_write
NPL ↛ graphiti_write
NPL ↛ neo4j_write
NPL ↛ kernel_mutation
NPL ↛ diagnostic (médical / psychologique)
```

---

## Prerequis Plan 2 avant branchement Plan 3

| Prerequis | Statut |
|-----------|--------|
| `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_CANONICAL_SPEC.md` | ✅ Créé |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_READONLY_BOUNDARY_SPEC.md` | ✅ Créé |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/HUMAN_LOGIC_PACKET_SPEC.md` | ✅ Créé |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/NARRATIVE_PROVENANCE_PACKET_SPEC.md` | ✅ Créé |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_TO_X108_BOUNDARY_SPEC.md` | ✅ Créé |
| Tests NPL (08_TESTS_REQUIRED/ du pack) | ❌ À implémenter en Plan 3 |

---

## Métriques NPL autorisées en Plan 3 (toutes ADVISORY)

Voir `specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_METRICS_ADVISORY_ONLY.md`

---

## Invariants

- NPL reste SPEC_FUTURE jusqu'à Plan 2 complet
- Plan 3 peut consommer NarrativeProvenancePacket readonly uniquement
- X-108 reste seul droit de passage pour ACT/HOLD/BLOCK

## X108 Boundary

KX108_ONLY — NPL produit du contexte, X-108 décide

## Tests Required

Plan 3 : test_npl_never_emits_act, test_npl_packet_readonly, test_npl_no_memory_write

## Claim-Scope Notes

Tout enrichissement NPL dans un ContextPacket Plan 3 doit porter le label `NPL_ADVISORY_NOT_SOVEREIGN`.
