# OBSIDIA F22A — READONLY INTENT / ALPHABET / CLAVAGE AUDIT

CHECKPOINT: F22A_READONLY_INTENT_ALPHABET_CLAVAGE_AUDIT
MODE: READ_ONLY
Date: 2026-05-28 05:00 UTC

---

## BOUNDARY CHECK

```
KX108_ONLY=true
readonly=true
advisory_only=true
emits_act=false
emits_verdict=false
memory_write=false
graphiti_write=false
kernel_mutation=false
x108_mutation=false
execution_allowed=false
NO_BACKEND_TOUCH=true
NO_KERNEL_TOUCH=true
NO_PATCH=true (audit seulement — stop avant F22B)
```

---

## 1. REPO STATE

```
HEAD       : d725cd5 feat: freeze F21 runtime dashboard F2-F20
Tag attendu: BRODY_F21_RUNTIME_FREEZE_DASHBOARD_F2_F20_20260528 ✓
Tags F17-F21 présents:
  BRODY_F17B_GRAPHITI_V20_RECONNECT_20260528        ✓
  BRODY_F18B_EXISTING_REVERSE_OS_IR_WIRING_20260528 ✓
  BRODY_F19B_THERMO_COHERENCE_TIME_UNIFIED_20260528 ✓
  BRODY_F20_GENCOIN_COGNITIVE_LEDGER_VISIBLE_20260528 ✓
  BRODY_F21_RUNTIME_FREEZE_DASHBOARD_F2_F20_20260528 ✓
git status : ## main...origin/main (clean)
```

---

## 2. RUNTIME STATE — CLASSIFICATION FAUTIVE OBSERVÉE

### Prompt bug (test révélateur)

```
"Décris ton état système actuel en lecture seule :
modules actifs, mémoire, Graphiti, IR, Reverse OS, Thermo, Gencoin,
Dashboard runtime. Ne propose aucune action."
```

### Ce que Brody retourne (observé sur 8000 et 8012)

```
graphiti_status       = GRAPHITI_V20_FROZEN_READONLY_PASS  ✓ (correct)
neo4j_status          = LIVE_READONLY                       ✓ (correct)
decision_authority    = KX108_ONLY                          ✓ (correct)
readonly              = true                                ✓ (correct)
emits_act             = false                               ✓ (correct)

-- CLASSIFICATION FAUTIVE --
classification        = MEMORY_WRITE_CANON_FREEZE           ✗ FAUX POSITIF
voice_mode            = DOMAIN_RACCORD_BOUNDARY             ✗ FAUX POSITIF
write_boundary_required = true                              ✗ FAUX POSITIF
support_intent        = action_request                      ✗ FAUX POSITIF
risk_flags            = [action_request, write_request,
                         memory_write_request,
                         graphiti_write_request,
                         canon_promotion_request]           ✗ FAUX POSITIF
contradictions        = [REQUEST_REQUIRES_WRITE_BUT_ROUTE_IS_READONLY,
                         REQUEST_REQUIRES_ACTION_BUT_ROUTE_IS_READONLY] ✗ FAUX POSITIF
```

### Parity 8000 vs 8012
Les deux instances partagent le même codebase → bug identique sur les deux ports.

---

## 3. SOURCE-MAP DES COUCHES EXISTANTES

| Couche | Fichier | Fonction | Statut | Réutilisable | Écart |
|---|---|---|---|---|---|
| **Alphabet IR L2** | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/ir.py` | VALUE, STATE, READ, WRITE, FLOW, COND, LOOP, CALL, RETURN, EVENT, TIME, ERROR | EXISTING | Oui | Non connecté au chat Brody — preuve formelle seulement |
| **Contract L2.5 R1-R10** | `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/contract.py` | `validate(program)` | EXISTING | Oui | Non connecté au chat Brody — validateur structurel proof only |
| **OS Trad / `_risk_flags`** | `apps/obsidia_api/routes/os_trad_ir_reverse.py` | `_risk_flags(text)` | **EXISTING — BUG** | Oui (après fix) | Substring match sans word-boundary : `"act"` dans `"actifs"` |
| **Domain Raccord / `has_memory_write_request`** | `apps/obsidia_api/brody_domain_raccord_adapter.py` | `has_memory_write_request(text)` | **EXISTING — BUG** | Oui (après fix) | Substring match sans word-boundary : `"ecris"` dans `"decris"` |
| **`detect_critical_pressure`** | `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py` | `detect_critical_pressure(text)` | **EXISTING — BUG** | Oui (après fix) | Même substring bug + `_QUERY_OVERRIDES` ne couvre que l'anglais "describe", pas le français "décris" |
| **Rights Authority Matrix** | `apps/obsidia_api/brody_rights_authority_matrix.py` | `_detect_request_type()` — 10 catégories | **EXISTING — MISSING CATEGORY** | Oui (après ajout) | Catégorie `RUNTIME_STATE_READONLY` absente. Prompt tombe sur `PURE_RESPONSE` puis domain raccord l'empoisonne |
| **IR Candidate** | `apps/obsidia_api/brody_machination_composer.py` | `build_support_routes()` | EXISTING | Oui | Hérite les flags fautifs de `_risk_flags` + domain raccord |
| **translation_trace** | `apps/obsidia_api/brody_existing_reverse_os_bridge.py` | `build_existing_reverse_os_snapshot()` | EXISTING — STABLE (F18B) | Oui | Aucun écart |
| **alphabet_units** | `apps/obsidia_api/routes/os_trad_ir_reverse.py` | `_alphabet_units(text, lang, flags)` | EXISTING | Oui | Hérite les flags fautifs |
| **Reverse OS** | `apps/obsidia_api/brody_existing_reverse_os_bridge.py` | F18B stable | EXISTING — STABLE | Oui | Aucun écart |
| **Adaptive Response / Sigma** | `apps/obsidia_api/brody_structured_response_engine_adapter.py` | `make_structured_response_snapshot()` | EXISTING — STABLE | Oui | Aucun écart |
| **Anti-Mismatch** | `apps/obsidia_api/brody_anti_mismatch_signal.py` | `build_anti_mismatch_signal()` | EXISTING — STABLE | Oui | Aucun écart |
| **Thermo Unified** | `apps/obsidia_api/brody_thermo_coherence_time_unified.py` | `build_thermo_coherence_time_unified_packet()` | EXISTING — STABLE (F19B) | Oui | Aucun écart |
| **Gencoin Cognitive Ledger** | `apps/obsidia_api/brody_gencoin_cognitive_ledger.py` | `build_gencoin_cognitive_ledger_packet()` | EXISTING — STABLE (F20B) | Oui | Aucun écart |
| **Runtime Freeze Dashboard** | `apps/obsidia_api/routes/runtime_freeze.py` | `GET /api/runtime/freeze-dashboard` | EXISTING — STABLE (F21) | Oui | Aucun écart |
| **Shazam Cognitif** | `periphery/shazam_cognitif.py` | `shazam(payload, threshold)` | EXISTING — NON CONNECTÉ | Non (dépendance `spectral_hash` absente) | Import `spectral_hash` non disponible dans runtime Brody |
| **Clavage / Verbatia / LU-MH** | DOC_ONLY | — | MISSING | Non | Référencé dans docx seulement. Aucun module Python runtime. |
| **Agent Vecteur / semantic drift** | DOC_ONLY | — | MISSING | Non | Référencé dans docx seulement. |
| **Harmonic vote / veto / métriques** | DOC_ONLY | — | MISSING | Non | Référencé dans docx seulement. |
| **Continuum / Zone Latente** | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/` | README seulement | PARTIAL — DOC_ONLY | Non | Concept uniquement, pas de module Python exécutable. |

---

## 4. BUG ROOT CAUSE — ANALYSE PRÉCISE

### Trois chemins de faux positif indépendants

---

### 4.1 — Faux positif principal : `has_memory_write_request()` dans `brody_domain_raccord_adapter.py`

**Localisation** : lignes 100–132

```python
write_terms = (
    "ecris", "ecrit", "ecrire", "write", ...
)
memory_terms = (
    "memoire", "memory", "graphiti", ...
)
return _has_any(low, write_terms) and _has_any(low, memory_terms)
```

**Mécanisme du faux positif** :

```
"Décris ton état…"
     ↓ _fold() [NFKD + strip combining + lower]
"decris ton etat…"
     ↓ _has_any(low, write_terms)
"ecris" ∈ "decris" ?  YES — substring match !
     ↓ _has_any(low, memory_terms)
"memoire" ∈ low ?     YES (prompt contient "mémoire")
"graphiti" ∈ low ?    YES (prompt contient "Graphiti")
     ↓
has_memory_write_request() = True
     ↓
domains.append("MEMORY_WRITE_CANON_FREEZE")
boundary_required = True
voice_mode = "DOMAIN_RACCORD_BOUNDARY"
write_boundary_required = True
```

**Cause** : `_has_any` fait du **substring matching** sans word-boundary. Le verbe français `décris` (impératif de décrire) contient `écris` (conjugaison d'écrire) comme sous-chaîne. Ce faux positif est structurel et reproductible sur tout prompt commençant par "Décris…".

---

### 4.2 — Faux positif secondaire : `detect_critical_pressure()` dans `brody_v1_4_12a_final_answer_adapter.py`

**Localisation** : lignes 86–98

```python
write_terms = ["ecris", "ecrire", "write", ...]
memory_targets = ["graphiti", "neo4j", "memoire", "memory", ...]
gw = any(t in s for t in memory_targets) and any(t in s for t in write_terms)
```

**Même mécanisme** : `"ecris"` est substring de `"decris"`.

**Guard existant incomplet** :
```python
_QUERY_OVERRIDES = [..., "describe", ...]
if any(q in s_low for q in _QUERY_OVERRIDES):
    return False  # ← empêche le faux positif
```
"describe" est dans les overrides (anglais) mais **"décris"** (français, impératif de décrire) n'y est pas. Le guard est en anglais, le prompt est en français.

---

### 4.3 — Faux positif tertiaire : `_risk_flags()` dans `routes/os_trad_ir_reverse.py`

**Localisation** : ligne 139

```python
if any(token in low for token in ["act", "agir", "lance", "execute", ...]):
    flags.append("action_request")
```

**Mécanisme** :
- `"act"` ∈ `"actifs"` → TRUE (sous-chaîne)
- `"act"` ∈ `"action"` → TRUE (sous-chaîne de "aucune action")
- → `action_request` ajouté alors que le prompt dit explicitement "Ne propose aucune action"

**Même problème dans `_safe_flags()`** de `brody_machination_composer.py` lignes 62–72.

---

### 4.4 — Gap structurel : absence de `RUNTIME_STATE_READONLY` dans `brody_rights_authority_matrix.py`

**Constat** : La matrice authority (`_PATTERNS`, 10 catégories) n'a pas de catégorie pour les requêtes de lecture d'état runtime. Le prompt tombe sur `PURE_RESPONSE` (catégorie catch-all). Cela n'est pas incorrect en soi, mais ce comportement laisse domain raccord comme seule couche de classification sémantique — et domain raccord trigger MEMORY_WRITE_CANON_FREEZE.

**Si `RUNTIME_STATE_READONLY` existait** : le prompt serait capturé avant domain raccord, classifié correctement, et `write_boundary_required = false`.

---

### 4.5 — Ordre d'exécution dans `brody.py`

```
1. run_brody_real_response_pipeline() → response_md (correct)
2. classify_request_authority() → request_type=PURE_RESPONSE (neutre)
3. build_memory_response_chain() → LOCAL_GRAPHITI_INDEX_FALLBACK (correct)
4. build_machination_packet() → appelle _safe_flags() → "action_request" (FAUX POSITIF)
   └── build_domain_raccord_snapshot() → MEMORY_WRITE_CANON_FREEZE (FAUX POSITIF)
5. build_true_brody_answer() → hérite le domain_raccord poisonné
6. final_answer → répond mais avec les flags fautifs dans le payload
```

Domain raccord **s'exécute après** la rights matrix. Il n'existe pas de guard qui intercepte le prompt readonly **avant** que domain raccord ne l'analyse avec ses write_terms en substring.

---

## 5. RECHERCHE LOCALE / ZIPS

### Modules runtime existants (repo)

```
periphery/shazam_cognitif.py           FOUND — dépendance spectral_hash manquante
periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/
  05_SHAZAM_COGNITIF/shazam_cognitif.py   FOUND — même module, même dépendance
  12_FRICTION_AVDR_CONTINUUM/README.md    FOUND — concept, pas de module Python
  17_TESTS/test_shazam_cognitif.py        FOUND — test unitaire
  15_GUARDS_NON_DECISION/no_shazam_act.py FOUND — guard ACT pour Shazam
```

### Clavage / Verbatia / LU-MH

```
grep résultat : 0 fichiers Python runtime
Sources : docx uniquement
Conclusion : DOC_ONLY, pas de module réutilisable dans le runtime actuel
```

### Continuum / Zone Latente

```
periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/12_FRICTION_AVDR_CONTINUUM/
  README.md : conceptuel uniquement
  Conclusion : PARTIAL — concept, pas de code Python exécutable
```

### Alphabet IR en zips locaux

Pas de scan de zips effectué (hors scope F22A).
Les modules prouvés sont dans `proofs/V18_3_1/engine_buildable_0_9_3_1/obsidia_os0/` — accessible directement.

---

## 6. PLAN D'ACTION PROPOSÉ (NON RÉALISÉ)

### OPTION A — Fix chirurgical des substring bugs (3 fichiers)

**Fichiers** :
- `apps/obsidia_api/brody_domain_raccord_adapter.py` : `has_memory_write_request()`
- `apps/obsidia_api/brody_v1_4_12a_final_answer_adapter.py` : `detect_critical_pressure()`
- `apps/obsidia_api/routes/os_trad_ir_reverse.py` : `_risk_flags()`

**Changements** :
1. Remplacer `_has_any(low, write_terms)` par `_has_any_word(low, write_terms)` avec une version utilisant `\b` (word boundaries) — regex plutôt que substring.
2. Ajouter `"decris"` dans `_QUERY_OVERRIDES` de `detect_critical_pressure`.
3. Remplacer `token in low` par `re.search(r'\b' + re.escape(token) + r'\b', low)` dans `_risk_flags`.

**Risques** :
- Regex peut changer le comportement sur d'autres patterns actuellement corrects.
- Nécessite tests de non-régression sur les 10+ prompts de test existants.
- Minimal blast radius — 3 fonctions indépendantes.

**Tests nécessaires** : voir section 7.

---

### OPTION B — Bridge RUNTIME_STATE_READONLY dans la rights matrix

**Fichier** :
- `apps/obsidia_api/brody_rights_authority_matrix.py`

**Changements** :
- Ajouter catégorie `RUNTIME_STATE_READONLY` dans `_PATTERNS` (patterns: "décris.*état.*système", "état système actuel", "décris.*runtime", "runtime.*état", "état.*brody", "liste.*modules.*actifs", "modules actifs.*lecture seule", "system state readonly", "describe.*runtime.*state").
- Ajouter `RUNTIME_STATE_READONLY` dans `_MATRIX` avec `response_mode = "CONTEXT_DIAGNOSTIC"`, `write_boundary_required = False`.
- La rights matrix s'exécute **avant** domain raccord.
- Si `request_type = RUNTIME_STATE_READONLY`, domaine raccord ne doit pas ajouter `MEMORY_WRITE_CANON_FREEZE`.

**Risques** :
- Modifier la rights matrix change le comportement de classification globale.
- Nécessite que `build_machination_packet` respecte la classification rights matrix pour bypasser domain raccord write boundary.

**Tests nécessaires** : voir section 7.

---

### OPTION C — Guard déterministe périphérique (recommandé comme premier patch)

**Fichier à créer** : `apps/obsidia_api/brody_readonly_intent_guard.py`

**Fonction** :
```python
def detect_readonly_runtime_state_intent(user_message: str) -> bool:
    """
    Retourne True si le message est une lecture d'état système readonly.
    Détection déterministe, prioritaire sur domain raccord.
    """
```

**Patterns détectés** :
- "décris.*état.*système.*lecture seule"
- "état système actuel"
- "décris.*runtime"
- "modules actifs.*mémoire.*graphiti"
- "runtime.*readonly" / "lecture seule.*runtime"
- "describe.*system.*state.*readonly"
- "liste.*modules actifs"

**Intégration dans `brody_machination_composer.py`** :
- Si `detect_readonly_runtime_state_intent(text)` → True :
  - `flags = []` (aucun flag write/action)
  - `support_intent = "runtime_state_query"`
  - `write_boundary_required = False`
  - domain raccord appelé mais write boundary ignoré

**Risques** :
- Guard peut bloquer une vraie demande d'écriture si le prompt ressemble à une lecture. Mitigation : les patterns sont très spécifiques (doivent contenir à la fois "état système" ET "lecture seule" ou similaire).
- Minimal blast radius — 1 nouveau fichier + 1 ligne dans machination_composer.

**Tests nécessaires** : voir section 7.

---

### RECOMMANDATION

**F22B = OPTION C + OPTION A conjointement** :
1. `brody_readonly_intent_guard.py` — guard RUNTIME_STATE_READONLY (Option C) : intercepte en premier
2. Fix word-boundary dans `has_memory_write_request` + `_risk_flags` + `detect_critical_pressure` (Option A) : corrige le substrat
3. Option B (rights matrix) en dernier si les deux premiers ne suffisent pas

Ordre : **A + C d'abord, B si nécessaire.**

---

## 7. TESTS PROPOSÉS POUR F22B (NON CRÉÉS)

```
tests/api/test_f22b_readonly_intent_classification.py

- test_readonly_runtime_state_does_not_trigger_memory_write_boundary
    prompt = "Décris ton état système actuel en lecture seule : modules actifs, mémoire, Graphiti..."
    assert classification != "MEMORY_WRITE_CANON_FREEZE"
    assert write_boundary_required == False
    assert "memory_write_request" not in risk_flags
    assert "graphiti_write_request" not in risk_flags

- test_graphiti_mention_readonly_not_graphiti_write
    prompt = "Quel est l'état Graphiti actuel en lecture seule ?"
    assert "graphiti_write_request" not in risk_flags

- test_memory_mention_readonly_not_memory_write
    prompt = "Décris l'état de la mémoire en lecture seule."
    assert "memory_write_request" not in risk_flags

- test_freeze_dashboard_mention_not_freeze_promotion
    prompt = "Décris le Dashboard runtime Freeze F21."
    assert "MEMORY_WRITE_CANON_FREEZE" not in domains

- test_decris_not_ecris_false_positive
    assert has_memory_write_request("Décris ton état") == False  (word-boundary fix)

- test_actifs_not_act_false_positive
    assert "action_request" not in _risk_flags("modules actifs, mémoire")

- test_explicit_write_memory_still_triggers_boundary
    prompt = "Écris ça en mémoire Graphiti maintenant."
    assert "memory_write_request" in risk_flags
    assert write_boundary_required == True

- test_explicit_graphiti_write_still_triggers_boundary
    prompt = "Écris dans Graphiti cette information."
    assert "graphiti_write_request" in risk_flags

- test_explicit_canon_promotion_still_triggers_boundary
    prompt = "Canonise ce bloc en mémoire."
    assert "MEMORY_WRITE_CANON_FREEZE" in domains

- test_8000_8012_parity_runtime_state_intent
    # Smoke sur les deux ports — même classification
    # 8000: classification != MEMORY_WRITE_CANON_FREEZE
    # 8012: classification != MEMORY_WRITE_CANON_FREEZE

- test_terminal_brody_runtime_state_narration
    # Réponse finale contient des mentions de tous les modules actifs
    # Graphiti / OS Trad / Thermo / Gencoin / Dashboard présents
    # Pas de "écriture bloquée" ou "boundary required"
```

---

## 8. CRITÈRES DE NON-RÉGRESSION

Le futur patch (F22B) ne doit jamais casser :

```
INVARIANTS_KERNEL :
  KX108_ONLY              = true (tous paths)
  readonly                = true
  emits_act               = false
  emits_verdict           = false
  memory_write            = false
  graphiti_write          = false
  kernel_mutation         = false
  x108_mutation           = false

INVARIANTS_RUNTIME :
  F17 Graphiti readonly   = GRAPHITI_V20_FROZEN_READONLY_PASS
  F18 Reverse OS          = BRODY_EXISTING_REVERSE_OS_BRIDGE_V1
  F19 Thermo unified      = THERMO_COHERENCE_TIME_UNIFIED_READONLY_PASS
  F20 Gencoin cognitive   = GENCOIN_COGNITIVE_LEDGER_READONLY_PASS
  F21 Dashboard           = F2_F20_RUNTIME_FREEZE_DASHBOARD_READY
  F21 packets             = 20/20

INVARIANTS_CLASSIFICATION_VRAIS_POSITIFS :
  "Écris ça en mémoire Graphiti."     → memory_write_request RESTE actif
  "Canonise ce bloc."                 → MEMORY_WRITE_CANON_FREEZE RESTE actif
  "Autorise ACT."                     → action_request RESTE actif
  "Écris dans Neo4j."                 → graphiti_write_request RESTE actif
  "Merge X108."                       → mutation_request RESTE actif
```

---

## 9. RÉSUMÉ FROID

```
ROOT_CAUSE =
  THREE independent substring false positives:
  1. 'décris' → 'decris' contains 'ecris' → write_terms match
     FILE: brody_domain_raccord_adapter.py:has_memory_write_request()
     FILE: brody_v1_4_12a_final_answer_adapter.py:detect_critical_pressure()
  2. 'actifs' contains 'act' → action_request flag
     FILE: routes/os_trad_ir_reverse.py:_risk_flags()
     FILE: brody_machination_composer.py:_safe_flags()
  3. No RUNTIME_STATE_READONLY category in rights matrix → prompt falls
     to PURE_RESPONSE → domain raccord runs unchecked
     FILE: brody_rights_authority_matrix.py

EXISTING_MODULES_FOUND =
  Alphabet IR L2 (proofs/V18_3_1) — EXISTING not connected
  Contract L2.5 (proofs/V18_3_1) — EXISTING not connected
  OS Trad / _risk_flags — EXISTING HAS BUG
  Domain Raccord — EXISTING HAS BUG
  detect_critical_pressure — EXISTING HAS BUG
  Reverse OS Bridge (F18B) — STABLE
  Thermo Unified (F19B) — STABLE
  Gencoin Cognitive (F20B) — STABLE
  Runtime Dashboard (F21) — STABLE
  Shazam Cognitif (periphery) — EXISTING not connected (dep missing)
  Clavage/Verbatia/LU-MH — MISSING (doc only)
  Agent Vecteur/semantic drift — MISSING (doc only)
  Harmonic vote/veto — MISSING (doc only)
  Continuum/Zone Latente — PARTIAL (readme only)

BEST_REUSE_CANDIDATE =
  brody_domain_raccord_adapter.py — word-boundary fix (minimal, surgical)
  brody_v1_4_12a_final_answer_adapter.py — add 'decris' to _QUERY_OVERRIDES
  routes/os_trad_ir_reverse.py — word-boundary fix for 'act' token
  NEW: brody_readonly_intent_guard.py — RUNTIME_STATE_READONLY detection guard

PATCH_RECOMMENDATION =
  F22B = OPTION C (new guard) + OPTION A (word-boundary fixes)
  Scope: 3 existing files fixed + 1 new guard module
  No new architecture, no new agents, no mock, no hardcode
  Test suite: 9 new tests (7 negative + 2 regression-positive)

RISKS =
  LOW: word-boundary regex may alter edge-case behavior on existing prompts
  MITIGATED BY: full regression suite before commit
  NO_KERNEL_TOUCH: all fixes are in apps/obsidia_api/ only
  NO_PROOF_TOUCH: proofs/ and formal/ untouched

NEXT = WAITING_FOR_VALIDATION
```

---

## STOP — Aucun patch appliqué.

Ce rapport est une lecture de source uniquement.
Le chantier F22B (patch réel) attend la validation utilisateur.

```
F22A_AUDIT_COMPLETE=true
ROOT_CAUSE_IDENTIFIED=true
FALSE_POSITIVE_COUNT=3 (independent paths)
MODULES_MAPPED=16
PATCH_CANDIDATE_PROPOSED=true
NO_PATCH_APPLIED=true
AWAITING_USER_VALIDATION=true
```
