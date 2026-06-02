# NPL_MISSING_SOURCE_WARNINGS
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1 — NPL EXTENSION
# Date: 2026-06-02

> Éléments absents sous le nom exact. Source alternative indiquée si applicable.

---

## ABSENT_UNDER_THIS_NAME (tous les concepts NPL nommés)

### NPL_CANONICAL_SPEC
- **Absent exact** : OUI — aucun fichier `NPL_CANONICAL_SPEC.md` ou équivalent
- **Trouvé sous autre nom** : NON
- **Source alternative** : texte utilisateur + `docs/PROOF_SCOPE.md` (modèle de structure canonique)
- **Action Plan 2** : Créer `specs/npl/NPL_CANONICAL_SPEC.md` — P0

### HUMAN_LOGIC_PACKET_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : Partiellement → `periphery/context/context_packet_builder_v2.py` (ContextPacket avec decision_authority, allowed_to_decide)
- **Source alternative** : ContextPacket V2 est le récepteur — HumanLogicPacket serait une extension
- **Action Plan 2** : `specs/npl/HUMAN_LOGIC_PACKET_SPEC.md` — P0

### NARRATIVE_PROVENANCE_PACKET_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON (concept totalement nouveau)
- **Source alternative** : `periphery/ingestion/document_ingestion_pipeline.py` (IngestedDocument avec source_class, content_hash) — récepteur partiel
- **Action Plan 2** : `specs/npl/NARRATIVE_PROVENANCE_PACKET_SPEC.md` — P0

### CULTURAL_MATRIX_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : `periphery/OBSIDIA_MMONDE.../04_ARBRES_34.../ARBRE_19__Arbre_de_la_Culture/` (activation_rules.md, non_decision_contract.md)
- **Source alternative** : Tree19 est le récepteur culturel — Cultural Matrix serait la matrice d'entrée
- **Action Plan 2** : `specs/npl/CULTURAL_MATRIX_SPEC.md` — P1

### TRUTH_REGIME_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : `ARBRE_27__Arbre_de_la_Verite/` (non_decision_contract.md présent)
- **Source alternative** : Tree27 = récepteur du signal de régime de vérité
- **Action Plan 2** : `specs/npl/TRUTH_REGIME_SPEC.md` — P1

### ARCHIVE_GAP_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON — concept entièrement nouveau
- **Source alternative** : `ARBRE_25__Arbre_de_l_Histoire/` (activation_rules.md) — récepteur Histoire
- **Action Plan 2** : `specs/npl/ARCHIVE_GAP_SPEC.md` — P1

### WINNER_NARRATIVE_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON
- **Source alternative** : Tree25 (Histoire) + Tree27 (Vérité) comme récepteurs
- **Action Plan 2** : `specs/npl/WINNER_NARRATIVE_SPEC.md` — P1

### DEFEATED_MEMORY_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON
- **Source alternative** : Tree24 (Mémoire) + Tree25 (Histoire) comme récepteurs
- **Action Plan 2** : `specs/npl/DEFEATED_MEMORY_SPEC.md` — P1

### COMMON_SENSE_CAPTURE_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : `periphery/bias/bias_gate.py` — intercepte le biais non validé (y compris "bon sens" présenté comme vérité)
- **Source alternative** : BiasGate est le récepteur partiel
- **Action Plan 2** : `specs/npl/COMMON_SENSE_CAPTURE_SPEC.md` — P2

### HIDDEN_TRANSCRIPT_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON
- **Source alternative** : `periphery/context/context_packet_builder_v2.py` (`forbidden_tokens_detected`, `contradictions`) — détection partielle
- **Action Plan 2** : `specs/npl/HIDDEN_TRANSCRIPT_SPEC.md` — P2

### CONCEPTUAL_METAPHOR_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON (Lakoff/Johnson absent du repo)
- **Source alternative** : Tree04 (Sens) + Tree08 (Pensée) comme récepteurs
- **Action Plan 2** : `specs/npl/CONCEPTUAL_METAPHOR_SPEC.md` — P2

### COLLECTIVE_MEMORY_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : Tree24 (Mémoire) + `MEMOIRE_PERSONNELLE_OBSIDIA` agent
- **Source alternative** : Tree24 activation_rules.md + agents_52 MEMOIRE_PERSONNELLE
- **Action Plan 2** : `specs/npl/COLLECTIVE_MEMORY_SPEC.md` — P2

### SUBALTERN_VOICE_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON (Spivak absent)
- **Source alternative** : Archive gap + mémoire vaincue comme contexte d'entrée
- **Action Plan 2** : `specs/npl/SUBALTERN_VOICE_SPEC.md` — P3

### PARADIGM_FRAME_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : Tree14 (Philosophie) + Tree27 (Vérité) comme récepteurs
- **Source alternative** : Trees 14 + 27 activation_rules.md
- **Action Plan 2** : `specs/npl/PARADIGM_FRAME_SPEC.md` — P3

### FUTURES_LOST_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON — concept entièrement nouveau
- **Source alternative** : Tree23 (Temps) + Tree29 (Finalité) comme récepteurs potentiels
- **Action Plan 2** : `specs/npl/FUTURES_LOST_SPEC.md` — P3

### OFFICIAL_MEMORY_VS_WARM_MEMORY_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : NON
- **Source alternative** : Tree24 (Mémoire) + Tree25 (Histoire) comme récepteurs
- **Action Plan 2** : `specs/npl/OFFICIAL_VS_WARM_MEMORY_SPEC.md` — P2

### NPL_TO_X108_BOUNDARY_SPEC
- **Absent exact** : OUI
- **Trouvé sous autre nom** : `periphery/x108_ingress/readonly_context_ingress.py` (`can_emit_act=False`, `can_write_memory=False`) — récepteur existant
- **Source alternative** : X108_READONLY_INGRESS est le récepteur exact
- **Action Plan 2** : `specs/npl/NPL_TO_X108_BOUNDARY_SPEC.md` — P0

---

## SOURCE_FOUND_UNDER_DIFFERENT_NAME (récepteurs NPL existants)

| Concept NPL | Récepteur Obsidia existant | Fichier | Statut |
|-------------|---------------------------|---------|--------|
| Context / X108 ingress | `X108ContextIngress` | `periphery/x108_ingress/readonly_context_ingress.py` | RUNTIME_CODE + READONLY |
| Cultural activation | Tree19 Culture | `.../ARBRE_19__Arbre_de_la_Culture/` | DOC_ONLY + non_decision_contract |
| Memory signal | Tree24 Mémoire | `.../ARBRE_24__Arbre_de_la_Memoire/` | DOC_ONLY + non_decision_contract |
| History signal | Tree25 Histoire | `.../ARBRE_25__Arbre_de_l_Histoire/` | DOC_ONLY + non_decision_contract |
| Truth regime | Tree27 Vérité | `.../ARBRE_27__Arbre_de_la_Verite/` | DOC_ONLY + non_decision_contract |
| Language encoding | Tree10 Langage + `language_router.py` | `.../ARBRE_10__Arbre_du_Langage/` + `periphery/language/language_router.py` | DOC_ONLY + RUNTIME_CODE |
| Bias / common sense intercept | `bias_gate.py` | `periphery/bias/bias_gate.py` | RUNTIME_CODE |
| Education / blockage | `education_score.py` | `periphery/education/education_score.py` | RUNTIME_CODE + ADVISORY_ONLY |
| Document provenance | `document_ingestion_pipeline.py`, `source_classifier.py` | `periphery/ingestion/` | RUNTIME_CODE |
| Action projection (readonly) | `action_projection_readonly.py` | `periphery/reverse_os/` | RUNTIME_CODE + ADVISORY_ONLY |
| Full context packet | `context_packet_builder_v2.py` | `periphery/context/` | RUNTIME_CODE |
| OS Trad / IR | `language_router.py` + `OS_TRAD_REVERSE_IR_DISCOVERY_REPORT.md` | `periphery/language/`, `apps/obsidia-workbench/` | RUNTIME_CODE + DOC_ONLY |
| Agent mémoire | `MEMOIRE_PERSONNELLE_OBSIDIA` | `agents_52.registry.json` | SOURCE_CANON (registry) |
| Agent histoire humaine | `HUMAN_HISTORY_MAPPER`, `FRISE_HUMAINE` | `agents_52.registry.json` | SOURCE_CANON (registry) |
| Agent vocabulaire | `VOCABULAIRE_CANONIQUE` | `agents_52.registry.json` | SOURCE_CANON (registry) |
| Agent théorie vivante | `THEORIE_VIVANTE` | `agents_52.registry.json` | SOURCE_CANON (registry) |
| Agent recherche externe | `RECHERCHE_EXTERNE` | `agents_52.registry.json` | SOURCE_CANON (registry) |
| Agent ontologie | `ONTOLOGUE_OBSIDIA` | `agents_52.registry.json` | SOURCE_CANON (registry) |
