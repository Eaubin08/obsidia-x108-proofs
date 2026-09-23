# BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_FREEZE_20260527

Status: FROZEN_PASS

Date: 2026-05-27

---

## Scope

Freeze de la phase 12L : exposition de la couche Adaptive Response Policy / Sigma
dans le RightPanel UI.

Ce freeze cloture la surface de lecture Brody :
terminal (12J-G) + API (12J-G) + UI/RightPanel (12L).

---

## Base stable avant ce freeze

| Commit | Phase | Titre | Status |
|---|---|---|---|
| `7b9ac74` | **12J-G** | Adaptive Response Policy terminal/API freeze | FROZEN_PASS |
| `4b3d920` | **12K** | Global day synthesis 2026-05-27 | SYNTHESIS_PASS |
| `e6fc212` | **12L** | feat: expose Brody adaptive sigma policy in RightPanel | COMMIT_PUSHED |

Tag present : `BRODY_PHASE12J_G_TERMINAL_API_SIGMA_FREEZE_20260527`

HEAD avant ce freeze : `e6fc212`

---

## Changement 12L

### Fichier modifie

```
apps/obsidia-workbench/src/components/RightPanel.tsx
```

### Nature

Ajout d'un composant React readonly `AdaptiveSigmaSection`.
Insertion entre `TrueVoiceSection` et `DomainRaccordSection` dans `ContextTab`.

### Source de donnees

```
lastBackendPayload.true_voice_snapshot.adaptive_response_policy
```

Lecture via `asRecord()` — pattern identique aux sections existantes.
Guard : `if (!Object.keys(pol).length) return null`
La section est invisible si le payload ne contient pas la policy.

### Fichiers non modifies

```
apps/obsidia-workbench/src/App.tsx              — non modifie
apps/obsidia_api/brody_adaptive_response_policy.py — non modifie
apps/obsidia_api/brody_true_voice_adapter.py    — non modifie
apps/obsidia_api/brody_domain_raccord_adapter.py — non modifie
apps/obsidia_api/routes/brody.py                — non modifie
Graphiti / Neo4j / X108 / contracts             — non modifies
```

---

## Champs visibles dans le RightPanel

| Champ | Colorisation UI |
|---|---|
| status | READY=pass, autre=hold |
| response_size | BOUNDARY_COMPACT=block, DEEP=brody, MEDIUM=pass, SHORT=dtext |
| density | neutre |
| context_need | brody |
| sigma_pressure | HIGH=block, MEDIUM=hold, LOW=pass |
| reason | texte libre |
| observed_answer_size | — |
| observed_answer_words | — |
| boundary_detected | true=block, false=dtext |
| decision_authority | kernel |
| readonly | pass |

---

## Build

```
tsc -b + vite build
1641 modules transformes
0 erreur TypeScript — 0 warning
STATUS : BUILD_OK
```

---

## Smoke test — 3 cas live (Checkpoint 2)

Endpoint : POST http://localhost:8012/api/brody/chat

| Cas | voice_source | response_size | context_need | sigma_pressure | Section | Verdict |
|---|---|---|---|---|---|---|
| code_debug | DOMAIN_RACCORD_CODE_DEBUG | MEDIUM | DEBUG | MEDIUM | VISIBLE | **PASS** |
| architecture_canonical | DOMAIN_RACCORD_ARCHITECTURE | DEEP | ARCHITECTURE | MEDIUM | VISIBLE | **PASS** |
| act_boundary | ACTION_BOUNDARY | BOUNDARY_COMPACT | BOUNDARY | HIGH | VISIBLE | **PASS** |

TOTAL : 3 cas | PASS : 3 | FAIL : 0

---

## Invariants KX108_ONLY — confirmes

```
decision_authority  : KX108_ONLY
readonly            : true
advisory_only       : true
context_signal_only : true
allowed_to_decide   : false
allowed_to_act      : false
emits_act           : false
emits_verdict       : false
memory_write        : false
graphiti_write      : false
kernel_mutation     : false
x108_mutation       : false
```

L'UI n'ajoute aucun role decisionnel.
Elle lit et affiche uniquement ce que Brody a calcule cote API sous KX108_ONLY.

---

## Limite

- Le RightPanel affiche la policy. Il ne la calcule pas. Il ne la modifie pas.
- Aucun nouveau calcul UI.
- Aucun role d'action ajoute a l'UI.
- L'UI reste une fenetre de lecture readonly sur l'etat interne de Brody.

---

## Surface Brody complete apres 12L

| Surface | Phase | Status |
|---|---|---|
| Terminal | 12I-E + 12J-G | FROZEN |
| API `/api/brody/chat` | 12J-G | FROZEN |
| UI chat | 12F | FROZEN |
| RightPanel (7 sections) | 12I-E | FROZEN |
| RightPanel Adaptive Sigma | **12L** | **FROZEN** |

---

## Decision

La couche Adaptive Response Policy / Sigma est maintenant exposee sur
toutes les surfaces Brody : terminal, API, et RightPanel UI.

Brody expose sa respiration en lecture partout.
Aucun role de decision n'a ete ajoute.
KX108_ONLY stable sur l'ensemble de la chaine.

STATUS : PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_FROZEN
