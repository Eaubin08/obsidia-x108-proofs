# OBSIDIA CHAT — Runbook opérateur complet

> Terminal fusionné : router pré-inférence → mémoire par sens → Brody live → Claude.
> Un seul point d'entrée pour tout faire, au coût d'inférence minimal.
> `decision_authority = KX108_ONLY` — le chat propose et exécute la cascade, il ne décide jamais contre le cadre.

---

## 1. Démarrage

```powershell
# Stack complète (kernel 3001, API Brody 8000, connecteurs) — si pas déjà UP
obsidia                          # boot conditionnel + terminal obsidia>
# ou seulement le chat (la stack peut être down : fallback automatique)
obsidia chat                     # boucle interactive
obsidia chat "ta requête"        # one-shot
```

`obsidia chat` active automatiquement le POST Brody vers l'API 8000
(lanceur humain explicite — conforme doctrine cockpit).

## 2. Ce qui se passe à chaque requête (cascade)

```
ta phrase
 → router (IR + gates + topic)                    0 token, déterministe
 → Level 0 : status / HOLD / DENY / CLARIFY       réponse immédiate, 0 token
 → Level 2 : mémoire par sens (34 arbres)         réponse canonique, 0 token
 → Level 1 : Brody réel (API 8000)                local, 0 token distant
 → Level 3 : claude -p + cadre invariants          SEUL cas payant
```

Toute requête est loggée dans `audit/obsidia_gateway_usage.jsonl`
(`model_call_avoided`, route, level) — données MEASURED.

## 3. Commandes internes de la boucle

| Commande | Effet |
|---|---|
| `metrics` | Compteurs session : appels LLM évités / payants |
| `exit` / `quit` | Quitter |
| toute autre phrase | Entre dans la cascade |

## 4. Utiliser Claude pour BUILDER via le chat

Les demandes de build/code escaladent en Level 3 (`claude -p`) avec le cadre
Obsidia injecté (KX108_ONLY, Invariant > Réversibilité > Score > Projection,
DecisionTicket pour tout MODIFY, no_auto_act/commit/push).

Exemples qui escaladent :
```
obsidia chat "code un connecteur sante qui appelle le kernel"
obsidia chat "refactorise scripts/obsidia_gateway.py pour ajouter un cache"
obsidia chat "genere les tests du reflex reducer"
```
Exemples qui NE COÛTENT RIEN (résolus avant Claude) :
```
obsidia chat "status de la stack"                  → Level 0
obsidia chat "explique le quintuplet canonique"    → mémoire, 0 token
obsidia chat "git push force"                      → HOLD + pause humaine
obsidia chat "capabilities brody"                  → Brody local
```
Règle d'or : formule d'abord ta question « sèche » — si la cascade répond
localement, tu viens d'économiser un appel. Sinon reformule en demande de
build explicite (verbes : code / implémente / refactorise / génère).

## 5. Sessions longues de build (Claude Code interactif)

Pour un chantier multi-fichiers, le chat one-shot ne suffit pas :
lance `claude` dans le repo — le hook UserPromptSubmit y injecte le même
verdict router à chaque message, et le serveur MCP `obsidia` (après
approbation au démarrage) donne à Claude les outils :
- `obsidia_route`          — verdict pré-inférence
- `obsidia_memory_search`  — mémoire par sens AVANT de lire des fichiers
- `obsidia_shazam`         — tagging 34 arbres

## 6. Entretenir la mémoire (rangement / tri / flux)

```powershell
# après toute évolution de MATH_MEMORY_INDEX ou de l'extension :
python scripts/export_gateway_memory_index.py
```
- Extension des arbres (bio, cosmos, nuage de points…) :
  `registries/tree_keywords_extension.json` — éditable à la main,
  fusionnée au canon MMONDE sans le modifier. Ajouter les pluriels
  (matching mots entiers, pas de stemming).
- La promotion canonique SRL (presave_buffer → CANONICAL) reste une
  décision opérateur.

## 7. Variables d'environnement

| Variable | Défaut | Rôle |
|---|---|---|
| `OBSIDIA_ROUTER_ROOT` | `C:\Users\User\Desktop\obsidia-router` | Emplacement du router |
| `OBSIDIA_BRODY_BASE` | `http://127.0.0.1:8000` | API Brody (fixé par `obsidia chat`) |
| `OBSIDIA_GATEWAY_ALLOW_BRODY_POST` | `1` via `obsidia chat` | POST Brody (lanceur humain) |
| `FIREWORKS_API_KEY` | — | Uniquement pour le benchmark live du router |

## 8. Pannes et fallbacks (fail-open partout)

| Symptôme | Cause | Effet réel |
|---|---|---|
| `[brody structural]` au lieu d'une vraie réponse | API 8000 down ou POST non autorisé | La cascade continue, rien ne casse |
| `claude CLI introuvable` | claude pas dans le PATH | Level 3 indisponible, le reste vit |
| Pas de verdict router dans Claude Code | router déplacé/cassé | Hook silencieux, session normale |
| Mémoire ne matche jamais | index absent | `python scripts/export_gateway_memory_index.py` |

## 9. Restauration d'urgence

```powershell
git checkout backup/pre-wiring-full-20260708    # dans l'un ou l'autre repo
```

## 10. Ce que le chat ne fait PAS (par doctrine)

- Jamais de commit/push automatique (HOLD sur toute action monde).
- Jamais d'exécution Obsidure ni de mutation kernel/preuves scellées.
- Jamais d'écriture mémoire autonome (`memory_write=False`).
- DENY/HOLD/CLARIFY = le chat s'arrête et te demande — c'est voulu.
