# NPL_CLAIM_SCOPE_WARNINGS
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION
# Date: 2026-06-02

---

## Interdictions publiques absolues

| Ce qui est interdit | Pourquoi |
|---------------------|---------|
| "NPL prouve la provenance réelle d'une pensée" | NPL propose des hypothèses de provenance — jamais de certitudes |
| "NPL détecte objectivement la vérité culturelle" | La vérité culturelle n'est pas un objet mesurable — NPL fournit des signaux probabilistes |
| "NPL sait ce que pense vraiment l'humain" | Impossible — NPL ne lit pas l'intention, il trace des patterns de surface |
| "NPL diagnostique un trauma" | NPL n'est pas un outil clinique — aucune autorité médicale ou psychologique |
| "NPL remplace historien, sociologue, psychologue" | NPL est un signal périphérique — ces disciplines restent souveraines |
| "NPL décide" | INTERDIT ABSOLU — `KX108_ONLY` pour toute décision |
| "NPL corrige moralement l'humain" | NPL ne peut pas émettre de verdict moral — `NO_VERDICT_FINAL` |
| "NPL sait quelle culture est dominante" | NPL détecte des patterns — il ne juge pas la légitimité d'une culture |
| "NPL détecte le mensonge" | NPL détecte des signaux d'incohérence — pas de verdict de mensonge |
| "NPL est une vérité" | NPL est un signal contextuel avec incertitude explicite |
| "Gramsci / Foucault / Trouillot prouvent X dans ce contexte" | Les courants externes sont des références, pas des autorités dans Obsidia |
| "Berger-Luckmann prouve que cette réalité est construite" | Référence bibliographique, pas preuve algorithmique |
| "L'archive gap confirme qu'il y a eu manipulation" | Archive gap = signal d'absence — hypothèse, pas confirmation |
| "La mémoire vaincue est la vraie vérité" | NPL ne hiérarchise pas les vérités — il expose des courants multiples |
| "NPL peut écrire mémoire" | NON sans gate humain explicite — `NO_MEMORY_WRITE` par défaut |
| "NPL peut passer dans le kernel" | INTERDIT — `NO_KERNEL_MUTATION` |

---

## Formulations autorisées

| Formulation | Statut |
|-------------|--------|
| "NPL propose une lecture contextuelle de provenance narrative" | AUTORISÉ |
| "NPL détecte des signaux possibles de matrice culturelle" | AUTORISÉ |
| "NPL trace des hypothèses de provenance — incertitude explicite" | AUTORISÉ |
| "NPL expose les courants culturels identifiables dans un signal" | AUTORISÉ |
| "NPL est readonly et non souverain" | AUTORISÉ |
| "NPL produit uniquement contexte, signal, hypothèse, audit" | AUTORISÉ |
| "X108 reste l'autorité si une action est demandée" | AUTORISÉ |
| "Les courants externes (Foucault, etc.) sont des références — pas des preuves" | AUTORISÉ |
| "NPL ne remplace aucune discipline humaine" | AUTORISÉ |
| "NPL_confidence_score = probabilité estimée — pas certitude" | AUTORISÉ |

---

## Risques de dilution par bloc

### Bloc A — NPL Core
- Risque principal : présenter NPL comme une couche d'analyse objective
- Garde : `PERIPHERAL_READONLY`, `ADVISORY_ONLY`, `KX108_BOUNDARY_REQUIRED`

### Bloc B — Packets
- Risque principal : transformer un packet en verdict (ex. TRUTH_REGIME_PACKET → "cette culture est la vraie")
- Garde : chaque packet doit inclure `provenance_uncertainty` et `manipulation_risk_signal`

### Bloc C — Concepts
- Risque : `LOGIC_AS_CULTURE_COMPRESSED` → "donc sa logique est fausse"
- Garde : la culture compressée explique sans juger — `NO_VERDICT_FINAL`

### Bloc D — Courants externes
- Risque MAJEUR : présenter Foucault ou Gramsci comme preuve algorithmique
- Garde : `EXTERNAL_REFERENCE_REGISTRY`, `DOC_ONLY`, `NO_AUTHORITY`, `NO_DECISION`
- Règle : ces auteurs informent la spec, ils ne fondent pas le runtime

### Bloc E — Branchements
- Risque : `NPL_TO_GRAPHITI` → Graphiti écrit des vérités culturelles non validées
- Garde : `NO_GRAPHITI_WRITE`, `NO_MEMORY_WRITE` sauf gate humain

### Bloc F — Métriques
- Risque : `winner_bias_score = 0.9` présenté comme "preuve de manipulation"
- Garde : score = signal probabiliste — jamais verdict

### Bloc G — Tests
- Risque : créer des tests qui "prouvent" une thèse culturelle
- Garde : tests de non-décision uniquement — `test_no_decision_authority`, `test_no_act_emission`

---

## Garde-fous RSSI / Non-manipulation

```
NPL_RSSI_NON_MANIPULATION = {
    "can_modify_memory": False,
    "can_emit_act": False,
    "can_emit_verdict": False,
    "can_diagnose": False,
    "can_moralize": False,
    "can_claim_cultural_truth": False,
    "can_override_human_judgment": False,
    "requires_human_gate_before_write": True,
    "external_references": "REGISTRY_ONLY_NOT_AUTHORITY"
}
```

---

## Note sur le diagnostic psychologique implicite

NPL ne peut pas produire de signal qui ressemble à un diagnostic :
- "ce signal indique un trauma" → INTERDIT
- "ce pattern suggère une blessure identitaire" → INTERDIT sauf si encadré explicitement comme hypothèse probabiliste avec `provenance_uncertainty > 0.7` et `needs_human_validation = True`

NPL peut uniquement dire :
- "signal détecté dans la zone T05 (Identité) — incertitude = X%"
- "pattern cohérent avec mémoire vaincue — hypothèse uniquement"
