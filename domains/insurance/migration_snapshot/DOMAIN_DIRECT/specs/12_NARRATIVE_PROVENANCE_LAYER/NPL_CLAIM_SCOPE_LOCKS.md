# NPL_CLAIM_SCOPE_LOCKS

Status: SPEC_FUTURE
Authority: KX108_ONLY
Runtime Status: SPEC_ONLY
Decision Status: NON_SOVEREIGN

---

## Source

Audit : `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/CLAIM_SCOPE_WARNINGS.md`
Pack NPL : `OBSIDIA_NARRATIVE_PROVENANCE_LAYER_SPEC_PACK_V1_MAX/CLAIM_SCOPE_LIMITS.md`

---

## Scope

Verrouiller les claims interdits et autorisés sur NPL.
Ce fichier est la référence de claim-scope pour toute communication externe sur NPL.

---

## Claims INTERDITS — NPL

```
❌ "NPL prouve la provenance exacte d'une logique humaine"
❌ "NPL décide"
❌ "NPL diagnostique un humain"
❌ "NPL remplace la sociologie / l'histoire / la psychologie"
❌ "NPL peut produire ALLOW / HOLD / BLOCK"
❌ "Graphiti / Brody peuvent écrire ou décider via NPL"
❌ "Les métriques NPL sont des preuves formelles"
❌ "La mémoire vaincue est nécessairement vraie"
❌ "Le vainqueur ment nécessairement"
❌ "archive_gap_score = preuve de manipulation"
❌ "NPL peut transformer un mythe en preuve"
❌ "victimhood_capture_risk indique qui est vraiment victime"
❌ "NPL est implémenté"
❌ "NPL est branché au runtime"
❌ "NPL est branché Sigma actif"
❌ "NPL écrit Graphiti"
❌ "NPL écrit Neo4j"
❌ "NPL détecte la vérité historique"
❌ "NPL décide quel récit est faux"
❌ "NPL prouve qu'un vainqueur ment"
❌ "NPL transforme un mythe en preuve"
❌ "NPL remplace X-108"
❌ "NPL est une preuve formelle"
```

## Claims AUTORISÉS — NPL

```
✅ "NPL propose une lecture contextuelle de la provenance narrative"
✅ "NPL produit des hypothèses de provenance — jamais de vérité finale"
✅ "NarrativeProvenancePacket est readonly, advisory uniquement"
✅ "NPL est une cible de Plan 2 — SPEC_FUTURE / KX108_ONLY"
✅ "Les métriques NPL sont des signaux probabilistes [0,1]"
✅ "NPL peut enrichir le contexte de X-108 — pas l'autorité"
✅ "Les références académiques (Foucault, Gramsci...) sont DOC_ONLY non souverains"
✅ "NPL expose depuis quelle chaîne narrative un récit semble parler"
```

---

## Métriques — statut non souverain

Toutes les métriques NPL sont `ADVISORY_ONLY`. Aucune ne peut déclencher une décision.

| Métrique | Type | Interdit |
|----------|------|---------|
| cultural_matrix_score | float [0,1] | ≠ verdict culturel |
| dominant_narrative_likelihood | float [0,1] | ≠ "ce récit est vrai" |
| archive_gap_signal_score | float [0,1] | ≠ preuve de censure |
| truth_regime_confidence | float [0,1] | ≠ vérité absolue |
| who_benefits_if_true_score | float [0,1] | ≠ condamnation |
| victimhood_capture_risk_score | float [0,1] | ≠ verdict de victimisation |
| narrative_custody_score | float [0,1] | ≠ propriété narrative |

Voir `NPL_METRICS_ADVISORY_ONLY.md` pour la liste complète des 37 métriques.

---

## Invariants

- NPL ↛ décision
- NPL → hypothèse de provenance uniquement
- decision_authority = KX108_ONLY

## X108 Boundary

KX108_ONLY — NPL ne peut pas remplacer X-108

## Claim-Scope Notes

Ce fichier complète `NPL_CLAIM_SCOPE_LIMITS.md` (vue générale) avec les locks
issus des audits P107/P161 et NPL Pack de 2026-06-02.
