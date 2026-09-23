# Ce que cette démonstration prouve — et ce qu'elle ne prouve pas

**F41 RC1 · Audit honnête du périmètre probatoire**  
**Mode:** READONLY · KX108_ONLY · emits_act=false  
**Date:** 2026-05-29

---

## Ce que ça PROUVE

### 1. La frontière advisory/décision est vérifiable en temps réel

Chaque réponse du composant Brody porte un dictionnaire `BOUNDARY` avec 15 drapeaux booléens. Ces drapeaux sont calculés et retournés par chaque fonction Python, vérifiés par chaque route FastAPI, et peuvent être inspectés en direct par tout appelant HTTP. 103 tests unitaires en vérifient la cohérence à chaque palier.

**Preuve :** `tests/api/test_f38_multi_domain_live_api_route_readonly.py` — 20 tests, PASS.

---

### 2. Aucun token décisionnel interdit n'est émis

Un scan par expression régulière à limites de mot (`\bTOKEN\b`) vérifie que les tokens `ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT` n'apparaissent jamais dans les textes générés par Brody. La vérification est appliquée à chaque réponse, sur chaque domaine, dans chaque smoke script.

**Preuve :** 474 checks cumulés sur 6 scripts — `forbidden_tokens_found=False` partout.

**Note technique :** La vérification utilise des limites de mot (pas une recherche de sous-chaîne) pour éviter les faux positifs sur des termes légitimes comme « transaction » ou « activations ».

---

### 3. La frontière tient sur un vrai serveur uvicorn

Trois preuves live-server ont été générées par exécution réelle (pas TestClient, pas mock) :
- **F34B** — port 9010, source `REAL_BACKEND`, 73/73 checks, SHA256 : `20A27188...`
- **F36B** — port 8011, source `LIVE_SERVER_8011`, 61/61 checks, SHA256 : `A6FD4BC2...`
- **F38** — port 8011, source `LIVE_SERVER_8011`, 141/141 checks, SHA256 : `746621E5...`

Ces preuves montrent que la frontière n'est pas une propriété des tests unitaires seuls — elle tient sur un processus uvicorn séparé, avec de vraies requêtes HTTP.

---

### 4. La chaîne palier est complète, étiquetée et traçable

10 tags git (F32→F39 + F34B + F36B) forment une chaîne traçable depuis `git log`. Chaque palier a :
- Un tag git avec timestamp
- Un rapport markdown dans `docs/runtime/`
- Une preuve JSON dans `docs/runtime/`
- Au moins un script smoke dans `scripts/`
- Un répertoire de freeze dans `.runtime_freezes/`

**Preuve :** `git tag --list "BRODY_F3*"` → 10 tags présents.

---

### 5. L'autorité de décision `KX108_ONLY` est déclarée à tous les niveaux

Les champs `decision_authority=KX108_ONLY`, `can_decide=False`, `allowed_to_decide=False`, `emits_act=False`, `emits_verdict=False` apparaissent dans :
- Le dictionnaire BOUNDARY de chaque module Python
- Chaque réponse de chaque route API
- Chaque packet de chaque script smoke
- L'index de release F40 (`OBSIDIA_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_20260529_061923.json`)

---

### 6. Le composant fonctionne sur 4 domaines hétérogènes

Bank, gps_defense_aviation, trading, unknown_refusal — chacun avec son propre payload, ses propres surfaces consultées, son propre résultat (READY_READONLY ou REFUSAL_READONLY). La robustesse multi-domaine est vérifiée par F37 (unit + direct call) et F38 (unit + live server).

---

## Ce que ça NE PROUVE PAS

### 1. Preuve formelle (Lean / TLA+)

Cette couche (F32–F40) est prouvée par smoke tests et unit tests Python — **pas par preuve formelle**. Les preuves formelles Lean et TLA+ existent pour d'autres couches du kernel Obsidia mais ne sont pas couplées à cette démo de la couche periphery/Brody.

**Implication :** Un auditeur exigeant une preuve formelle de correction de la boundary enforcement devra attendre la couche F50+ ou consulter les artefacts Lean séparément.

---

### 2. Le kernel KX108 est instancié et opérationnel

Le kernel KX108 est l'**autorité référencée**, non l'autorité instanciée dans cette démo. Les routes retournent `decision_authority=KX108_ONLY` comme déclaration de frontière — le handoff réel vers un kernel KX108 opérationnel est hors scope de F32–F40.

**Implication :** Cette démo prouve que Brody ne décide pas et que la frontière est déclarée. Elle ne prouve pas que les décisions sont effectivement prises par un kernel KX108 en production.

---

### 3. Résistance aux attaques adversariales

La frontière est vérifiée sur des entrées bien formées et des scénarios connus. Elle n'a **pas** été soumise à :
- Red-teaming systématique
- Adversarial prompting (injections dans `user_input`)
- Fuzzing des entrées `sigma_payload`
- Attaques par contournement de la couche FastAPI

**Implication :** Un acteur malveillant ayant accès au code source pourrait contourner la frontière. Ce composant est un proof-of-concept de gouvernance, pas un système durci pour environnement hostile.

---

### 4. Scalabilité et performance en production

Tous les tests sont mono-instance, mono-thread, sans charge concurrente. Aucune mesure de :
- Latence sous charge
- Throughput (requêtes/seconde)
- Résilience aux pannes
- Comportement en environnement distribué

n'est incluse dans F32–F40.

---

### 5. Persistance, mémoire et apprentissage

`neo4j_write=false`, `graphiti_write=false`, `memory_write=false` — ces drapeaux sont **exacts pour cette démo**. Cela signifie également qu'aucun apprentissage, aucun contexte persistant, et aucune évolution du modèle à partir des interactions n'est démontré.

**Implication :** Brody répond de manière statique à partir de son état runtime au moment de l'appel. Il ne s'améliore pas, ne mémorise pas, ne s'adapte pas entre les sessions.

---

### 6. Intégration système complète

Cette démo expose 7 routes API dans un serveur FastAPI standalone. Elle ne prouve pas :
- L'intégration avec un système de trading réel
- L'intégration avec des systèmes GPS/défense réels
- La connection à une base Neo4j en production
- L'interopérabilité avec d'autres composants Obsidia (Sigma, kernel, etc.)

---

## Résumé pour auditeur

| Claim | Prouvé | Niveau de preuve |
|-------|--------|-----------------|
| Boundary déclarée à tous les niveaux | ✅ | Unit tests + smoke + live server |
| Aucun token décisionnel émis | ✅ | 474 checks cumulés |
| Chaîne palier complète et étiquetée | ✅ | 10 git tags + SHA256 |
| Frontière tient sur vrai serveur | ✅ | 3 live-server proofs |
| Preuve formelle (Lean/TLA+) | ❌ | Non disponible à cette couche |
| Kernel KX108 instancié | ❌ | Hors scope F32–F40 |
| Résistance adversariale | ❌ | Non testé |
| Performance production | ❌ | Non mesuré |

---

*F41 RC1 · Honest Proof Perimeter Audit · READONLY · KX108_ONLY · Generated 2026-05-29*
