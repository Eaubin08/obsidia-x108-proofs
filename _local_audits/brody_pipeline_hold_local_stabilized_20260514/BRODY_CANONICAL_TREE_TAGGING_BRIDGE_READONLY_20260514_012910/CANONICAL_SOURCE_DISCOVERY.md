# CANONICAL SOURCE DISCOVERY
## Mission: BRODY_CANONICAL_TREE_TAGGING_BRIDGE_READONLY
## Timestamp: 20260514_012910
## Status: READONLY | decision_authority=KX108_ONLY

---

## Objectif

Identifier toutes les sources canoniques disponibles pour enrichir le tagging famille/arbre des BrodyMemoryDoc dans Neo4j. Zéro invention. Zéro heuristique. Zéro LLM-guess.

---

## Sources analysées (8 total)

### SRC_001 — arbres_34.canon.json ✅ USABLE
- **Path:** `obsidia-engine-candidate/candidate_packs/OBSIDIA_ENGINE_FULL_RUNTIME_KERNEL_BOUND_V2_20260508_195252/zip2_runtime_source/04_ARBRES_34_TENSOR_MATRIX/arbres_34.canon.json`
- **Type:** CANONICAL_TREE_REGISTRY
- **Statut:** STABLE_FREEZE
- **Contenu:** 34 arbres — champs id (01..34), name, folder_slug, family, non_decision
- **Format id:** numeric string "01".."34" → T01..T34 avec préfixe T
- **Format famille:** I_FONDAMENTAUX..VIII_OBSIDIA_AGI
- **Confidence:** 0.99
- **Raison:** Source canonique directe. Match exact possible via regex `_T(\d+)__` sur title. Pas de devinette. Aussi présent en Neo4j (BrodyMemoryDoc title=arbres_34.canon.json).
- **Utilisable pour tagging bridge:** OUI

### SRC_002 — arbres_34.registry.json ✅ USABLE
- **Path:** `obsidia-engine-candidate/candidate_packs/.../19_REGISTRES_JSON/arbres_34.registry.json`
- **Type:** CANONICAL_TREE_REGISTRY
- **Statut:** STABLE_FREEZE
- **Contenu:** 34 arbres — id, name, family — format registre
- **Confidence:** 0.99
- **Raison:** Format registre confirmé par _tree_discovery5.py. Complémentaire à SRC_001.
- **Utilisable pour tagging bridge:** OUI (référence croisée)

### SRC_003 — IR Alphabet Kernel Binding ⛔ NON USABLE (direct tagging)
- **Path:** `obsidia-engine-candidate/freezes/OBSIDIA_KERNEL_LANGUAGE_IR_ALPHABET_BINDING_V1_20260508_222633/`
- **Type:** IR_ALPHABET_KERNEL_BINDING
- **Statut:** STABLE_FREEZE
- **Contenu:** Tokens alphabet: READ, PARSE, NORMALIZE, PROJECT_CONTEXT, TRACE, AUDIT, BIND_READONLY_INGRESS, INFORM_KX108, REFUSE_UNKNOWN
- **Confidence:** 0.1
- **Raison:** IR alphabet définit des OPÉRATIONS, pas des appartenances famille-arbre. Assigner un BrodyMemoryDoc à une famille via tokens IR nécessiterait une table de mapping → heuristique. BLOQUÉ par règle anti-invention.
- **Utilisable pour tagging bridge:** NON (advisory uniquement)

### SRC_004 — Reverse OS Interlanguage Canon ⛔ NON USABLE (direct tagging)
- **Path:** `obsidia-engine-candidate/freezes/OBSIDIA_REVERSE_OS_INTERLANGUAGE_TRANSDUCTION_V1_20260508_224325/runtime/reverse_os_interlanguage_canon_v1.json`
- **Type:** REVERSE_OS_INTERLANGUAGE_CANON
- **Statut:** CANON_DRAFT_RUNTIME_BOUNDARY
- **Contenu:** Concepts: balance_fractale, avdr, memoire_fractale, procedural_universel, symbolisme_dynamique, agents_obsidiens, civilisation_cognitive. Pivot L2: VALUE STATE READ WRITE FLOW COND LOOP CALL RETURN EVENT TIME ERROR
- **Confidence:** 0.2
- **Raison:** Contient des concepts avec domaines (math, memory, agents) qui POURRAIENT mapper (ex: memoire_fractale → T24 Mémoire) mais AUCUN tree_id/family_id explicite. Créer ce mapping = heuristique. BLOQUÉ par anti-invention.
- **Potentiel futur:** HYBRID_BRIDGE_INPUT avec table concept→arbre fournie par opérateur
- **Utilisable pour tagging bridge:** NON (futur potentiel uniquement)

### SRC_005 — reverse_os.registry.json ⛔ VIDE
- **Path:** `obsidia-engine-candidate/candidate_packs/.../19_REGISTRES_JSON/reverse_os.registry.json`
- **Type:** REVERSE_OS_REGISTRY
- **Statut:** EMPTY
- **Contenu:** `{}` — fichier vide
- **Confidence:** 0.0
- **Raison:** Aucun contenu. Inutilisable.
- **Utilisable pour tagging bridge:** NON

### SRC_006 — test_T01_T02_os_trad_module.py ⛔ NON PERTINENT
- **Path:** `proofs/V18_3_1/engine_buildable_0_9_3_1/tests_modules/test_T01_T02_os_trad_module.py`
- **Type:** OS_TRAD_TEST_MODULE
- **Statut:** PROOF_STABLE
- **Contenu:** Tests PROPOSE/ACTION via orchestrator OS Trad
- **Confidence:** 0.05
- **Raison:** T01/T02 dans les noms de fonctions = IDs de TEST, pas IDs d'arbres (T01=Humain, T02=Conscience). Nomenclature coïncidente. OS Trad = protocole de traduction/proposition, pas taxonomie arbre.
- **Note:** OS Trad = "Obsidia Standard Translation" — opérations, pas arbre-famille.
- **Utilisable pour tagging bridge:** NON

### SRC_007 — BrodyMemoryDoc title regex _Tnn__ ✅ USABLE
- **Path:** BrodyMemoryDoc (Neo4j bolt://127.0.0.1:7688) — champ title
- **Type:** TITLE_ENCODED_TREE_ID
- **Statut:** IMPLICIT_STABLE
- **Contenu:** 48 docs avec pattern `_Tnn__` dans le titre sur 2739 docs 34_arbres (1.8%)
- **Confidence:** 0.99
- **Raison:** Match structurel direct au tree ID canonique. Combiner avec SRC_001 pour obtenir famille. Pas de devinette requise.
- **Exemples:**
  - `003BEA03EEDD_T04__Consensus_Distribue_Resonance_semantique.md`
  - `56C8CDE2F94D_T01__Reduction_Incertitude_Audit_coherence.md`
  - `2C6000D53716_T02__Gardien_de_fond__Conscience_Distribuee_Validation_reciprocite.md`
- **Utilisable pour tagging bridge:** OUI (source principale Path A)

### SRC_008 — LOCAL_9_GROUPS_34_ARBRES_SOURCE_SCAN ✅ USABLE (cross-ref)
- **Path:** `_local_audits/LOCAL_9_GROUPS_34_ARBRES_SOURCE_SCAN_20260512_220347/`
- **Type:** LOCAL_AUDIT_SCAN
- **Statut:** LOCAL_AUDIT
- **Contenu:** Source dumps de arbres_34.canon/registry/diff/raw_image
- **Confidence:** 0.85
- **Raison:** Scan précédent confirmant le contenu canonique. Référence croisée pour SRC_001.
- **Utilisable pour tagging bridge:** OUI (cross-référence)

---

## Résumé des sources

| Source ID | Type | Usable | Confidence | Raison blocage |
|---|---|---|---|---|
| SRC_001 | arbres_34.canon.json | ✅ OUI | 0.99 | — |
| SRC_002 | arbres_34.registry.json | ✅ OUI | 0.99 | — |
| SRC_003 | IR Alphabet | ⛔ NON | 0.10 | Définit opérations, pas familles |
| SRC_004 | Reverse OS Interlanguage | ⛔ NON | 0.20 | Pas de tree_id explicite → heuristique |
| SRC_005 | reverse_os.registry.json | ⛔ NON | 0.00 | Fichier vide `{}` |
| SRC_006 | OS Trad test module | ⛔ NON | 0.05 | Test IDs ≠ tree IDs |
| SRC_007 | BrodyMemoryDoc title regex | ✅ OUI | 0.99 | — |
| SRC_008 | Local audit scan | ✅ cross-ref | 0.85 | — |

**Sources utilisables:** SRC_001, SRC_002, SRC_007, SRC_008
**Sources bloquées:** SRC_003, SRC_004, SRC_005, SRC_006

---

## Coverage estimate

- Docs directement taggables (TITLE_REGEX_MATCH) : **48 / 2739** (1.8%)
- Docs en attente signal supplémentaire : **2691 / 2739** (98.2%)
- Docs hors corpus 34_arbres : **528 / 3267**

---

## Contraintes appliquées

- `no_heuristic_tagging = true`
- `no_llm_guessing = true`
- `no_invention = true`
- `tag_source MUST be arbres_34.canon.json`
- `tree_id extraction MUST use regex _T(\d+)__ on title only`
- `existing tags MUST be preserved — append only`
- `all writes require KX108 gate`
