# NPL_PACK_TO_EXISTING_SPECS_MAP
# OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1
# Date: 2026-06-02
# Couvre : Phase 2 NPL Audit + Phase 2 Audio Entropy Audit

---

## Sources existantes lues

| Source | Statut |
|--------|--------|
| `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_SOURCE_DISCOVERY_REPORT.md` | ✅ Présent |
| `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_SOURCE_TO_SPEC_MAPPING.md` | ✅ Présent |
| `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/NPL_PLAN2_INPUT_MATRIX.md` | ✅ Présent |
| `specs/PLAN2_SPEC_FREEZE_REPORT.md` | ❌ Absent (Plan 2 non encore exécuté) |
| `specs/SPEC_REGISTRY.md` | ❌ Absent (Plan 2 non encore exécuté) |

---

## Classement de chaque bloc NPL du pack

### A. ALREADY_COVERED_BY_PLAN1_BIS (Source Discovery existant)

| Bloc NPL | Couvert par | Fichier source discovery |
|----------|------------|--------------------------|
| NPL concept général | NPL_SOURCE_DISCOVERY_REPORT.md | `OBSIDIA_SOURCE_DISCOVERY_MAP_V1_NPL_EXTENSION/` |
| NPL → Graphiti readonly | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc E | idem |
| NPL → Brody context | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc E | idem |
| NPL → Tree34 (arbres 10,17,18,19,24,25,27) | NPL_PLAN2_INPUT_MATRIX.md | idem |
| NPL → OS Trad IR | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc E | idem |
| NPL → Sigma advisory | NPL_PLAN2_INPUT_MATRIX.md | idem |
| Claim-scope NPL | NPL_CLAIM_SCOPE_WARNINGS.md | idem |
| Sources manquantes NPL | NPL_MISSING_SOURCE_WARNINGS.md | idem |

### B. NEW_SPEC_CANDIDATE (apporté par le pack, absent du Source Discovery)

| Bloc NPL | Fichier dans le pack | Priorité | Notes |
|----------|---------------------|----------|-------|
| NARRATIVE_CUSTODY_CHAIN | 11_ADVANCED_PROVENANCE/NARRATIVE_CUSTODY_CHAIN_SPEC.md | P1 | Nouveau concept non dans Source Discovery |
| WHO_BENEFITS_IF_TRUE | 11_ADVANCED_PROVENANCE/WHO_BENEFITS_IF_TRUE_SPEC.md | P1 | Nouveau — audit de bénéficiaire du récit |
| LOST_FUTURES_SIGNAL | 11_ADVANCED_PROVENANCE/LOST_FUTURES_SIGNAL_SPEC.md | P2 | Nouveau — possibles non actualisés |
| NATURALIZATION_PRESSURE | 11_ADVANCED_PROVENANCE/NATURALIZATION_PRESSURE_SPEC.md | P2 | Nouveau — pression de naturalisation |
| AUTONYM_EXONYM_GAP | 11_ADVANCED_PROVENANCE/AUTONYM_EXONYM_GAP_SPEC.md | P2 | Nouveau — écart auto/exo-nommage |
| OFFICIAL_LANGUAGE_FRAME | 11_ADVANCED_PROVENANCE/OFFICIAL_LANGUAGE_FRAME_SPEC.md | P2 | Nouveau — cadrage langue officielle |
| COUNTER_ARCHIVE_QUALITY | 11_ADVANCED_PROVENANCE/COUNTER_ARCHIVE_QUALITY_SPEC.md | P2 | Nouveau — qualité contre-archive |
| MYTH_AS_MEMORY_BOUNDARY | 11_ADVANCED_PROVENANCE/MYTH_AS_MEMORY_BOUNDARY_SPEC.md | P2 | Nouveau — mythe comme signal mémoriel |
| VICTIMHOOD_CAPTURE_RISK | 11_ADVANCED_PROVENANCE/VICTIMHOOD_CAPTURE_RISK_SPEC.md | P1 | CRITIQUE — risque de capture idéologique |
| TIME_DEPTH_CONFIDENCE | 11_ADVANCED_PROVENANCE/TIME_DEPTH_CONFIDENCE_SPEC.md | P2 | Nouveau — confiance temporelle |
| Matrices de tests NPL | 08_TESTS_REQUIRED/*.md | P0 | Tests requis formalisés — absents du Source Discovery |
| Risques adversariaux | 07_ADVERSARIAL_RISKS/*.md | P1 | 7 risques spécifiques formalisés |
| MANIFEST_SHA256 | MANIFEST_SHA256.json | P0 | Intégrité du pack — nouveau |

### C. SOURCE_ONLY_REFERENCE (ne pas importer en runtime)

| Bloc NPL | Fichier | Raison |
|----------|---------|--------|
| Berger-Luckmann | 10_EXTERNAL_REFERENCES/BERGER_LUCKMANN_SOCIAL_CONSTRUCTION.md | DOC_ONLY, EXTERNAL_REFERENCE_REGISTRY |
| Foucault | 10_EXTERNAL_REFERENCES/FOUCAULT_TRUTH_REGIME.md | DOC_ONLY |
| Gramsci | 10_EXTERNAL_REFERENCES/GRAMSCI_CULTURAL_HEGEMONY.md | DOC_ONLY |
| Trouillot | 10_EXTERNAL_REFERENCES/TROUILLOT_ARCHIVE_SILENCING.md | DOC_ONLY |
| Halbwachs/Assmann | 10_EXTERNAL_REFERENCES/HALBWACHS_ASSMANN_COLLECTIVE_MEMORY.md | DOC_ONLY |
| James Scott | 10_EXTERNAL_REFERENCES/JAMES_SCOTT_HIDDEN_TRANSCRIPTS.md | DOC_ONLY |
| Edward Said | 10_EXTERNAL_REFERENCES/EDWARD_SAID_EXTERNAL_POWER_GAZE.md | DOC_ONLY |
| Spivak | 10_EXTERNAL_REFERENCES/SPIVAK_SUBALTERN_VOICE_BOUNDARY.md | DOC_ONLY |
| Lakoff/Johnson | 10_EXTERNAL_REFERENCES/LAKOFF_JOHNSON_CONCEPTUAL_METAPHOR.md | DOC_ONLY |
| Kuhn | 10_EXTERNAL_REFERENCES/KUHN_PARADIGM_FRAME.md | DOC_ONLY |

### D. DUPLICATE_RICHER_THAN_EXISTING

| Bloc NPL | Doublon avec | Plus riche car |
|----------|-------------|----------------|
| NPL_MASTER_BOUNDARY.md | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc A | Inclut NPL_RUNTIME_EXCLUSION_SPEC + KX108_AUTHORITY_MAPPING |
| NPL_TO_X108_BOUNDARY_SPEC.md (pack) | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc A | Inclut exemples de packets + règles de validation |
| NPL_TO_GRAPHITI_CONTEXT_PACKET_SPEC.md | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc E | Plus détaillé : 7012 bytes vs référence courte |
| NPL_TO_OS_TRAD_IR_PACKET_SPEC.md | NPL_SOURCE_TO_SPEC_MAPPING.md Bloc E | Plus détaillé : 6994 bytes |
| CLAIM_SCOPE_LIMITS.md (pack) | NPL_CLAIM_SCOPE_WARNINGS.md | Plus complet : couvre 11_ADVANCED_PROVENANCE |

### E. CLAIM_SCOPE_RISK

| Bloc | Risque | Mitigation dans le pack |
|------|--------|------------------------|
| VICTIMHOOD_CAPTURE_RISK | NPL pourrait romanticiser la mémoire vaincue | Explicitement documenté dans 07_ADVERSARIAL_RISKS/ |
| NPL_FALSE_HISTORY_RISK | NPL pourrait sembler valider une version de l'histoire | NPL_TRUTH_VERDICT_FORBIDDEN_RISK.md |
| NPL_IDEOLOGICAL_CAPTURE_RISK | NPL pourrait être capturé par un cadre idéologique | NPL_IDEOLOGICAL_CAPTURE_RISK.md |
| ARCHIVE_GAP_OVERINTERPRETATION | L'absence d'archive ≠ preuve de censure | NPL_ARCHIVE_GAP_OVERINTERPRETATION_RISK.md |

### F. DO_NOT_IMPORT_RUNTIME

| Bloc | Raison |
|------|--------|
| Toute la section 10_EXTERNAL_REFERENCES/ | DOC_ONLY — théories académiques non souveraines |
| 08_TESTS_REQUIRED/ | Tests requis = spec, pas runtime — à implémenter en Plan 3/4 |
| MANIFEST_SHA256.json | Intégrité du pack seulement — ne pas exposer en API |
| VALIDATION_REPORT.md | Rapport d'audit interne — ne pas exposer |

---

## Verdict mapping

```
NPL pack couvre et enrichit le Source Discovery V1 :
- Plan 1 Bis couvrait le noyau NPL (concepts, branchements, claim-scope)
- Le pack ajoute 11_ADVANCED_PROVENANCE (10 specs nouvelles), 07_ADVERSARIAL_RISKS (7),
  08_TESTS_REQUIRED (7), et MANIFEST_SHA256

Recommandation : ADD_TO_PLAN2_AS_SECTION_12
Ordre d'intégration dans Plan 2 :
  1. 01_MASTER_SPEC/ → specs/12_NARRATIVE_PROVENANCE_LAYER/00_MASTER/
  2. 04_PACKET_SCHEMA/ → specs/12_NARRATIVE_PROVENANCE_LAYER/01_PACKETS/
  3. 05_METRICS/ → specs/12_NARRATIVE_PROVENANCE_LAYER/02_METRICS/
  4. 02_CORE_CONCEPTS/ + 03_SIGNALS/ → specs/12_NARRATIVE_PROVENANCE_LAYER/03_CONCEPTS/
  5. 11_ADVANCED_PROVENANCE/ → specs/12_NARRATIVE_PROVENANCE_LAYER/04_ADVANCED/
  6. 06_OBSIDIA_BRANCHING/ → specs/12_NARRATIVE_PROVENANCE_LAYER/05_BRANCHING/
  7. 07_ADVERSARIAL_RISKS/ + 08_TESTS_REQUIRED/ → specs/12_NARRATIVE_PROVENANCE_LAYER/06_RISKS_TESTS/
  8. 10_EXTERNAL_REFERENCES/ → specs/12_NARRATIVE_PROVENANCE_LAYER/07_REFERENCES/ (DOC_ONLY)
```
