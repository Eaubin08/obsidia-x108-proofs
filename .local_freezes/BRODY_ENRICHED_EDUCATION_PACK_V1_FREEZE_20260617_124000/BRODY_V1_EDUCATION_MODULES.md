# BRODY_V1_EDUCATION_MODULES.md
# Pack: BRODY_ENRICHED_EDUCATION_PACK_V1 — 2026-06-17
# Statut : VALIDATED_BY_REPO uniquement — aucune synthèse non vérifiée
# Sources citées explicitement dans chaque module

---

## Règles de ce document

- Chaque affirmation est sourcée par un chemin repo direct.
- Aucun chiffre Cowork non vérifié n'est inclus (voir BRODY_V1_FORBIDDEN_BELIEFS.md).
- Les modules sont à l'usage éducatif — pas pour produire des décisions opérationnelles.
- Structure calquée sur les 7 modules Cowork V0 — contenu re-sourcé depuis le repo.

---

## MODULE 01 — Qu'est-ce qu'Obsidia X-108 ?

**Niveau :** Débutant
**Source :** `docs/KERNEL_OVERVIEW.md`, `PUBLIC_STATUS.md`

### La question fondamentale

Obsidia X-108 répond à une question que les systèmes d'IA conventionnels ignorent :

**"Comment prouver qu'une action avait le droit d'être exécutée ?"**

Les systèmes habituels agissent, puis vérifient après. X-108 inverse le paradigme :
les invariants mathématiques sont évalués **avant** chaque action.
Si les invariants ne sont pas respectés → l'action ne part pas.

### Ce qu'est X-108

- Un **kernel de gouvernance déterministe** : pas un LLM, pas un heuristique.
- Un **juge mathématique ex ante** : il vérifie avant d'autoriser.
- Un système dont les preuves sont vérifiables par n'importe qui : Lean 4, TLA+, Python.

### Ce que X-108 n'est pas

- X-108 n'est pas une IA générative.
- X-108 ne "juge" pas avec du bon sens — il applique des invariants formels.
- X-108 ne peut pas être contourné par Brody, Sigma, ou tout autre composant.

### Jalons publics (VALIDATED_BY_REPO)

| Jalon | Détail |
|---|---|
| `p1-freeze-2026-04-22` | Tag officiel P1 |
| Commit `99e966a` | Gel public P1 |
| `v1.0.0-stable-kernel` | Release GitHub |
| 5 invariants Lean 4 (sans sorry) | D1, E2, G1, G2, G3 |
| TLA+ : 1,2M états, 0 violation | Vérifiable localement |

---

## MODULE 02 — Le Kernel X-108

**Niveau :** Intermédiaire
**Source :** `proofs/lean/`, `formal/tla/`, `docs/KERNEL_OVERVIEW.md`

### Les 3 verdicts possibles

Toute décision X-108 aboutit à l'un de ces 3 verdicts :

| Verdict | Signification | Condition |
|---|---|---|
| `ACT` | Tous invariants respectés → exécution | Certitude suffisante |
| `HOLD` | Certitude insuffisante → attente | Ambiguïté résoluble |
| `BLOCK` | Invariant violé → blocage immédiat | Violation détectée |

Ces verdicts sont **déterministes** : à entrée identique, verdict identique.
Il n'y a pas de "peut-être", pas de "selon le contexte" dans la décision finale.

### Les 5 invariants Lean 4 (VALIDATED_BY_REPO)

Prouvés formellement dans `proofs/lean/` — sans `sorry` (pas de raccourci) :

| ID | Nom | Ce qu'il garantit |
|---|---|---|
| D1 | Déterminisme | Même input → même verdict |
| E2 | Exclusivité | Un seul verdict possible par décision |
| G1 | Garde amont | Les invariants sont vérifiés avant l'action |
| G2 | Immuabilité | Le kernel ne peut pas être reconfiguré en cours de route |
| G3 | Traçabilité | Chaque décision est tracée de façon immuable |

### TLA+ (VALIDATED_BY_REPO)

- 1 200 000 états explorés
- 0 violation d'invariant
- Source : `formal/tla/X108.tla`

### Aucune exception possible

Si les invariants ne sont pas respectés : `BLOCK` immédiat.
X-108 ne connaît pas le "cas d'urgence" ni le "contournement justifié".

---

## MODULE 03 — BRODY : le moteur de contexte

**Niveau :** Intermédiaire
**Source :** `apps/obsidia_api/cic/`, `apps/obsidia_api/main.py`

### Ce qu'est Brody

Brody est le composant de contexte naturel d'Obsidia X-108.
Il est classifié `FIRST_CLASS_X108_MODULE` dans la couche PERIPHERY.

Son rôle unique :
1. Recevoir des questions en langage naturel
2. Assembler le CIC (Causal Identity Context)
3. Formuler des réponses compréhensibles
4. Transmettre le contexte enrichi au pipeline

**Brody ne décide jamais.** C'est sa seule contrainte absolue.

### Le contrat Brody (BRODY_RESPONSE_CONTRACT_V1)

8 invariants vérifiables à chaque réponse :

```python
decision_authority   = "KX108_ONLY"
advisory_only        = True
memory_write         = False
kernel_mutation      = False
emits_act            = False
emits_verdict        = False
readonly             = True
context_signal_only  = True
```

Toute violation déclenche : `BRODY_CONTRACT_VIOLATION`.

### Le CIC — Causal Identity Context

Assemblé à chaque appel par `build_cic_readonly_context()`
(source : `apps/obsidia_api/cic/cic_readonly_pack_provider.py`, commit 783e664).

21 clés retournées — toutes readonly. Extraits importants :

```
authority              = "NONE"
decision_authority     = "KX108_ONLY"
canonical_write        = False
ncp_context            = { ncp_active: False, fetch: False, authority: "NONE" }
scraping_context       = { scraping_active: False, quarantine_policy: "WEB_SCRAPE_QUARANTINED" }
cic_receipt            = { receipt_id: "CIC_RCP_489413558D392A28", ... }
```

### Le receipt CIC

```
invocation_hash = SHA256(domain + source_zip_sha256 + confirmed_metric_families)
receipt_id      = "CIC_RCP_" + invocation_hash[:16].upper()
```

Source : `apps/obsidia_api/cic/cic_receipt_pack.py`

Le receipt est **stable** : le même appel avec le même contexte donne toujours le même hash.
Cela permet le replay et l'audit de n'importe quelle décision passée.

### Ce que Brody ne peut pas faire

| Action | Statut | Invariant |
|---|---|---|
| Décider ACT/HOLD/BLOCK | INTERDIT | `emits_verdict=False` |
| Appeler le réseau | INTERDIT | `ncp_active=False`, `web_scrape_allowed=False` |
| Écrire en mémoire persistante | INTERDIT | `memory_write=False` |
| Muter le kernel | INTERDIT | `kernel_mutation=False` |
| Émettre un acte | INTERDIT | `emits_act=False` |

---

## MODULE 04 — Sigma : l'agrégateur d'agents

**Niveau :** Avancé
**Source :** `sigma/contracts.py`, `sigma/domains/`

### Le rôle de Sigma

Sigma est le moteur d'agrégation des votes d'agents spécialisés par domaine.
Sigma agrège → X-108 décide.
Sigma ne décide pas. Il recommande.

### Le cycle Sigma

```
[Agents domaine]     — chacun évalue un aspect (fraude, liquidité, etc.)
       |
[Sigma Engine]       — agrège les scores avec pondération
       |
[Score agrégé]       — transmis à X-108
       |
[X-108 KERNEL]       — applique les invariants et émet le verdict
```

### Exemple de vote (domaine Banking)

```
FraudDetectionAgent       → score 0.95 (BLOCK recommandé)
BehaviorAnalysisAgent     → score 0.80 (BLOCK recommandé)
TransactionValidationAgent → score 0.30 (ACT recommandé)
Agrégation Sigma           → 0.68
Seuil BLOCK               → 0.60
Verdict X-108             → BLOCK
```

### Agents par domaine (VALIDATED_BY_REPO)

| Domaine | Source | Agents |
|---|---|---|
| Banking | `sigma/domains/bank_agents.py` | FraudDetection, BehaviorAnalysis, TransactionValidation |
| Trading | `sigma/domains/trading_agents.py` | MarketData, Liquidity, Volatility, Momentum |
| GPS/Défense | `sigma/domains/gps_defense_aviation_agents.py` | (spécialisés navigation) |
| E-Commerce | `sigma/domains/ecom_agents.py` | TrafficQuality, IntentAnalysis, FraudDetection |
| Meta | `sigma/domains/meta_agents.py` | IdentityVerification, AnomalyDetection, PolicyCompliance |

### Le fichier ragnarok — rappel d'exclusion

`sigma/contracts.broken-ragnarok.py` est **EXCLUDE_ABSOLUTE**.
Il teste les modes d'échec total — ne jamais le citer comme exemple de fonctionnement normal.

---

## MODULE 05 — Preuves formelles : Lean 4 et TLA+

**Niveau :** Expert
**Source :** `proofs/lean/`, `formal/tla/`, `proofs/tla/`

### Lean 4 : preuves sans sorry

Lean 4 est un assistant de preuve mathématique.
"Sans sorry" signifie qu'aucun raccourci logique n'a été utilisé.
Chaque preuve est vérifiable de façon indépendante en exécutant `lake build`.

Les 5 invariants (D1, E2, G1, G2, G3) sont tous prouvés.

### TLA+ : model-checking à large échelle

TLA+ (Temporal Logic of Actions) permet de vérifier des propriétés
de systèmes distribués et concurrents sur un grand nombre d'états.

Résultats : 1 200 000 états explorés, 0 violation.
Source : `formal/tla/X108.tla`

### Les verifiers Python

Des vérificateurs Python permettent de rejouer les preuves localement :
- `verify_all.py`
- `verify_decision.py`
- `verify_merkle.py`

### Chaîne de preuve cryptographique

```
Décision X-108
  → Decision ID + Trace ID
  → Merkle Root     (immuabilité — sigma/merkle_root_generator.py)
  → RFC3161 stamp   (preuve temporelle — proofs/rfc3161/)
  → CIC Receipt     (contexte causal — cic_receipt_pack.py)
```

---

## MODULE 06 — Domaines réels

**Niveau :** Intermédiaire
**Source :** `sigma/domains/`, `sigma/examples/`, `docs/`

### Les 5 domaines actifs (VALIDATED_BY_REPO)

| Domaine | Source agents | Exemples |
|---|---|---|
| Banking | `sigma/domains/bank_agents.py` | `sigma/examples/bank_*.json` |
| Trading | `sigma/domains/trading_agents.py` | `sigma/examples/trading_*.json` |
| GPS / Défense | `sigma/domains/gps_defense_aviation_agents.py` | `sigma/examples/gps_*.json` |
| E-Commerce | `sigma/domains/ecom_agents.py` | `sigma/examples/ecom_normal.json` |
| Meta / Gouvernance | `sigma/domains/meta_agents.py` | (exemples intégrés) |

### Pourquoi ces domaines ?

Ces domaines ont en commun :
- Des décisions irréversibles ou coûteuses à corriger
- Des signaux conflictuels fréquents (fraude vs légitimité, sources GPS contradictoires)
- Des contraintes réglementaires ou de sécurité critiques

X-108 est spécialement adapté aux situations où l'erreur a des conséquences immédiates.

### Gencoin (hors token)

Gencoin est la couche économique d'Obsidia X-108.
**Gencoin n'est pas un token crypto.**
Source : `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`

---

## MODULE 07 — World Call Gateway

**Niveau :** Avancé
**Source :** `periphery/world_calls/`

### La frontière monde

Le World Call Gateway est la frontière absolue entre X-108 et le monde extérieur.
Aucune action ne sort de X-108 sans passer par ce gateway.

### Le pipeline World Call

```
[ActionCandidate]
     |
classify_action_risk()      → ActionRiskClass
     |
classify_world_call()       → WorldCallClass
     |
compute_autonomy_level()    → AutonomyLevel (0-5)
     |
issue_sovereign_ticket()    → SovereignTicket (dry_run_only=True TOUJOURS)
     |
ObsidiaGateway.check()      → GatewayDecision (egress_allowed=False TOUJOURS)
     |
WorldActionBus.publish()    → journal local append-only (aucun egress réseau)
```

### Les 2 invariants absolus du gateway

1. `egress_allowed = False` — **TOUJOURS** — aucune sortie réseau réelle
2. `dry_run_only = True` — **TOUJOURS** — mode simulation permanent

### Ce que produit le WorldActionBus

Le `WorldActionBus` est un **journal local append-only**.
Il enregistre toutes les intentions d'action et leurs verdicts.
Il n'est **pas** une interface vers le monde extérieur.

### Protection supplémentaire

`assert_no_secret_in_agent_payload()` est exécuté avant tout gateway pass.
Aucun secret ne peut sortir via le WorldActionBus même en théorie.
