# F78B_NEXT_PHASE_RECOMMENDATION
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## État après F78B

F78B est complété avec verdict `F78B_SOURCE_PACKS_DEEP_DIFF_READY`.
Les décisions KEEP/INTEGRATE/ARCHIVE/QUARANTINE sont établies pour chaque pack.

---

## Collisions fortes détectées ?

| Collision | Gravité | Bloque |
|-----------|---------|--------|
| 37 RSSI_EXT vs specs/ | LOW (déjà importé) | NON |
| README.md x3 | TRIVIAL | NON |
| .pytest_cache Atlas | HAUTE | F06 uniquement (exclure lors import) |
| .runtime_freezes Atlas 92 dups | MOYENNE | F06 uniquement (archiver, pas bloquer) |
| 8 dups RGPD | FAIBLE | F03 uniquement (résoudre lors import) |
| 57 .py dans zips | **CRITIQUE** | F03/F06 (exclusions obligatoires) |
| packages/ 3 fichiers | HAUTE (historique) | Déjà résolu (DO_NOT_IMPORT) |

**Conclusion :** Pas de `F78B_COLLISION_RESOLUTION_DELTA` requis avant P4.
Les collisions sont traitables par exclusion lors de F03/F06/F07.
P4 peut démarrer.

---

## Option A — RECOMMANDÉE

### Étape 1 : P4 — Anti-bypass Tests SPEC

**Pourquoi P4 avant F03/F06/F07 :**
- P4 est SPEC_ONLY — pas d'import de packs
- P4 documente les tests anti-bypass sur la base des 13 boundaries existantes
- P4 ne dépend pas des packs non extraits
- P4 protège les imports futurs en établissant les tests dès maintenant

**Livrables P4 attendus :**
```
runtime_contracts/anti_bypass_tests/
  specs/ANTI_BYPASS_TEST_SPEC.md
  specs/PERIPHERY_SOVEREIGNTY_VIOLATION_SPEC.md
  specs/P107_P161_OVERAUTHORITY_TEST_SPEC.md
  specs/SOURCE_PACK_IMPORT_GUARD_TEST_SPEC.md
  mapping/BYPASS_VECTORS_TO_BOUNDARIES_MAP.md
  failure_modes/ANTI_BYPASS_TEST_FAILURE_MODES.md
  reports/PLAN3_P4_*.md
```

### Étape 2 : F07 — Cognitive Import

**Pourquoi F07 en premier parmi F03/F06/F07/F10 :**
- Pack le plus propre : 0 .py, 0 dups
- Structure claire : yaml principal + quelques md/json
- 519 fichiers — gérable en un seul run
- Boundary `COGNITIVE_REINTEGRATION_ADVISORY_ONLY` déjà créée en P1
- Risque minimal : pas de périphérie Python active

**Exclusions F07 :**
```
Aucune exclusion majeure nécessaire.
Vérifier uniquement : sha256 file + csv files
```

### Étape 3 : F03 — RSSI + RGPD Import

**Prérequis F03 :**
- Résoudre 8 dups RGPD (garder version riche)
- Exclure tous les `periphery/**/*.py` (39 fichiers total)
- Gérer DPA_TEMPLATE.md doublon entre les deux packs
- Boundaries `RSSI_EVIDENCE_ONLY` et `RGPD_COMPLIANCE_SCOPE_GUARD` déjà créées

**Exclusions F03 :**
```
periphery/rssi_security_pack/*.py (16 RSSI + 23 RGPD = 39 fichiers)
Renommer README.md → README_RSSI_SEC.md / README_RGPD_ISO.md
```

### Étape 4 : F06 — Atlas Import

**Prérequis F06 :**
- Complexité haute : 1738 fichiers
- Exclusions multiples : periphery/ + .pytest_cache + .runtime_freezes
- 92 dups basenames (snapshots) → sélection manuelle recommandée
- Boundary `ATLAS_READONLY_ADVISORY_ONLY` déjà créée

**Exclusions F06 :**
```
.pytest_cache/     → QUARANTINE
.runtime_freezes/  → RAW_ARCHIVE_ONLY (ne pas mettre dans specs/)
periphery/world_protocol_atlas/*.py (18 fichiers)
patches/*.py (SNIPPET_NOT_APPLIED mais .py)
92 dups → garder version V0_7 uniquement
```

### Étape 5 : F10 — RGPD Final Compliance

**Prérequis F10 :**
- F03 terminé ✓
- Review humaine des claims RGPD/ISO
- Boundary `RGPD_COMPLIANCE_SCOPE_GUARD` confirme : readiness ≠ certification légale

---

## Séquence finale recommandée

```
F78B ✅ (ce run)
  ↓
P4 — Anti-bypass SPEC (SPEC_ONLY — pas d'import)
  ↓
P5 — OS3 Evidence SPEC (SPEC_ONLY)
  ↓
P6 — Graphiti/Brody/NPL wrappers SPEC (SPEC_ONLY)
  ↓
F07 — Cognitive import (PROPRE — prioritaire)
  ↓
F03 — RSSI + RGPD import (exclure .py, résoudre dups)
  ↓
F06 — Atlas import (complexe — sélection manuelle)
  ↓
F10 — RGPD final compliance (après F03)
  ↓
P7 — Education benchmark SPEC (après F0x)
```

---

## Prérequis par phase

| Phase | Prérequis |
|-------|-----------|
| P4 | F78B ✅ |
| P5 | P4 ✅ |
| P6 | P5 ✅ (ou parallèle P5) |
| F07 | F78B ✅ |
| F03 | F78B ✅ + .py exclusion plan ✅ |
| F06 | F78B ✅ + .py exclusion + .pytest_cache plan ✅ |
| F10 | F03 ✅ |
| P7 | F07+F03+F06 ou parallèle |
