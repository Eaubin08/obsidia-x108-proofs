# EXTRACTION_LIMITS_AND_DEFERRED_SCOPE.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## Limites de cette extraction

### Limite 1 : Volume vs profondeur

Le repo contient **49 535 fichiers** (hors node_modules, __pycache__, .git). Cette mission a pu lire en profondeur ~20 fichiers et référencer ~42 candidats. Cela représente < 0.1% du volume total.

**Conséquence :** L'extraction capture les concepts fondateurs (kernel, BRODY, Sigma, preuves, domaines), mais ne peut pas couvrir :
- L'ensemble des tests (tests/ contient des centaines de fichiers)
- Les modules Python individuels de periphery/ (~50+ fichiers .py)
- Les modules Python de apps/obsidia_api/ (~25 fichiers brody_*.py non lus)
- Les archives R&D profondes (OBSIDIA_V4_STRUCTURED_FULL, OBSIDIA_MMONDE)

---

### Limite 2 : Timeout bash (45s)

Les opérations bash sont limitées à 45s. Cela empêche les `find` + `grep` larges sur 49 535 fichiers en un seul appel. Chaque opération doit être ciblée.

---

### Limite 3 : Production propriétaire hors scope

Par conception, ce repo **ne contient pas** :
- Le moteur de production Python complet
- La couche Sigma de production complète
- Les adaptateurs métier finaux
- Les clés et secrets de déploiement
- Le cockpit opérateur institutionnel

Ces éléments sont hors scope même avec une lecture exhaustive du repo.

---

### Limite 4 : Contraintes mission READ_ONLY

Cette mission est **strictement READ_ONLY** :
- NO PATCH, NO COMMIT, NO PUSH, NO TAG
- NO MEMORY WRITE, NO GRAPHITI WRITE, NO NEO4J WRITE
- NO RUNTIME BINDING, NO WEB, NO SCRAPING
- NO PROVIDER BINDING, NO PATH COMPUTE

Cela empêche notamment l'exécution des verifiers (`verify_all.py`, `verify_decision.py`) pour confirmer les résultats live. L'extraction se base sur les rapports de résultats existants.

---

### Limite 5 : OBSIDIA_TOUS_LES_AGENTS.docx non disponible

La source de vérité des 52 agents en 9 familles est un fichier `.docx` **non committé dans ce repo**. Seul le top 5 est documenté dans `agents/registry.md`. Les 47 autres agents restent non documentés dans l'extraction.

---

## Scope déféré

### Déféré 1 : Lecture profonde de periphery/

`periphery/` contient ~50 modules Python non lus :
- `periphery/avdr.py` — AVDR (Analyse Vélocité Décisionnelle Relative)
- `periphery/bdf/double_brain_router.py` — Double cerveau
- `periphery/event_bus.py` — Bus d'événements
- `periphery/control_plane.py` — Plan de contrôle
- `periphery/data_gate.py` — Gate données
- `periphery/eml_compression.py` — Compression EML
- `periphery/energy_thermo.py` — Thermodynamique
- `periphery/agents/modules_a1_a24/` — 24 modules agentiques A1-A24

**Valeur éducative si lus :** HIGH (implémentation du stack constitutionnel)

---

### Déféré 2 : apps/obsidia_api/ — 25 modules BRODY

Non lus (timeout) :
- `brody_full_runtime_orchestrator.py`
- `brody_rights_authority_matrix.py`
- `brody_cognitive_modules_adapter.py`
- `brody_true_voice_adapter.py`
- `brody_tree_policy.py`
- etc.

**Valeur éducative si lus :** HIGH (implémentation complète de l'orchestration BRODY)

---

### Déféré 3 : formal/tla/ — Lecture des specs TLA+

X108.tla et DistributedX108.tla sont référencés mais non lus directement. Leur contenu exact (variables, invariants TLA+, propriétés temporelles) n'est pas extrait.

**Valeur éducative si lus :** VERY HIGH pour les chercheurs en vérification formelle.

---

### Déféré 4 : periphery/OBSIDIA_V4_STRUCTURED_FULL/ — Archive V4

14 sous-dossiers, contenu non lu :
- `02_BLOCS_17/` — 17 blocs conceptuels
- `03_PEPITES_161/` — 161 pépites conceptuelles
- `04_SPECS_40/` — 40 spécifications
- `05_MODULES_A1_A24/`
- `06_GARDIENS_DE_FOND_T1_T12/`
- `08_PREUVES_LEAN_TLA/`
- `12_EXTENSIONS_R_D/`

**Valeur éducative si lus :** MEDIUM (contexte R&D de V4, antérieur au stack P1 actuel)

---

### Déféré 5 : .deepseek/pastes/ — Historique DeepSeek

11 pastes de sessions DeepSeek (2026-05-19 à 2026-05-21) contenant probablement des logs de debug BRODY. Non lus.

**Valeur éducative si lus :** LOW (debug sessions spécifiques)

---

### Déféré 6 : _external_benchmarks/ — Comparaisons industrie

8 benchmarks encapsulés :
- SWE-bench, BFCL, AgentDojo, TAU-bench, WebArena, GAIA, OSWorld

**Valeur éducative si lus :** MEDIUM (positionnement Obsidia vs benchmarks standards)

---

### Déféré 7 : .claude/context/ — Doctrine opérationnelle complète

Non lus directement :
- `OBSIDIA_IDENTITY.md`
- `WORKFLOW.md`
- `PROTECTED_SCOPE.md`
- `AGENTIC_ROUTING.md`
- `TOKEN_POLICY.md`
- `FRACTAL_INFERENCE.md`

**Valeur éducative si lus :** HIGH (doctrine opérationnelle complète du repo)

---

### Déféré 8 : proofs/ — Tests et verifiers non exécutés

Contenu référencé mais non lu profondément :
- `proofs/lean/Obsidia.lean` — code Lean 4 réel
- `proofs/verifiers/verify_all.py` — verifier complet
- `proofs/verifiers/verify_decision.py` — verifier décision
- `tests/adversarial/` — 1M+ cas adversariaux

---

## Recommandations pour missions ultérieures

Pour un deuxième passage BRODY_RND_V1 :

1. **Lire periphery/ modules-clés** : event_bus, control_plane, data_gate, avdr, bdf/double_brain_router
2. **Lire apps/obsidia_api/brody_full_runtime_orchestrator.py** — pour comprendre l'orchestration complète
3. **Lire formal/tla/X108.tla** — pour les invariants TLA+ exacts
4. **Lire .claude/context/OBSIDIA_IDENTITY.md** — pour la doctrine identitaire complète
5. **Lire periphery/OBSIDIA_V4_STRUCTURED_FULL/03_PEPITES_161/** — pour les pépites conceptuelles V4
6. **Lire .claude/context/PROTECTED_SCOPE.md** — pour la liste exacte des fichiers protégés

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
