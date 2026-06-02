# CLAIM_SCOPE_WARNINGS
# OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1
# Date: 2026-06-02
# Couvre : Phase 5 NPL Audit + Phase 5 Audio Entropy Audit (Claim-Scope Corrections)
# Sources : NPL Pack + Fichier audio entropie

---

## Interdictions absolues

### Sur NPL

```
❌ "NPL prouve la provenance exacte d'une logique humaine"
   → Correction : NPL produit des hypothèses de provenance — jamais une certitude

❌ "NPL décide"
   → Correction : NPL est ADVISORY_ONLY — X-108 seul décide

❌ "NPL diagnostique un humain"
   → Correction : NPL produit un signal contextuel — pas un diagnostic médical ou psychologique

❌ "NPL remplace la sociologie / l'histoire / la psychologie"
   → Correction : NPL s'appuie sur ces disciplines comme EXTERNAL_REFERENCE_REGISTRY non souverain

❌ "NPL peut produire ALLOW / HOLD / BLOCK"
   → Correction : NPL ↛ ACT ; decision_authority = KX108_ONLY

❌ "Graphiti / Brody peuvent écrire ou décider via NPL"
   → Correction : NPL → Graphiti = readonly ContextPacket uniquement ; memory_write=false

❌ "Les métriques NPL sont des preuves formelles"
   → Correction : cultural_matrix_score, archive_gap_score, etc. = signaux probabilistes [0,1]

❌ "La mémoire vaincue est nécessairement vraie"
   → Correction : defeated_memory_signal = signal d'absence documentaire — hypothèse

❌ "Le vainqueur ment nécessairement"
   → Correction : winner_narrative_bias_score = signal contextuel — pas condamnation

❌ "archive_gap_score = preuve de manipulation"
   → Correction : absence de source ≠ preuve de censure — hypothèse ouverte

❌ "NPL peut transformer un mythe en preuve"
   → Correction : myth_as_memory_signal = signal mémoriel — jamais vérité formelle

❌ "victimhood_capture_risk indique qui est vraiment victime"
   → Correction : risque de romanticisation — jamais verdict d'identité

❌ "NPL est implémenté"
   → Correction : NPL = SPEC_FUTURE — aucun runtime actif
```

### Sur la calibration énergétique / thermodynamique

```
❌ "La calibration énergétique temporelle (P161) est prouvée"
   → Correction : P161_LEAN_SKELETON_ONLY — Python spec non testée, DOC_ONLY

❌ "La fonction de Lyapunov (P107) est formellement prouvée en Lean4"
   → Correction : P107_LEAN_SKELETON_ONLY — squelette trivial, hors lakefile

❌ "L'entropie cognitive est un invariant runtime prouvé"
   → Correction : Thermodynamique cognitive = théorie non formalisée — SPEC_TARGET_NOT_CREATED

❌ "La chaleur sémantique est mesurée"
   → Correction : semantic_heat = concept — aucun monitoring actif à ce jour

❌ "thermo_debt peut déclencher HOLD directement"
   → Correction : thermo_debt > θ influence un signal advisory uniquement — X-108 décide

❌ "Ces couches peuvent produire ACT/HOLD/BLOCK"
   → Correction : P107, P161, NPL, BUV = signaux advisory — decision_authority = KX108_ONLY
```

### Sur le fichier audio (sur-affirmations détectées)

| Phrase risquée dans l'audio | Correction stricte | Raison | Source locale |
|----------------------------|-------------------|--------|---------------|
| "agi_subordination_spec.md : déjà localisé et vérifié dans GitHub" | ABSENT_UNDER_THIS_NAME | Fichier inexistant sous ce nom exact | Glob sur repo |
| "geometries_canonical_index.md : déjà localisé" | ABSENT_UNDER_THIS_NAME | Inexistant (uniquement dans le pack NPL) | Glob sur repo |
| "buv_master_spec.md : déjà localisé" | ABSENT_UNDER_THIS_NAME | Inexistant (uniquement dans le pack NPL) | Glob sur repo |
| "critical_world_admission_spec.md : déjà localisé" | ABSENT_UNDER_THIS_NAME | Inexistant | Glob sur repo |
| "value_emission_model.md : déjà localisé" | ABSENT_UNDER_THIS_NAME | Inexistant | Glob sur repo |
| "obsidia_interlayer_constitution.md : déjà localisé" | ABSENT_UNDER_THIS_NAME | Inexistant | Glob sur repo |
| "SPEC_BUILD_READY: 86 specifications frozen" | FAUX — Plan 2 non exécuté | specs/ est vide | git status |
| "prototype fonctionnel actif" (BUV balance_operator.py) | Prototype sandbox uniquement | Non branché production | periphery/gencoin_sandbox/ |
| "La thermodynamique cognitive est un moteur" | C'est une méthodologie | Aucun runtime actif | Audio section 3 |
| "Gencoin = économie native" | Gencoin = modèle d'adossement sous spécification formelle | Smart contracts absents | periphery/gencoin.py = simulation |

---

## Formulations autorisées

### Sur NPL

```
✅ "NPL propose une lecture contextuelle de la provenance narrative"
✅ "NPL produit des hypothèses de provenance — jamais de vérité finale"
✅ "NarrativeProvenancePacket est readonly, advisory uniquement"
✅ "NPL est une cible de Plan 2 — SPEC_FUTURE / KX108_ONLY"
✅ "Les métriques NPL sont des signaux probabilistes [0,1]"
✅ "NPL peut enrichir le contexte de X-108 — pas l'autorité"
✅ "Les références académiques (Foucault, Gramsci, etc.) sont EXTERNAL_REFERENCE_REGISTRY non souverains"
```

### Sur l'entropie / énergie

```
✅ "Entropie et énergie cognitive sont des candidats de métriques périphériques"
✅ "P107/P161 restent des cibles formelles futures (Plan 4+)"
✅ "thermo_debt et L_value sont des signaux Python advisory avec label PYTHON_SPEC_NOT_LEAN_PROVEN"
✅ "La BUV est un opérateur de filtrage de cohérence — non un décideur"
✅ "Ces signaux peuvent enrichir le contexte, pas l'autorité de décision"
✅ "X-108 reste seul droit de passage pour tout ACT/HOLD/BLOCK"
✅ "La thermodynamique cognitive est une métaphore architecturale en cours de formalisation"
✅ "Gencoin est un modèle d'adossement productif sous spécification formelle — non prêt marché"
```

---

## Métriques NPL — statut non souverain confirmé

Toutes les métriques NPL sont `ADVISORY_ONLY` — elles ne peuvent pas déclencher une décision.

| Métrique | Type | Statut | Interdit |
|----------|------|--------|---------|
| cultural_matrix_score | float [0,1] | ADVISORY | ≠ verdict culturel |
| dominant_narrative_likelihood | float [0,1] | ADVISORY | ≠ "ce récit est vrai" |
| winner_narrative_bias_score | float [0,1] | ADVISORY | ≠ condamnation |
| archive_gap_signal_score | float [0,1] | ADVISORY | ≠ preuve de censure |
| source_asymmetry_score | float [0,1] | ADVISORY | ≠ manipulation prouvée |
| truth_regime_confidence | float [0,1] | ADVISORY | ≠ vérité absolue |
| common_sense_capture_score | float [0,1] | ADVISORY | ≠ "bon sens = faux" |
| hidden_transcript_likelihood | float [0,1] | ADVISORY | ≠ intention cachée prouvée |
| defeated_memory_signal_score | float [0,1] | ADVISORY | ≠ "mémoire vaincue = vraie" |
| external_power_gaze_score | float [0,1] | ADVISORY | ≠ jugement de culture |
| represented_by_self_score | float [0,1] | ADVISORY | ≠ verdict d'identité |
| forced_translation_risk_score | float [0,1] | ADVISORY | ≠ verdict de traduction |
| conceptual_metaphor_density | float [0,1] | ADVISORY | ≠ preuve cognitive |
| language_encoding_score | float [0,1] | ADVISORY | ≠ jugement linguistique |
| narrative_conflict_score | float [0,1] | ADVISORY | ≠ verdict de conflit |
| counter_archive_presence_score | float [0,1] | ADVISORY | ≠ preuve de contre-histoire |
| silence_signal_strength | float [0,1] | ADVISORY | ≠ preuve de censure |
| mythic_residue_score | float [0,1] | ADVISORY | ≠ "mythe = faux" |
| institutional_authority_weight | float [0,1] | ADVISORY | ≠ jugement d'institution |
| memory_fragmentation_score | float [0,1] | ADVISORY | ≠ diagnostic mémoriel |
| claim_provenance_confidence | float [0,1] | ADVISORY | ≠ certitude |
| historical_selection_pressure | float [0,1] | ADVISORY | ≠ verdict historique |
| official_memory_weight | float [0,1] | ADVISORY | ≠ vérité officielle |
| subaltern_voice_distortion_risk | float [0,1] | ADVISORY | ≠ "parler à la place de" |
| narrative_custody_score | float [0,1] | ADVISORY | ≠ propriété narrative |
| who_benefits_if_true_score | float [0,1] | ADVISORY | ≠ condamnation bénéficiaire |
| lost_futures_signal_score | float [0,1] | ADVISORY | ≠ "ce futur était juste" |
| naturalization_pressure_score | float [0,1] | ADVISORY | ≠ verdict de naturalisation |
| autonym_exonym_gap_score | float [0,1] | ADVISORY | ≠ jugement d'identité |
| official_language_frame_score | float [0,1] | ADVISORY | ≠ verdict linguistique |
| counter_archive_quality_score | float [0,1] | ADVISORY | ≠ validation contre-archive |
| myth_as_memory_signal_score | float [0,1] | ADVISORY | ≠ vérité du mythe |
| victimhood_capture_risk_score | float [0,1] | ADVISORY | ≠ verdict de victimisation |
| time_depth_confidence | float [0,1] | ADVISORY | ≠ certitude temporelle |
| narrative_time_depth_score | float [0,1] | ADVISORY | ≠ verdict d'ancienneté |
| custody_break_count | int | ADVISORY | ≠ preuve de rupture |
| official_vs_self_naming_conflict_score | float [0,1] | ADVISORY | ≠ verdict d'identité |
