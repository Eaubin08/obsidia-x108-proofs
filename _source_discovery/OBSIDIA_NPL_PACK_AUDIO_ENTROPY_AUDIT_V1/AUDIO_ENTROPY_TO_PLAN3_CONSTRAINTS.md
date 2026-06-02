# AUDIO_ENTROPY_TO_PLAN3_CONSTRAINTS
# OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1
# Date: 2026-06-02
# Couvre : Phase 4 NPL Audit + Phase 7 (Plan2 Delta) + Phase 8 (Plan3 Blockers) Audio Entropy Audit

---

## Contraintes pour Plan 3 (Runtime Contract Skeleton)

Ces deux sources (NPL Pack + Audio/Entropy) ne peuvent influencer Plan 3 QUE comme contraintes,
jamais comme autorité. X-108 reste seul droit de passage.

---

## ALLOWED dans Plan 3

### Depuis le pack NPL

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
  label_obligatoire: PROVENANCE_HYPOTHESIS_ONLY

context_packet_npl_enriched:
  type: ContextPacket
  enrichments:
    - cultural_matrix_score: float [0,1]
    - dominant_narrative_likelihood: float [0,1]
    - archive_gap_signal_score: float [0,1]
    - source_asymmetry_score: float [0,1]
    - truth_regime_confidence: float [0,1]
    - narrative_custody_score: float [0,1]
    - who_benefits_if_true_score: float [0,1]
    - lost_futures_signal_score: float [0,1]
    - victimhood_capture_risk_score: float [0,1]
  authority: ADVISORY_ONLY
  label_obligatoire: NPL_ADVISORY_NOT_SOVEREIGN
```

### Depuis l'audio / entropie

```yaml
entropy_metrics_candidate:
  - thermo_debt: float        # advisory signal P161
  - L_value: float            # Lyapunov advisory signal P107
  - semantic_heat_estimate: float  # futur — non existant
  status: PYTHON_SPEC_NOT_LEAN_PROVEN
  authority: ADVISORY_ONLY
  can_trigger_hold: false     # seul X-108 décide
  label_obligatoire: ENTROPY_ADVISORY_NOT_RUNTIME_AUTHORITY

buv_filter_candidate:
  type: float  # admissibility_score
  status: PYTHON_SPEC_SANDBOX_ONLY
  authority: ADVISORY_ONLY
  label_obligatoire: BUV_SANDBOX_NOT_GATEWAY

narrative_provenance_context:
  usage: enrichir le ContextPacket de Plan 3
  source: NPL pack → NarrativeProvenancePacket
  authority: CONTEXT_ONLY
  label_obligatoire: NPL_ADVISORY_NOT_SOVEREIGN

future_formal_target:
  - P107 → Plan 4+ formalisation Lean
  - P161 → Plan 4+ formalisation Lean
  - NPL_MASTER_SPEC → Plan 2 specs/ d'abord
  - BUV_MASTER_SPEC → Plan 2 specs/ d'abord
```

---

## FORBIDDEN dans Plan 3

### Depuis le pack NPL

```
NPL ↛ ACT
NPL ↛ ALLOW
NPL ↛ HOLD
NPL ↛ BLOCK
NPL ↛ truth_final
NPL ↛ historical_truth_final
NPL ↛ historical_verdict_final
NPL ↛ moral_verdict
NPL ↛ victim_truth
NPL ↛ winner_falsehood
NPL ↛ defeated_truth
NPL ↛ archive_gap_proof
NPL ↛ myth_truth
NPL ↛ naturalization_falsehood
NPL ↛ official_language_falsehood
NPL ↛ memory_write
NPL ↛ graphiti_write
NPL ↛ neo4j_write
NPL ↛ kernel_mutation
```

### Depuis l'audio / entropie

```
❌ runtime authority pour thermodynamique cognitive
❌ X108-level invariant pour BUV ou entropie
❌ ACT/HOLD/BLOCK depuis entropie seule
❌ proof claim Lyapunov ou calibration énergétique
❌ claim médical ou psychologique (éducation, cognition humaine)
❌ "energy law proven" — entropie cognitive = théorie, pas loi
❌ manipulation cachée via scoring narratif
❌ "agi_subordination_spec.md est localisé" — ABSENT_UNDER_THIS_NAME
❌ "86 specs frozen" — FAUX, Plan 2 non exécuté
❌ "BUV est le gardien opérationnel" — sandbox uniquement
```

---

## PLAN 2 DELTA — Ce que l'audio impose pour Plan 2

### Specs audio déjà dans Plan 2 prévu (concordance)

| Spec audio | Compartiment Plan 2 | Statut |
|-----------|--------------------|---------| 
| ENTROPY_DISCIPLINE_SPEC.md | 03_ENTROPY_DISCIPLINE | ✅ Prévu |
| THERMODYNAMIC_DEBT_BOUNDARY.md | 03_ENTROPY_DISCIPLINE | ✅ Prévu |
| LYAPUNOV_RUNTIME_TO_FORMAL_PROOF_PLAN.md | 03_ENTROPY_DISCIPLINE | ✅ Prévu |
| BALANCE_ADMISSIBILITY_OPERATOR_SPEC.md | 05_BALANCE_BUV_GEOMETRIES | ✅ Prévu |
| COGNITIVE_TREE_DATA_LIFECYCLE.md | 04_AGI_TREE34_FLUX | ✅ Prévu |
| XYZ_COMPILATION_PIPELINE_SPEC.md | 02_INTERLAYER_CONSTITUTION | ✅ Prévu |
| AGI_SUBORDINATION_SPEC.md | 04_AGI_TREE34_FLUX | ✅ Prévu (à créer) |
| CRITICAL_WORLD_ADMISSION_SPEC.md | 09_CRITICAL_WORLDS | ✅ Prévu |
| VALUE_EMISSION_MODEL.md | 10_VALUE_GENCOIN_JCOIN | ✅ Prévu |
| OBSIDIA_INTERLAYER_CONSTITUTION.md | 02_INTERLAYER_CONSTITUTION | ✅ Prévu |

### Specs à ajouter au Plan 2 (issues de l'audio, absentes du plan)

| Spec nouvelle | Compartiment suggéré | Raison |
|--------------|---------------------|--------|
| SEMANTIC_HEAT_MONITORING_SPEC.md | 03_ENTROPY_DISCIPLINE | Concept clé de l'audio non encore prévu |
| ENTROPY_TO_X108_HOLD_RULE.md | 03_ENTROPY_DISCIPLINE | Interrupteur sémantique manquant |
| OBJECT_STATUS_LIFECYCLE.md | 02_INTERLAYER_CONSTITUTION | Mentionné explicitement dans l'audio |
| MACHINE_WORK_ORACLE_SPEC.md | 10_VALUE_GENCOIN_JCOIN | Oracle travail machine |

### NPL — intégration dans Plan 2

- NPL doit devenir **section 12** : `specs/12_NARRATIVE_PROVENANCE_LAYER/`
- Le pack fournit directement les 103 specs sources
- Ordre d'intégration : voir NPL_PACK_TO_EXISTING_SPECS_MAP.md

### Est-ce que l'audio impose une section Entropy Discipline renforcée ?

**OUI.** Le bloc `03_ENTROPY_DISCIPLINE` doit être étendu avec :
- SEMANTIC_HEAT_MONITORING_SPEC.md (manquant)
- ENTROPY_TO_X108_HOLD_RULE.md (interrupteur sémantique — manquant)

### Est-ce que .xyz impose une spec dédiée obligatoire ?

**OUI.** `XYZ_COMPILATION_PIPELINE_SPEC.md` est déjà prévu en `02_INTERLAYER_CONSTITUTION`.
C'est une priorité P1 — à créer avant tout pipeline workspace→runtime.

---

## PLAN 3 BLOCKERS — Blocages runtime identifiés

| Blocage | Pourquoi | Source | Résolution requise | Plan |
|---------|----------|--------|-------------------|------|
| No .xyz pipeline test | Aucun pipeline de conversion formalisé | Audio section 5 | XYZ_COMPILATION_PIPELINE_SPEC.md + test | Plan 2 d'abord |
| No semantic heat metric active | chaleur sémantique = théorie pure | Audio section 4 | SEMANTIC_HEAT_MONITORING_SPEC.md | Plan 2 |
| No entropy → HOLD test | Aucun interrupteur entropie actif | Audio section 4 | ENTROPY_TO_X108_HOLD_RULE.md | Plan 2 |
| No BUV no-decision test | BUV sandbox, non testé | Audio section 4 | BALANCE_ADMISSIBILITY_OPERATOR_SPEC.md + tests | Plan 2 |
| No Tree34 runtime admission test | non_decision_contract partiel | Audio section 5 | TREE34_RUNTIME_ADMISSION_SPEC.md | Plan 2 |
| No GPS no-actuator proof | GPS = signal only, pas de test | Audio section 4 | GPS_NO_ACT_WITHOUT_DECISIONTICKET.md | Plan 2 |
| No Gencoin anti-fake-work oracle | Smart contracts absents | Audio section 5 | MACHINE_WORK_ORACLE_SPEC.md + ANTI_FAKE_WORK | Plan 3/4 |
| No smart contract / tokenomics / legal | Gencoin = sandbox | Audio section 10 | Phase économique complète | Plan 4 |
| No OS3 production replay | replay_status=NOT_RUN | Audio section 5 | REPLAY_VERIFIER_PRODUCTION_SPEC.md | Plan 3 |
| No Lean proof P107/P161 | DOC_ONLY squelettes | P107/P161 audit | P107Proofs.lean + P161Proofs.lean | Plan 4+ |
| No interlayer constitution frozen | Spec absente | Audio section 8 | OBSIDIA_INTERLAYER_CONSTITUTION.md | Plan 2 |
| No spec registry frozen | specs/ vide | Audio section 9 | SPEC_REGISTRY.md + 86 specs | Plan 2 |
| NPL not branched runtime | Pack = SPEC_FUTURE | NPL Pack | Plan 2 specs → Plan 3 tests | Plan 3+ |
| AGI subordination spec absent | ABSENT_UNDER_THIS_NAME | Audio section 8 | AGI_SUBORDINATION_SPEC.md | Plan 2 |

---

## Recommandation finale

```
Plan 2 est le prerequis absolu de Plan 3.

Plan 3 Runtime Contract peut démarrer UNIQUEMENT après :
1. specs/SPEC_REGISTRY.md créé
2. Compartiments 00-03 de Plan 2 gelés (Scope + X108 Authority + Interlayer + Entropy)
3. NPL section 12 intégrée
4. Tests 08_TESTS_REQUIRED/ NPL exécutés
5. Blockers ci-dessus adressés en Plan 2

P107/P161 restent FORMAL_TARGET pour Plan 4+.
NPL reste SPEC_FUTURE jusqu'à Plan 2 complet.
```
