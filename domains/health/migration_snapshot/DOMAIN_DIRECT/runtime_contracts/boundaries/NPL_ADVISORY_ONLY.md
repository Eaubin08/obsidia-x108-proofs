# NPL_ADVISORY_ONLY
# runtime_contracts/boundaries/NPL_ADVISORY_ONLY.md
# Status: CONTRACT_SKELETON_ONLY
# Source: specs/12_NARRATIVE_PROVENANCE_LAYER/NPL_TO_PLAN3_CONSTRAINTS.md

---

## 1. Boundary Statement

```
NPL = PROVENANCE_HYPOTHESIS_ONLY
NPL ↛ ACT
NPL ↛ ALLOW / HOLD / BLOCK
NPL ↛ truth_final / historical_truth / moral_verdict
NPL ↛ memory_write
NPL ↛ graphiti_write
NPL ↛ neo4j_write
NPL ↛ kernel_mutation
NPL ↛ diagnosis (médical / psychologique)
NPL → ContextPacket readonly advisory
NPL → NarrativeProvenancePacket readonly advisory
decision_authority = KX108_ONLY
```

---

## 2. Applies To

NPL (Narrative Provenance Layer) — SPEC_FUTURE :
- 37 métriques [0,1] toutes ADVISORY_ONLY
- NarrativeProvenancePacket readonly
- ContextPacket enrichi advisory
- Signaux : cultural_matrix_score, archive_gap_signal_score, truth_regime_confidence, etc.
- Sources académiques : Foucault, Gramsci, Trouillot, Said, Spivak, etc. (DOC_ONLY — non souverains)

---

## 3. Allowed

- Produire NarrativeProvenancePacket avec `advisory_only=true`, `emits_verdict=false`
- Enrichir ContextPacket avec métriques NPL labellisées `NPL_ADVISORY_NOT_SOVEREIGN`
- Signaler archive_gap, truth_regime, hidden_transcript, naturalization_pressure
- Exposer depuis quelle chaîne narrative un récit semble parler (hypothèse, jamais certitude)

---

## 4. Forbidden

```
❌ "NPL prouve la provenance exacte d'une logique humaine"
❌ "NPL décide" — jamais
❌ "NPL diagnostique un humain" — aucun diagnostic
❌ "NPL remplace la sociologie / l'histoire / la psychologie"
❌ "NPL peut produire ALLOW / HOLD / BLOCK"
❌ "archive_gap_score = preuve de manipulation"
❌ "defeated_memory = vérité"
❌ "NPL est implémenté" — SPEC_FUTURE uniquement
❌ Écrire mémoire / Graphiti / Neo4j
```

---

## 5. Failure Mode

- Label `NPL_ADVISORY_NOT_SOVEREIGN` manquant → `label_missing_flag` → X108 pénalise
- `emits_verdict = true` depuis NPL → violation
- `confidence = 1.0` sans LEAN_PROVEN → `overconfidence_flag`

---

## 6. Required Contract Fields

- `labels: ["NPL_ADVISORY_NOT_SOVEREIGN"]` dans ContextPacket si source=npl
- `advisory_only: true`, `emits_act: false`, `emits_verdict: false`
- `decision_authority: "KX108_ONLY"`

---

## 7. Required Future Tests (Phase P6)

- `test_npl_no_decision_authority`
- `test_npl_packet_readonly`
- `test_npl_metrics_advisory`
- `test_npl_graphiti_write_forbidden`

---

## 8. Proof Expectation

- Python test : validation schema + label enforcement
- Récepteurs Tree34 existants : non_decision_contract (arbres 10, 17, 18, 19, 24, 25, 27)

---

## 9. Claim-Scope

**Autorisé :**
- "NPL expose depuis quelle chaîne narrative un récit semble parler — hypothèse uniquement"
- "Les 37 métriques NPL sont des signaux probabilistes [0,1] advisory"
- "NPL est SPEC_FUTURE — non encore implémenté"

**Interdit :** Tout claim de vérité, diagnostic, décision, ou preuve depuis NPL.

---

## 10. Example Violation

```python
# VIOLATION
if npl.cultural_matrix_score > 0.8:
    memory.write("cultural_verdict", "dominant_culture")  # ← VIOLATION
```

---

## 11. Correct Handling

```python
# CORRECT
packet = ContextPacket(
    source_layer="npl", advisory_only=True, emits_verdict=False,
    labels=["NPL_ADVISORY_NOT_SOVEREIGN"],
    context_payload={"cultural_matrix_score": 0.63, "_npl_can_decide": False}
)
# → X108 reçoit le contexte NPL et décide
```
