# FAQ Investisseur / Jury — Obsidia X-108 (F41 RC1)

**Mode:** READONLY · KX108_ONLY · emits_act=false  
**Date:** 2026-05-29

---

## Questions fondamentales

---

**Q1 : Qu'est-ce qu'Obsidia X-108 ?**

Obsidia X-108 est un kernel de gouvernance déterministe. Son rôle est de garantir qu'un composant d'IA (ici : Brody) reste dans un rôle purement advisory — jamais décisionnel. L'autorité de décision est réservée à `KX108_ONLY`, c'est-à-dire au kernel Obsidia lui-même. La frontière est appliquée à trois niveaux indépendants : module Python, route API, et contenu de la réponse.

---

**Q2 : Que fait Brody et que ne fait-il pas ?**

Brody (Boundary-Respecting Observational Decision Yielder) :

| Fait | Ne fait pas |
|------|-------------|
| Consulte 7 surfaces runtime | Décide |
| Agrège l'état du système | Exécute des actions |
| Produit une réponse informative | Mute l'état (mémoire, base de données) |
| Retourne un BOUNDARY dict vérifiable | Émet des verdicts souverains |
| Traite 4 domaines hétérogènes | Appeler des services externes |

---

**Q3 : Quelles sont les 7 surfaces runtime consultées ?**

| Surface | Rôle |
|---------|------|
| `sigma_dispatcher` | Dispatch des signaux de contexte |
| `tree_signal_packet` | Paquet de signaux arborescents |
| `monitoring_adapters` | Adaptateurs de surveillance |
| `operator_view_packet` | Vue opérateur synthétique |
| `brody_runtime_context` | Contexte runtime Brody |
| `workflow_governance_readonly` | Gouvernance de workflow (lecture seule) |
| `neo4j_guide_bridge` | Pont de guidage Neo4j (lecture seule) |

---

## Questions sur la preuve

---

**Q4 : Comment la frontière est-elle appliquée ?**

À trois niveaux simultanément et indépendamment :

1. **Module** : le dictionnaire `BOUNDARY` (15 drapeaux booléens) est calculé et retourné par chaque fonction Python. Il n'y a pas de chemin de code qui retourne sans ce dictionnaire.

2. **Route** : chaque route FastAPI appelle `safe_backend_response()`, qui vérifie la source, nettoie la réponse, et garantit la présence des flags boundary.

3. **Réponse** : un scan par regex `\bTOKEN\b` vérifie l'absence des tokens interdits (`ALLOW`, `HOLD`, `BLOCK`, `ACT`, `DECIDE`, `VERDICT`) dans tout texte généré.

---

**Q5 : Est-ce formellement prouvé ?**

Non, pas à cette couche. Les preuves F32–F40 sont des smoke tests et des unit tests Python (103/103, 474 checks cumulés). Des preuves formelles Lean existent pour d'autres couches du kernel Obsidia mais ne couvrent pas la couche periphery/Brody démontrée ici.

Pour un audit complet du périmètre probatoire (ce qui est prouvé et ce qui ne l'est pas), voir : `docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md`.

---

**Q6 : Comment vérifier les preuves indépendamment ?**

1. Cloner le dépôt à `HEAD=23ca559` (tag `BRODY_F39_OPERATOR_DEMO_PACK_CONSOLIDATION_PALIER_20260529`)
2. Lancer `python -m pytest tests/api/ -q` → 103 passed
3. Lancer `python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8011`
4. Lancer `python scripts/smoke_f38_multi_domain_live_uvicorn_api.py` → PASS 141/141
5. Vérifier les SHA256 des preuves live dans `docs/runtime/OBSIDIA_F40_RELEASE_CANDIDATE_DEMO_FREEZE_INDEX_20260529_061923.json`

Tout est vérifiable sans accès spécial, sans credentials, sans infrastructure externe.

---

**Q7 : Que signifie « RUNTIME_SMOKE_ONLY_NOT_LEAN_PROVEN » ?**

C'est le champ `proof_status` présent dans tous les artéfacts de preuve. Il indique honnêtement que la preuve de cette couche repose sur l'exécution runtime (tests unitaires, smoke scripts, preuves live-server) — pas sur une preuve formelle (Lean, TLA+, Coq). C'est une déclaration d'honnêteté probatoire, pas une limitation cachée.

---

## Questions sur la valeur et le positionnement

---

**Q8 : Quelle est la différence avec un simple prompt système ?**

Un prompt système est une contrainte comportementale — il peut être ignoré, oublié, ou contourné par un modèle suffisamment capable ou mal aligné. Obsidia enforces the boundary at the **output layer**, independently of the model's internal behavior.

| Approche | Application | Auditabilité | Indépendance du modèle |
|----------|-------------|--------------|----------------------|
| Prompt système | Comportementale | Aucune | Oui |
| Fine-tuning RLHF | Interne | Aucune | Non |
| Filtres post-hoc | Couche sortie | Partielle | Oui |
| **Obsidia X-108** | **Couche architecture** | **Complète (SHA256, tests, tags)** | **Oui** |

---

**Q9 : Quels secteurs cible cette technologie ?**

Tout secteur où une IA advisory doit coexister avec une autorité décisionnelle séparée et auditable :

- **Finance** : IA qui analyse les transactions sans les approuver
- **Défense / Aviation** : IA qui interprète les signaux de navigation sans commander les actionneurs
- **Médical** : IA qui synthétise les données patient sans prescrire
- **Infrastructure critique** : IA qui surveille sans contrôler

---

**Q10 : Qui décide, si Brody ne décide pas ?**

`KX108_ONLY` — le kernel Obsidia. Dans cette démo, le kernel est la référence d'autorité déclarative. Dans le système complet (roadmap F50+), le kernel KX108 est le composant qui reçoit les recommandations advisory de Brody, les évalue contre un ensemble de règles déterministes, et prend la décision finale.

La séparation est architecturale, pas seulement sémantique.

---

## Questions pratiques

---

**Q11 : Que faut-il pour faire tourner la démo ?**

- Python 3.10+
- FastAPI + uvicorn + pydantic (`pip install fastapi uvicorn pydantic`)
- Le dépôt cloné à HEAD=23ca559
- Un terminal PowerShell ou Bash
- Aucune base de données, aucun service externe, aucune API key

---

**Q12 : Quels sont les tokens interdits et pourquoi ?**

Les tokens interdits sont : `ALLOW · HOLD · BLOCK · ACT · DECIDE · VERDICT`

Ce sont les tokens qui signalent une décision ou une action dans le vocabulaire du système Obsidia. Leur présence dans une sortie Brody indiquerait une fuite de l'autorité décisionnelle. La vérification est faite par regex à limites de mot (pas de sous-chaîne) pour éviter les faux positifs sur des termes légitimes comme « transaction » (contient « act ») ou « activations ».

---

**Q13 : Qu'est-ce qu'un palier ?**

Un palier est une étape de la chaîne de preuve. Chaque palier :
- Ajoute une capacité ou une preuve spécifique
- Est étiqueté par un tag git signé
- A un rapport markdown et une preuve JSON SHA256
- Est couvert par au moins un test et un script smoke

La chaîne actuelle : F32 → F33 → F34 → F34B → F35 → F36 → F36B → F37 → F38 → F39 (10 paliers).

---

**Q14 : Quelle est la prochaine étape (F50+) ?**

La roadmap F50+ comprend :
- Intégration complète du kernel KX108 (handoff réel des décisions)
- Preuve formelle Lean de la boundary enforcement à cette couche
- Hardening adversarial (red-teaming, fuzzing)
- Déploiement multi-instance et mesures de performance

F40 RC1 est le Release Candidate de la couche démo. F41 est le pack narratif public. Les paliers suivants sont de la responsabilité de l'équipe Obsidia selon le calendrier de roadmap.

---

*F41 RC1 · Investor/Jury FAQ · READONLY · KX108_ONLY · Generated 2026-05-29*
