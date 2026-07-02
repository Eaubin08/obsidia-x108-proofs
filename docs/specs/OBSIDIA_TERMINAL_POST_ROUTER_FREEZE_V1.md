# OBSIDIA_TERMINAL_POST_ROUTER_FREEZE_V1

## 0. Identité du freeze

- Nom : `OBSIDIA_TERMINAL_POST_ROUTER_FREEZE_V1`
- Branche : `feat/path-brody-r02-thermo-mcp-closure`
- Date : 2026-07-02
- Type : **freeze documentaire**. Pas un seal, pas un manifest, pas une
  ancre crypto, pas une preuve Lean, pas une autorité souveraine. Il fige
  un état de référence après l'ajout du routeur universel d'IN. Le hash du
  commit portant ce freeze n'est pas inscrit ici : il vivra dans Git après
  commit.

## 1. Position dans la ligne terminale

```
Terminal Stack V1  →  Plan Panel V1  →  Answer Router V1  →  Post-Router Freeze V1
```

Le freeze `OBSIDIA_TERMINAL_STACK_FREEZE_V1` (74cfd0d) reste vrai : il fige
l'état d'avant Plan Panel. Le présent document fige l'état d'après Answer
Router.

## 2. Commits fermés

```
74cfd0d docs(terminal): freeze terminal stack line v1
519f87c feat(terminal): add active plan panel v1 with capabilities
11d125a feat(terminal): add universal answer router v1
```

## 3. Comportement one-shot après Answer Router

`obsidia "<IN libre>"` → panneau lisible `OBSIDIA_RESPONSE` (réponse, mode,
couche, organes, outils, corpus, limites, prochaine action humaine, sortie
terminale). Exemples : `obsidia "resume le freeze terminal"`,
`obsidia "c'est quoi thermo"`, `obsidia "commit le kernel"`,
`obsidia "prepare obsidure"`, `obsidia "blabla"`.

## 4. Comportement shell après Answer Router

`obsidia>` : tout IN libre → `OBSIDIA_RESPONSE`. Les commandes internes
restent prioritaires et interceptées avant le routeur : help, clear, exit,
doctor, plan, route, tools, blockers, gates, scope, next, answer, raw, json.

## 5. Compatibilité raw/json

`obsidia raw "<IN>"` et `obsidia json "<IN>"` (one-shot et shell)
conservent l'ancien JSON `handle()` à l'identique.

## 6. Doctor inchangé

`obsidia doctor` reste le doctor existant : JSON readonly, sondes HTTP GET
sur les 5 endpoints du registry.

## 7. Plan Panel intact

`obsidia plan/route/tools "<IN>"` restent intacts et affichent : roadmap
12 étapes, couche, capacités/organes, outils techniques, corpus, gates
(jamais lancés), blockers, next action.

## 8. Policy deny intacte

`obsidia "commit le kernel"` donne désormais une réponse lisible
`OBSIDIA_RESPONSE` (mode ANSWER_POLICY_DENY), mais la sortie terminale
reste `POLICY_DENY` et la guidance `HOLD_RECOMMENDED`.
`obsidia raw "commit le kernel"` garde l'ancien JSON
`POLICY_DENY/HOLD_RECOMMENDED`. La policy n'a pas bougé d'une ligne.

## 9. Autorité et non-souveraineté

Le terminal répond dans ses droits. Le Plan explique la route. Les organes
contribuent selon leur rôle. Les outils soutiennent la réponse. L'humain
applique. X108 décide.

Interdits permanents : aucun apply/commit/push/deploy automatique, aucun
lancement Obsidure/Lean/stack automatique, aucune écriture mémoire, aucune
mutation Kernel/X108, aucune mutation Sigma Core.

## 10. Outputs autorisés

Sorties terminales (les seules) : `EXECUTE` (GET readonly), `COMMANDS`,
`GUIDE`, `POLICY_DENY`, `STOP_UNKNOWN` — verrouillées par
`assert_output_allowed()`. Les modes internes du routeur (ANSWER_LOCAL,
ANSWER_LIVE_READONLY, ANSWER_COMMANDS_ONLY, ANSWER_PLAN, ANSWER_UNKNOWN,
ANSWER_POLICY_DENY) sont des étiquettes de traitement, **pas des verdicts
souverains** — chacun se projette sur une des 5 sorties ci-dessus.

## 11. Organes / capacités visibles

Terminal, OS Langage Uni, Brody, Obsidure, Sigma, Thermo, Kernel/X108,
Domains, Memory/Graphiti, Lean/Proofs, Audit/Merkle, Registry, Gates,
Receipts — statuts `[MOBILISE]/[MOBILISABLE]/[INTERDIT]/[NON_NECESSAIRE]`,
rôles documentés dans la spec Plan Panel.

## 12. Outils techniques visibles

registry, policy_check, Plan Panel, doctor readonly, sigma_guidance_report,
collect_file_signals, live HTTP GET readonly, PROOFKIT_REPORT.json,
manifest Lean, merkle_seal.json (lecture), registre proposals Obsidure
(readonly), stress_tests (diagnostic only), docs/protocols/, docs/specs/,
scripts/gates/, tests/gates/, receipts locaux, _PATCH_PROPOSALS (readonly).

## 13. Corpus local et règle anti-hallucination

Sujet dans `LOCAL_CORPUS` (sigma, obsidure, freeze terminal, plan panel,
gates, doctrine, brody) → réponse depuis le corpus local readonly, sources
citées. Sujet hors index → ANSWER_UNKNOWN / STOP_UNKNOWN avec explication
de ce qui manque — **jamais d'improvisation**. Exemple validé :
`c'est quoi thermo` → corpus Thermo non indexé → réponse honnête demandant
la source à indexer.

## 14. Exemples validés

```
obsidia "resume le freeze terminal" → ANSWER_LOCAL / GUIDE (sections + commits lus du fichier réel)
obsidia "c'est quoi thermo"         → ANSWER_UNKNOWN / STOP_UNKNOWN
obsidia raw "commit le kernel"      → ancien JSON POLICY_DENY/HOLD_RECOMMENDED
obsidia json "sigma coherence"      → ancien JSON EXECUTE
obsidia "commit le kernel"          → OBSIDIA_RESPONSE / ANSWER_POLICY_DENY / POLICY_DENY
obsidia "prepare obsidure"          → OBSIDIA_RESPONSE / ANSWER_COMMANDS_ONLY / COMMANDS
obsidia "blabla"                    → OBSIDIA_RESPONSE / ANSWER_UNKNOWN / STOP_UNKNOWN
obsidia plan "sigma coherence"      → OBSIDIA_ACTIVE_PLAN intact
obsidia tools "sigma coherence"     → tools/capacités intacts
obsidia doctor                      → doctor JSON intact
```

## 15. Tests et gates

```
python -m py_compile scripts\obsidia_cli.py   → OK
python -m pytest tests/gates/ -q              → 29 passed
```

Le gate `obsidia_sigma_non_sovereignty_check` continue de verrouiller
l'invariant non souverain dont dépend toute la ligne terminale.

## 16. Limites V1

Pas de subprocess Git (blockers affiche les commandes, ne les lance pas) ;
pas de vraie lecture Git automatique ; pas d'écriture `.local_obsidia/plan/` ;
pas d'expansion automatique du corpus ; pas d'édition registry par le
routeur ; pas d'exécution Obsidure ; pas d'exécution Lean ; aucune mutation.
La sortie prévue du Plan reste une prédiction — l'exécution réelle passe
par l'IN direct.

## 17. Backlog V2

Étendre LOCAL_CORPUS ; indexer Thermo proprement (source à fournir) ;
améliorer les alias naturels ; nettoyer les doublons d'affichage (ex.
"mutation Sigma Core" apparaissant dans deux blocs) ; vue compacte/verbose ;
export markdown de réponse optionnel ; UI terminal plus lisible ;
éventuellement connecter Brody en explication readonly des réponses.
