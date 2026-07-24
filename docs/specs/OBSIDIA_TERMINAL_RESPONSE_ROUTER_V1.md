# OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1 — spécification

## Identité

Couche : `OBSIDIA_ANSWER_ROUTER` (bannière de sortie : `OBSIDIA_RESPONSE`).
**Moteur universel de tout IN libre** — pas une commande optionnelle.
Nouvelle ligne après le Plan Panel V1 (commit 519f87c) ; réutilise
`build_active_plan()`, `PLAN_ORGANES`, `PLAN_TOOLING`, la policy et le
vocabulaire existants sans les modifier.

## Doctrine

Le terminal répond dans ses droits. Le Plan explique la route. Les organes
contribuent selon leur rôle. Les outils soutiennent la réponse. L'humain
applique. X108 décide. Aucun verdict ALLOW/BLOCK/HOLD/ACT ; toute sortie
passe par `assert_output_allowed()`. Zéro subprocess, GET readonly
uniquement, aucune écriture hors receipts, stateless.

## Pipeline universel

```
IN brut → interception commandes internes → normalisation → policy check
→ build_active_plan() → couche/organes/outils/corpus → choix du mode
→ réponse utile | COMMANDS | POLICY_DENY | STOP_UNKNOWN → receipt
```

## Comportement V1 (décision verrouillée)

- `obsidia "<IN libre>"` (one-shot) → OBSIDIA_RESPONSE
- `obsidia> <IN libre>` (shell) → OBSIDIA_RESPONSE
- `obsidia answer "<IN>"` → test explicite du même moteur
- `obsidia raw "<IN>"` / `obsidia json "<IN>"` → ancien JSON `handle()`
- `obsidia doctor` → doctor existant inchangé (JSON EXECUTE)
- plan/route/tools/blockers/gates/scope/next/help/clear/exit → inchangés

## Modes internes → sorties terminales

| Mode | Sortie | Source |
|---|---|---|
| ANSWER_LOCAL | GUIDE | LOCAL_CORPUS (réponses sourcées uniquement) |
| ANSWER_LIVE_READONLY | EXECUTE | doctor GET readonly ; ou guidance_reasons réelles (sigma "pourquoi") |
| ANSWER_COMMANDS_ONLY | COMMANDS | commandes registry, jamais lancées |
| ANSWER_PLAN | GUIDE | build_active_plan (plan prudent / blockers) |
| ANSWER_UNKNOWN | STOP_UNKNOWN | clarification, liste des couches |
| ANSWER_POLICY_DENY | POLICY_DENY | policy existante intacte |

## Règles ordonnées

1. Policy d'abord (mots interdits → ANSWER_POLICY_DENY, rien ne passe avant).
2. Mots blockers/méta ("ça bloque où", "quels outils", "roadmap") → ANSWER_PLAN.
3. "pourquoi" + couche sigma → ANSWER_LIVE_READONLY (explication des
   guidance_reasons réelles, jamais inventées).
4. Mots d'état ("status", "tourne", "health") → ANSWER_LIVE_READONLY (doctor).
5. Question de connaissance ("c'est quoi", "explique", "résume") + sujet
   dans LOCAL_CORPUS → ANSWER_LOCAL avec sources citées ; sujet hors index
   → ANSWER_UNKNOWN.
6. Mots d'action ("lance", "prépare", "démarre") → ANSWER_COMMANDS_ONLY.
7. Couche unknown → ANSWER_UNKNOWN. Sinon → ANSWER_PLAN prudent.

Règle fondamentale : une entrée inconnue ne meurt jamais silencieusement.
Règle d'ambiguïté : une entrée ambiguë route prudemment (ANSWER_PLAN /
ANSWER_UNKNOWN), jamais d'action déclenchée.
Règle de droits : si la réponse complète exigerait un outil interdit, le
bloc LIMITES affiche « répondre complètement exigerait <X> [INTERDIT] —
voici ce que je peux faire à la place : <alternative humaine safe> ».

## LOCAL_CORPUS (anti-hallucination)

Sujets indexés V1 : sigma, obsidure, freeze terminal (lu depuis le fichier
freeze réel), plan panel, gates, doctrine, brody. **Thermo volontairement
absent** : capacité déclarée sans doc détaillée → ANSWER_UNKNOWN honnête
demandant la source à indexer. Règle : hors index = pas d'improvisation.

## Format de sortie

Blocs : INPUT, RÉPONSE (en premier — la traçabilité suit), MODE DE RÉPONSE,
COUCHE, CAPACITÉS/ORGANES MOBILISÉS, OUTILS TECHNIQUES MOBILISÉS, CORPUS
UTILISÉ, LIMITES (obligatoire, jamais vide), PROCHAINE ACTION HUMAINE,
SORTIE TERMINAL.

## Alias naturels V1

« ça bloque où ? » → vue blockers (ANSWER_PLAN) ; « quels outils tu vas
utiliser » → ANSWER_PLAN ; « pourquoi sigma me dit continue » → raisons
réelles ; « prépare obsidure » → COMMANDS_ONLY.

## Limites V1 / Backlog V2

Corpus local restreint aux sujets indexés (extension = données, pas de
pouvoir nouveau). Détection d'intention par mots-clés simples (pas de
modèle). État git non lu (zéro subprocess). V2 : enrichir LOCAL_CORPUS,
migrer l'index dans le registry, JSON en mode debug uniquement.
