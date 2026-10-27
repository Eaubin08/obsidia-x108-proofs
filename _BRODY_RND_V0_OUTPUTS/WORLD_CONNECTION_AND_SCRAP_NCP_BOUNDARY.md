# WORLD_CONNECTION_AND_SCRAP_NCP_BOUNDARY.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Date: 2026-06-17

---

## La frontière Monde : Architecture World Call Gateway

### Principe fondamental

Obsidia X-108 ne se connecte **jamais directement au monde réel** en dehors d'un pipeline d'autorisation strict. Toute action vers le monde extérieur passe par la World Call Gateway.

### Pipeline World Call Gateway (V4)

```
ActionCandidate
  ↓
classify_action_risk()       → ActionRiskClass
  ↓
classify_world_call()        → WorldCallClass
  ↓
compute_autonomy_level()     → AutonomyLevel (0–5)
  ↓
issue_sovereign_ticket()     → SovereignTicket (dry_run_only=True TOUJOURS)
  ↓
ObsidiaGateway.check()       → GatewayDecision (egress_allowed=False TOUJOURS)
  ↓
WorldActionBus.publish()     → journal local append-only (pas d'egress réel)
```

### Invariants absolus (V4)

| Invariant | Valeur | Signification |
|---|---|---|
| `egress_allowed` | **False** (toujours) | Aucune sortie vers le monde réel |
| `dry_run_only` | **True** (toujours) | Tout ticket est en mode dry-run |
| No Ticket → BLOCK | Absolu | Pas de ticket = BLOCK immédiat |
| Append-only | Absolu | WorldActionBus et TicketStore n'écrasent jamais |
| Secret boundary | Absolu | `assert_no_secret_in_agent_payload()` avant tout gateway pass |

---

## WorldCallClass — Hiérarchie des types d'appels monde

| Classe | Bloquée | Description |
|---|---|---|
| `NO_WORLD_CALL` | Non | Pas d'interaction monde |
| `READ_ONLY` | Non | Lecture seule vers monde |
| `REVERSIBLE` | Non | Action réversible |
| `IRREVERSIBLE` | Non (niveau autonomie 4+) | Action non réversible, nécessite autonomie élevée |
| `CRITICAL` | **Oui** | Action critique → BLOCK |
| `FORBIDDEN` | **Oui** | Action interdite → BLOCK |

---

## AutonomyLevel (0–5)

La gateway calcule un niveau d'autonomie avant d'autoriser un type d'action. Plus le niveau est élevé, plus l'action est sensible. Les niveaux CRITICAL et FORBIDDEN sont bloqués quel que soit le niveau.

---

## Modules World Calls (periphery/world_calls/)

| Fichier | Rôle |
|---|---|
| `world_call_classifier.py` | Classifie les appels monde |
| `action_risk_classifier.py` | Classifie le risque de l'action |
| `autonomy_level_matrix.py` | Calcule le niveau d'autonomie |
| `sovereign_ticket.py` | Génère les tickets souverains |
| `ticket_store.py` | Stocke les tickets (append-only) |
| `world_action_bus.py` | Bus d'actions monde (journal append-only) |
| `secret_boundary.py` | Frontière des secrets |
| `obsidia_gateway.py` | Gateway principale (egress_allowed=False) |
| `egress_policy.py` | Politique d'egress |
| `route_policy_x25.py` | Politique de routage X25 |
| `world_executor_dryrun.py` | Exécuteur dry-run |

**Schémas JSON :**
- `periphery/schemas/sovereign_ticket.schema.json`
- `periphery/schemas/world_action_event.schema.json`

---

## NCP / Scrap — Contexte

**NCP (Network Connection Point)** et **Scrap** sont des termes Obsidia désignant les points de connexion vers les systèmes externes et la zone de récupération de données brutes.

Observé via :
- `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/09_MCP_BRIDGE_OBSIDIA_IR/` — Bridge MCP vers IR (Interface Réelle)
- La frontière NCP/Scrap représente la ligne entre ce qui est "monde simulé" et ce qui touche l'infrastructure réelle

**Règle de frontière (extraite du CLAUDE.md) :**
- `NO RUNTIME BINDING` — aucune liaison runtime vers le monde
- `NO WEB, NO SCRAPING, NO NETWORK, NO ACT` — aucune connexion réseau en mode DISCOVERY
- `NO PROVIDER BINDING, NO PATH COMPUTE` — aucune liaison fournisseur

---

## Graphiti et la mémoire graphe

**Graphiti** est le système de mémoire graphe d'Obsidia. Il stocke les entités, relations et épisodes en mémoire sous forme de graphe (Neo4j).

Dans ce repo, Graphiti est **en mode READ-ONLY** :
- `_graphiti_readonly_indexes/` — index en lecture seule uniquement
- `.graph-memory/ALLOWLIST.md` / `DENYLIST.md` — politique d'inclusion/exclusion
- `.graph-memory/SANDBOX_POLICY.md` — politique sandbox (pas d'écriture)
- `.graph-memory/DRY_RUN_PLAN.md` — plan de dry-run

**Invariant mission :**
```
NO GRAPHITI WRITE, NO NEO4J WRITE
```

---

## La règle DEMO vs RÉEL

Dans le repo :
- `Demo-obsidia-x108-proof/` (racine) — version démo décompressée
- `Demo-obsidia-x108-proof-main (5).zip` — archive démo

La démo illustre le périmètre public sans exposer le moteur de production.

---

## Connectors

`connectors/` — Connecteurs métier. Non lus en profondeur (scope production propriétaire).

`periphery/adapters/` :
- `bank_adapter.py`
- `gps_adapter.py`
- `trading_adapter.py`

Ces adaptateurs font le pont entre les formats métier et le format canonique Sigma.

---

## Résumé des frontières

```
[Monde réel]
     |
     ← WorldCallGateway (egress_allowed=False, dry_run_only=True)
     |
[ObsidiaGateway]
     |
     ← Sigma → X-108 → OS3
     |
[Agents / BRODY]
     |
     ← Graphiti (READ-ONLY dans ce repo)
     |
[Mémoire / Contexte]
```

Aucun chemin ne traverse la frontière vers le monde réel en V4. Tout est dry-run.

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
