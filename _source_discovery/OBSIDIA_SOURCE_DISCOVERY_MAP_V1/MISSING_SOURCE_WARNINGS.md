# MISSING_SOURCE_WARNINGS
# OBSIDIA_SOURCE_DISCOVERY_MAP_V1
# Date: 2026-06-02

> Concepts cherchés qui sont absents sous le nom exact, ou trouvés sous un nom différent.

---

## ABSENT_UNDER_THIS_NAME

### Jcoin
- **Recherché sous** : `Jcoin`, `J_coin`, `jcoin`, `j_coin`
- **Trouvé sous autre nom** : NON
- **Source alternative** : Gencoin est le seul concept de valeur numérique — `periphery/gencoin.py`
- **Note** : Jcoin n'existe ni comme fichier, ni comme variable, ni comme classe dans le repo
- **Action Plan 2** : Confirmer si Jcoin = Gencoin (alias audio) ou concept distinct à spécifier

### agi_subordination_spec.md
- **Recherché sous** : `agi_subordination_spec`, `AGI subordination`, `agi_sub`
- **Trouvé sous autre nom** : NON (concept de non-souveraineté présent dans `docs/civilization/CAPABILITY_IS_NOT_AUTHORITY_V1.md`)
- **Source alternative** : `docs/civilization/CAPABILITY_IS_NOT_AUTHORITY_V1.md`, `docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md`
- **Action Plan 2** : Créer spec formelle à partir de ces sources existantes

### buv_master_spec.md
- **Recherché sous** : `BUV`, `buv_master_spec`, `Balance Universelle Valorisée`, `Balance Obsidienne master`
- **Trouvé sous autre nom** : NON — BUV mentionné conceptuellement mais aucun fichier `buv_master_spec.md`
- **Source alternative** : `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md`, `periphery/gencoin_sandbox/balance_operator.py`
- **Action Plan 2** : Consolidation nécessaire — BALANCE_CANON.md est la source la plus proche

### critical_world_admission_spec.md
- **Recherché sous** : `world_admission`, `critical_world`, `world gate`, `admission_spec`
- **Trouvé sous autre nom** : `periphery/world_action_gateway.py`, `periphery/engine_gates/world_action_gateway.py`
- **Source alternative** : gateway runtime présent, spec documentaire absente
- **Action Plan 2** : Extraire spec depuis world_action_gateway.py

### value_emission_model.md
- **Recherché sous** : `value_emission_model`, `value emission spec`, `emission_model`
- **Trouvé sous autre nom** : `docs/gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md`, `periphery/gencoin_distribution.py`
- **Source alternative** : Distribution law partielle — pas de spec d'émission de valeur unifiée
- **Action Plan 2** : Consolider depuis GENCOIN_DISTRIBUTION_LAW_V0.md + GENCOIN_FORMAL_MATH_SPEC_V0_2.md

### obsidia_interlayer_constitution.md
- **Recherché sous** : `interlayer_constitution`, `OBSIDIA_CONSTITUTION`, `inter_layer_spec`
- **Trouvé sous autre nom** : `docs/civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md`
- **Source alternative** : Couche agentic-constitutional présente mais pas de spec interlayer unifiée
- **Action Plan 2** : P2 — utile mais non bloquant pour Plan 2

### OBJECT_STATUS_LIFECYCLE.md
- **Recherché sous** : `OBJECT_STATUS_LIFECYCLE`, `object lifecycle`, `status lifecycle`
- **Trouvé sous autre nom** : `periphery/action_lifecycle.py` (cycle de phases d'action)
- **Source alternative** : action_lifecycle.py est le plus proche — mais couvre les actions, pas les objets génériques
- **Action Plan 2** : Vérifier si périmètre est actions seulement ou objets génériques

### XYZ_COMPILATION_PIPELINE_SPEC.md
- **Recherché sous** : `.xyz`, `XYZ`, `xyz_compilation`, `xyz_pipeline`
- **Trouvé sous autre nom** : `BRANCHESXYZKLN.md` dans `periphery/OBSIDIA_V4_STRUCTURED_FULL/12_EXTENSIONS_R_D/`
- **Source alternative** : Fichier existant mais contenu non vérifié en détail
- **Action Plan 2** : Lire BRANCHESXYZKLN.md pour confirmer si équivalent

### 7 flux exacts (corpus canonique)
- **Recherché sous** : `sept flux`, `7 flux`, `seven flux`, `flux complets`
- **Trouvé sous autre nom** : T31 = "Arbre des Flux" (`apps/obsidia_api/brody_tree_policy.py`)
- **Statut** : `docs/REPO_BOUNDARY.md` ligne 84 : "7 flux complets | Non, pas comme corpus canonique complet | **Hors périmètre public**"
- **Action Plan 2** : Les 7 flux exacts sont HORS PERIMETRE PUBLIC — à ne pas inclure dans specs publiques sans décision explicite

### obsidia-workspace (repo dédié fondations/domaines/agents/)
- **Recherché sous** : `obsidia-workspace`, `fondations/`, `domaines/`, `gouvernance/`, `recherche/`
- **Trouvé sous autre nom** : `periphery/OBSIDIA_V4_STRUCTURED_FULL/` (structure 15 dossiers), `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/`
- **Note** : Pas de repo standalone `obsidia-workspace` — le workspace hub intellectuel est intégré dans `periphery/`
- **Action Plan 2** : Corriger la référence Gemini — workspace = OBSIDIA_V4_STRUCTURED_FULL

---

## SOURCE_FOUND_UNDER_DIFFERENT_NAME

| Terme Gemini / Audio | Nom réel GitHub | Chemin | Statut |
|----------------------|-----------------|--------|--------|
| `/domaine/` | `domaines/` inexistant → `02_BLOCS_17/`, `04_SPECS_40/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `/agent/` | `07_AGENTS_ET_ROLES/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/07_AGENTS_ET_ROLES/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `/fondation/` | `06_GARDIENS_DE_FOND_T1_T12/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/06_GARDIENS_DE_FOND_T1_T12/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `BUV` | `balance_operator.py`, `BALANCE_CANON.md` | `periphery/gencoin_sandbox/`, `docs/gencoin/sandbox_pre_freeze/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `Jcoin` | NON TROUVÉ — possible alias Gencoin | — | ABSENT_UNDER_THIS_NAME |
| `.xyz` | `BRANCHESXYZKLN.md` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/12_EXTENSIONS_R_D/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `obsidia-workspace` | `OBSIDIA_V4_STRUCTURED_FULL` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `Reverse OS` | `06_REVERSE_OS_SSR_JARVIS/` + `jarvis_projection.py` | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/06_REVERSE_OS_SSR_JARVIS/` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
| `FEEDBACK_CAPTURED` (état manquant) | `FEEDBACK_CAPTURED` présent dans action_lifecycle.py | `periphery/action_lifecycle.py:28` | SOURCE_FOUND_UNDER_DIFFERENT_NAME |
