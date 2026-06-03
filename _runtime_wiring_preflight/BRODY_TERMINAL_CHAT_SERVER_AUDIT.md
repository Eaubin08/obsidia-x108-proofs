# BRODY_TERMINAL_CHAT_SERVER_AUDIT
# Date: 2026-06-03
# Branch: p8-runtime-dryrun-wiring | HEAD: 84cc0d0

---

## Résumé

Brody n'a **pas de serveur séparé**. Il se décompose en trois composants distincts :
1. **Routes API** — intégrées dans `apps/obsidia_api/` (`/api/brody/*`)
2. **CLI Terminal Chat** — client interactif (`scripts/brody_terminal_chat.py`)
3. **Modules périphérie** — `periphery/brody/` et `periphery/brody_memory_readonly/`

Aucun processus Brody séparé à lancer. P11A n'a aucun impact sur Brody.

**Verdict : BRODY_TERMINAL_CHAT_SERVER_AUDIT_OK**

---

## Fichiers trouvés

| Fichier | Rôle | Catégorie |
|---------|------|-----------|
| `scripts/brody_terminal_chat.py` (970 lignes) | CLI client interactif V1 | **B. BRODY_TERMINAL_CLI** |
| `scripts/run_brody_terminal_chat.ps1` | Lance le CLI client | Script lancement |
| `scripts/run_brody_terminal.ps1` | Terminal PowerShell simple | Script lancement |
| `scripts/run_brody_terminal_enriched.ps1` | Terminal enrichi multi-routes | Script lancement |
| `scripts/run_brody_api_local.ps1` | Lance l'API (`apps.obsidia_api.main:app`) | Pointe vers l'API principale |
| `apps/obsidia_api/routes/brody.py` | Routes FastAPI `/api/brody/*` | **C. BRODY_ROUTE_IN_API** |
| `apps/obsidia_api/routes/brody_monitoring.py` | Routes monitoring Brody | **C. BRODY_ROUTE_IN_API** |
| `apps/obsidia_api/brody_*.py` (44 fichiers) | Modules logique Brody | **C. BRODY_ROUTE_IN_API** |
| `periphery/brody/` | Modules readonly (runtime_loader) | **C. BRODY_ROUTE_IN_API** |
| `periphery/brody_memory_readonly/` | Readonly memory bridge | **C. BRODY_ROUTE_IN_API** |
| `scripts/f11a_live_brody_chat_smoke.py` | Smoke test live chat | Script test |
| `scripts/smoke_brody_routes.ps1` | Smoke routes | Script test |

---

## Cartographie

| BRODY_COMPONENT | Type | Fichier | Commande | Port | Statut |
|----------------|------|---------|---------|------|--------|
| Brody API routes | BRODY_ROUTE_IN_API | `apps/obsidia_api/routes/brody.py` | Même que OBSIDIA_API | 8000/8012 | CONFIRMED — testé |
| Brody Terminal Chat | BRODY_TERMINAL_CLI | `scripts/brody_terminal_chat.py` | `python scripts/brody_terminal_chat.py [endpoint]` | N/A (client) | CONFIRMED — testé |
| Brody PowerShell terminal | BRODY_TERMINAL_CLI | `scripts/run_brody_terminal.ps1` | PowerShell interactif | N/A | DETECTED |
| Brody Server Séparé | — | — | — | — | NOT_FOUND |

---

## Commandes détectées

```bash
# CLI terminal chat (client — appelle /api/brody/chat sur 8000 ou 8012)
python scripts/brody_terminal_chat.py
python scripts/brody_terminal_chat.py http://127.0.0.1:8000
python scripts/brody_terminal_chat.py http://127.0.0.1:8012

# Équivalent PowerShell
.\scripts\run_brody_terminal_chat.ps1           # → port 8012 (défaut script)
.\scripts\run_brody_terminal_chat.ps1 "http://127.0.0.1:8000"

# Brody n'a PAS son propre uvicorn / FastAPI / serveur
```

---

## Tests réalisés

### Test 1 — Import module

```
python -c "import scripts.brody_terminal_chat as btc"
→ Import OK
```

### Test 2 — Fonctions utilitaires (sans boucle interactive)

| Fonction | Résultat |
|---------|---------|
| `build_payload('test', session_id='audit')` | OK — dict correct |
| `extract_answer({'final_answer': '...'})` | OK — extrait la réponse |
| `extract_boundary({'decision_authority': 'KX108_ONLY', 'emits_act': False})` | OK — boundary correct |
| `detect_memory_signal('garde cette info')` | OK — True |
| `detect_memory_signal('bonjour')` | OK — False |
| `PersonalMemorySidecar()` | OK — instanciation sans écriture |

### Test 3 — Appel live via `call_brody_api` (API 8000 HEAD 84cc0d0)

```
call_brody_api('http://127.0.0.1:8000', payload) → HTTP 200
  answer: 'Demande ouverte recue. Je peux la structurer selon trois axes...'
  decision_authority : KX108_ONLY ✓
  emits_act          : False ✓
  memory_write       : False ✓
  kernel_mutation    : False ✓
BRODY_CHAT_LIVE_TEST=PASS
```

### Test 4 — Stdin non-interactif `/status` + `/exit`

```
echo "/status\n/exit" | python scripts/brody_terminal_chat.py
→ Brody Terminal Chat Client V1
→ Endpoint: http://127.0.0.1:8000
→ /status affiche état complet
→ /exit → 'Au revoir. Session sauvegardée.'
→ Exit code 0
BRODY_TERMINAL_STDIN_TEST=PASS
```

---

## Résultat

Tout PASS. Aucun crash. Aucune régression.

---

## Phase 4 — Réponses explicites

| Question | Réponse |
|---------|---------|
| Brody a-t-il un serveur séparé ? | **NON** — pas de serveur uvicorn / FastAPI séparé |
| Brody a-t-il un terminal chat séparé ? | **OUI — CLI client seulement** (`scripts/brody_terminal_chat.py`). Pas de daemon/serveur. |
| Brody est-il intégré dans API 8000/8012 ? | **OUI** — `/api/brody/chat`, `/api/brody/monitoring`, etc. dans `apps/obsidia_api/routes/brody.py` |
| P11A a-t-il cassé Brody ? | **NON** — `brody_terminal_chat.py` ne dépend d'aucun fichier P11A. Tests PASS. |
| Brody doit-il être inclus dans la matrice avant commit ? | **OUI** — comme BRODY_ROUTE_IN_API (déjà testé via /api/brody/chat sur 8000/8012). Pas de serveur supplémentaire à gérer. |
| Quelle commande exacte lance Brody ? | `python scripts/brody_terminal_chat.py http://127.0.0.1:8000` (ou 8012). Nécessite que l'API soit déjà lancée. |

---

## Impact P11A — Conclusion

Les fichiers modifiés par P11A sont :
- `apps/obsidia-workbench/src/App.tsx` — React (Vite only)
- `apps/obsidia-workbench/src/components/LeftSidebar.tsx` — React (Vite only)
- `apps/obsidia-workbench/vite.config.ts` — Vite proxy config
- `apps/obsidia-workbench/src/views/RuntimeWiringPreviewView.tsx` — React view (corrigée)
- `apps/obsidia_api/main.py` — +1 import route, +1 include_router (committés en 84cc0d0)
- `apps/obsidia_api/routes/runtime_wiring_preview.py` — nouvelle route (committée en 84cc0d0)

**Aucun de ces fichiers n'est importé ou utilisé par `brody_terminal_chat.py`.**
**Impact P11A sur Brody : ZERO.**

---

## Logs

```
P11A_BRODY_TERMINAL_LOG : aucun processus lancé ni arrêté
Aucun port ouvert/fermé pour ce test.
Tests réalisés en mode import Python uniquement + subprocess stdin.
```
