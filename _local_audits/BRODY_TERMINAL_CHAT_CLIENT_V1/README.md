# Brody Terminal Chat Client V1

> **Palier**: BRODY_TERMINAL_CHAT_CLIENT_V1
> **Date**: 2026-05-22
> **Principe**: *Le terminal est seulement une interface client. Brody reste derrière /api/brody/chat. X108 reste seule autorité décisionnelle.*

---

## Objectif

Interface terminal interactive pour dialoguer avec Brody via l'API locale `http://127.0.0.1:8000/api/brody/chat`.

Ce n'est PAS une UI React, PAS un patch Brody, PAS un write mémoire.

---

## Fichiers créés

| Fichier | Rôle |
|---|---|
| `scripts/brody_terminal_chat.py` | Client CLI interactif |
| `scripts/run_brody_terminal_chat.ps1` | Lanceur PowerShell (UTF-8) |
| `tests/api/test_brody_terminal_chat_client.py` | Tests unitaires (20 tests) |
| `_local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/README.md` | Ce document |

---

## Usage

### Prérequis

L'API Obsidia doit être lancée sur `http://127.0.0.1:8000`.

### Lancement

```powershell
# PowerShell (recommended)
.\scripts\run_brody_terminal_chat.ps1

# Direct Python
python scripts/brody_terminal_chat.py

# Custom endpoint
python scripts/brody_terminal_chat.py http://127.0.0.1:8000
```

### Commandes

| Commande | Action |
|---|---|
| `/help` | Affiche les commandes disponibles |
| `/exit`, `/quit` | Quitte et sauvegarde |
| `/debug on` / `off` | Active/désactive le mode debug |
| `/compact on` / `off` | Active/désactive le mode compact |
| `/session <name>` | Change l'identifiant de session |
| `/status` | Affiche l'état du client |
| `/save` | Sauvegarde le transcript |
| `/last` | Réaffiche la dernière réponse |
| `/raw` | Affiche le JSON brut reçu |

---

## Invariants Boundary

À chaque réponse, le client affiche une ligne de frontière :

```
Boundary: decision_authority=KX108_ONLY  emits_act=False  memory_write=False  graphiti_write=False  neo4j_write=False  kernel_mutation=False
```

Champs extraits :
- `decision_authority`
- `emits_act`
- `emits_verdict`
- `memory_write`
- `graphiti_write`
- `neo4j_write`
- `kernel_mutation`
- `readonly`
- `compact`
- `debug`

Si un champ est absent du payload, la valeur affichée est `UNKNOWN` — jamais forcée à `true` ou `false`.

---

## Transcript local

Chaque session est sauvegardée dans :

```
_local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/sessions/
├── <session_id>.jsonl   # Un tour par ligne
└── <session_id>.md      # Transcript markdown complet
```

Chaque tour contient :
- `timestamp` ISO
- `session_id`
- `user_message`
- `final_answer`
- `decision_authority`, `emits_act`, `memory_write`, `graphiti_write`, `neo4j_write`, `kernel_mutation`
- `compact`, `debug`

**Attention**: Ceci est une sauvegarde locale. Aucune écriture Neo4j/Graphiti. Aucun appel à un endpoint de write.

---

## No Write / No X108 Mutation

Le client terminal :
- N'active jamais `memory_write`
- N'active jamais `graphiti_write`
- N'active jamais `neo4j_write`
- N'appelle que `/api/brody/chat` en readonly
- Ne modifie pas X108
- Ne modifie pas le moteur Brody

---

## Tests

```bash
python -m pytest tests/api/test_brody_terminal_chat_client.py -q --tb=short
```

20 tests :
- Payload builder (compact, debug, session)
- Answer extractor (final_answer > response_md > response > fallback)
- Boundary extractor (flags, UNKNOWN for missing fields)
- Command handlers (debug, compact, session, exit, help)
- Transcript writers (JSONL, MD)
- No write / no mutation (pas de memory_write, graphiti_write, neo4j_write dans les payloads)
- Safe print (UTF-8 accents)
- HTTP call (mock success, HTTP 500, connection refused, invalid JSON)
