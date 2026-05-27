# BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_VALIDATION_20260527

Status: PASS_READY_FOR_REVIEW

Date: 2026-05-27

---

## Scope

Exposition de la couche Adaptive Response Policy / Sigma dans le RightPanel UI.

La donnee existait deja cote API/terminal depuis 12J-G.
Ce patch ajoute uniquement l'affichage UI readonly.
Aucune logique de calcul ajoutee. Aucun role decisionnel cree.

---

## Source stable

- **12J-G** `7b9ac74` — Adaptive Response Policy terminal/API freeze
  `brody_adaptive_response_policy.py` stable, stress 10/10 + live 6/6 PASS.

- **12K** `4b3d920` — Synthese globale journee 2026-05-27
  Etat consolide avant cette phase.

---

## Patch UI

### Fichier modifie

```
apps/obsidia-workbench/src/components/RightPanel.tsx
```

### Fichiers non modifies

```
apps/obsidia-workbench/src/App.tsx              — non modifie
apps/obsidia_api/brody_adaptive_response_policy.py — non modifie
apps/obsidia_api/brody_true_voice_adapter.py    — non modifie
apps/obsidia_api/brody_domain_raccord_adapter.py — non modifie
apps/obsidia_api/routes/brody.py                — non modifie
Graphiti / Neo4j / X108 / contracts             — non modifies
```

### Nature du patch

Ajout d'un composant React readonly `AdaptiveSigmaSection`.

**Source de donnees stricte :**
```
lastBackendPayload.true_voice_snapshot.adaptive_response_policy
```

Ce chemin est identique au pattern deja utilise par `TrueVoiceSection`
et `DomainRaccordSection` : lecture de `live.true_voice_snapshot` via `asRecord()`.

**Guard :** `if (!Object.keys(pol).length) return null`
La section est invisible si le payload ne contient pas la policy. Aucun affichage par defaut.

**Insertion :** entre `TrueVoiceSection` et `DomainRaccordSection` dans `ContextTab`.

### Champs affiches

| Champ | Source | Colorisation |
|---|---|---|
| status | pol.status | READY=pass, autre=hold |
| response_size | pol.response_size | BOUNDARY_COMPACT=block, DEEP=brody, MEDIUM=pass, SHORT=dtext |
| density | pol.density | mtext (neutre) |
| context_need | pol.context_need | brody |
| sigma_pressure | pol.sigma_pressure | HIGH=block, MEDIUM=hold, LOW=pass |
| reason | pol.reason | texte libre |
| observed_answer_size | pol.observed_answer_size | — |
| observed_answer_words | pol.observed_answer_words | — |
| boundary_detected | pol.boundary_detected | true=block, false=dtext |
| decision_authority | pol.decision_authority | kernel |
| readonly | pol.readonly | pass |

---

## Build

```
tsc -b + vite build
1641 modules transformes
347.73 kB JS / 20.70 kB CSS
0 erreur TypeScript
0 warning
Build time : 1.67s
STATUS : BUILD_OK
```

---

## Smoke test — 3 cas live

Endpoint : POST http://localhost:8012/api/brody/chat
Methode  : verification payload true_voice_snapshot.adaptive_response_policy

### Resultat

| Cas | voice_source | response_size | context_need | sigma_pressure | Section visible | Verdict |
|---|---|---|---|---|---|---|
| code_debug | DOMAIN_RACCORD_CODE_DEBUG | MEDIUM | DEBUG | MEDIUM | VISIBLE (26 keys) | **PASS** |
| architecture_canonical | DOMAIN_RACCORD_ARCHITECTURE | DEEP | ARCHITECTURE | MEDIUM | VISIBLE (26 keys) | **PASS** |
| act_boundary | ACTION_BOUNDARY | BOUNDARY_COMPACT | BOUNDARY | HIGH | VISIBLE (26 keys) | **PASS** |

TOTAL : 3 cas | PASS : 3 | FAIL : 0

### Detail code_debug

```
pol.status               : ADAPTIVE_RESPONSE_POLICY_READY
pol.response_size        : MEDIUM
pol.density              : HIGH
pol.context_need         : DEBUG
pol.sigma_pressure       : MEDIUM
pol.reason               : Code/debug intent requires operational steps without over-expanding.
pol.observed_answer_size : MEDIUM
pol.observed_answer_words: 121
pol.boundary_detected    : False
pol.decision_authority   : KX108_ONLY
pol.readonly             : True
pol.can_act              : False
pol.kernel_mutation      : False
pol.x108_mutation        : False
```

### Detail architecture_canonical

```
pol.response_size        : DEEP
pol.density              : HIGH
pol.context_need         : ARCHITECTURE
pol.sigma_pressure       : MEDIUM
pol.reason               : Architecture question requires component-level explanation.
pol.observed_answer_size : DEEP
pol.observed_answer_words: 181
pol.boundary_detected    : False
pol.decision_authority   : KX108_ONLY
pol.readonly             : True
```

### Detail act_boundary

```
pol.response_size        : BOUNDARY_COMPACT
pol.density              : HIGH
pol.context_need         : BOUNDARY
pol.sigma_pressure       : HIGH
pol.reason               : Boundary/risk request detected; response must stay compact, explicit, and non-actionable.
pol.boundary_detected    : True
pol.decision_authority   : KX108_ONLY
pol.readonly             : True
pol.can_act              : False
pol.kernel_mutation      : False
pol.x108_mutation        : False
```

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

Verifie sur les 3 cas du smoke test.
L'UI n'ajoute aucun role decisionnel. Elle lit et affiche uniquement.

---

## Ce que l'UI n'est pas

- L'UI n'invente pas de politique de reponse.
- L'UI ne calcule pas response_size ni sigma_pressure.
- L'UI ne modifie pas le payload backend.
- L'UI ne decide pas, n'agit pas, n'ecrit pas.
- L'UI expose ce que Brody a deja calcule cote API sous KX108_ONLY.

---

## Perimetre du commit a venir

Fichiers a stager :

```
apps/obsidia-workbench/src/components/RightPanel.tsx
docs/runtime/BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_VALIDATION_20260527.md
```

Message de commit propose :
```
feat: expose Brody adaptive sigma policy in RightPanel phase 12L
```

---

## Deferred

- Freeze 12L (Checkpoint 5) : rapport freeze separe apres validation humaine.
- Tag 12L : apres freeze.
- 12H mojibake cosmétique : toujours defere.
- 12M stress long multi-session : futur.

---

## Decision

La couche Adaptive Response Policy / Sigma est maintenant visible dans le RightPanel.

Brody expose sa respiration en terminal, en API, et maintenant en UI.
La surface de lecture est complete. Aucun role de decision n'a ete ajoute.

STATUS : PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_PASS_READY_FOR_REVIEW
