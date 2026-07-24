# OBSIDIA_TERMINAL_PLAN_PANEL_V1 — spécification

## Identité

Couche : `OBSIDIA_ACTIVE_PLAN` — panneau de pilotage lisible du terminal
Obsidia. **Nouvelle ligne après `OBSIDIA_TERMINAL_STACK_FREEZE_V1`** : le
freeze précédent reste vrai (il fige l'état terminal avant Plan Panel) ;
cette couche est une évolution contrôlée, pas une modification du freeze.

Rôle : pour n'importe quel IN, montrer *comment* le terminal l'a compris,
*où* il le route, *avec quels outils*, *quel corpus*, *ce qu'il refuse de
toucher*, *quelle réponse il prévoit* et *quelle est l'étape humaine
suivante*.

## Doctrine non souveraine

Le Plan propose. Le terminal affiche. L'humain applique. X108 décide.
Le Plan ne décide jamais, ne lance rien (ni Obsidure, ni Lean, ni Git,
ni stack), ne modifie rien, n'écrit pas en mémoire. Aucun verdict
ALLOW/BLOCK/HOLD/ACT — les états du panneau sont les PLAN_STATUS
ci-dessous. `HOLD_RECOMMENDED` reste une guidance terminale non
souveraine, jamais un HOLD X108.

Mode V1 : **stateless**. Aucun fichier `.local_obsidia/plan/`. Zéro
subprocess (`blockers` affiche les commandes git à lancer, ne les lance
pas). `handle()` est intact : le panneau enveloppe le pipeline, il ne le
remplace pas. Le registry est lu, jamais modifié.

## Roadmap de traitement (12 étapes, obligatoire dans `plan`)

1. Réception de l'IN brut — 2. Normalisation — 3. Détection des triggers —
4. Couche détectée + confiance — 5. Policy check — 6. Choix du mode de
sortie — 7. Outils utilisés — 8. Corpus utilisé ou mobilisable —
9. Outils/corpus exclus — 10. Gates nécessaires (jamais lancés) —
11. Réponse terminal prévue — 12. Prochaine action humaine.

La roadmap est générée par le passage réel dans le pipeline (normalisation
calculée, triggers réellement matchés, policy réellement évaluée) — elle ne
peut pas mentir sur son propre traitement. Quand la policy coupe (mot
interdit) ou que la couche est inconnue, la roadmap **montre l'arrêt** :
les étapes suivantes s'affichent "non atteinte — coupée à l'étape N".

## Format de sortie de `obsidia plan "<IN>"`

Blocs, dans l'ordre : INPUT, ROADMAP DE TRAITEMENT, COUCHE DÉTECTÉE,
ROUTAGE, CAPACITÉS / ORGANES MOBILISÉS, CAPACITÉS / ORGANES MOBILISABLES,
CAPACITÉS / ORGANES INTERDITS / NON UTILISÉS, OUTILS TECHNIQUES MOBILISÉS,
OUTILS TECHNIQUES MOBILISABLES, OUTILS TECHNIQUES INTERDITS / NON UTILISÉS,
CORPUS PERTINENT, SCOPE, GATES, BLOCKERS, SORTIE TERMINAL PRÉVUE,
GUIDANCE, PROCHAINE ACTION HUMAINE, PLAN_STATUS.

## Capacités / organes Obsidia (distincts des outils techniques)

Le panneau distingue **quelle partie de l'organisme Obsidia répond**
(capacités/organes) et **quel outil technique soutient la réponse**.

Rôles des capacités affichables :

- **Terminal** : affiche, route, guide — ne décide pas.
- **OS Langage Uni** : normalise l'IN, structure l'intention, prépare le
  passage vers les couches.
- **Brody** : explique, contextualise, synthétise — ne décide pas.
- **Obsidure** : construit des proposals ; commands-only depuis le
  terminal, jamais exécuté automatiquement.
- **Sigma** : guide sur cohérence, contradiction, fraîcheur — ne décide pas.
- **Thermo** : analyse friction, coût, inertie, stabilité — si disponible.
- **Kernel/X108** : autorité d'admissibilité ; consultable en status
  readonly, jamais muté par le terminal.
- **Domains** : bridge-only (Bank, Trading, GPS, Ecom...), KX108_ONLY.
- **Memory/Graphiti** : readonly / frozen status, aucune écriture mémoire.
- **Lean/Proofs** : preuve/vérification commands-only, jamais lancée
  automatiquement.
- **Audit/Merkle** : lecture de traces, manifests, seals — sans
  régénération automatique.
- **Registry** : source locale de routage.
- **Gates** : vérifications listées, jamais lancées.
- **Receipts** : traces locales non souveraines.

Statuts d'organes : `[MOBILISE]`, `[MOBILISABLE]`, `[INTERDIT]`,
`[NON_NECESSAIRE]`. Interdits permanents (toutes couches) : mutation
Kernel/X108, memory write, exécution automatique Obsidure/Lean,
apply/commit/push automatique.

## Statuts d'outils techniques

`OUTIL_UTILISÉ`, `OUTIL_MOBILISABLE`, `OUTIL_READONLY`,
`OUTIL_COMMANDS_ONLY`, `OUTIL_NON_NÉCESSAIRE`, `OUTIL_INTERDIT`.

Interdits permanents affichés quand pertinent : git commit/push/deploy,
mutation Kernel/X108, mutation Sigma Core, memory write, exécution
Obsidure, exécution Lean, lancement stack, écriture `.local_obsidia/plan/`.

## PLAN_STATUS autorisés

`ROUTED`, `WAITING_FOR_HUMAN`, `BLOCKED_BY_STAGED_FILES`,
`READY_FOR_REVIEW`, `NEEDS_SCOPE_CONFIRMATION`, `NO_ACTION_TAKEN`,
`POLICY_CUT`. Jamais ALLOW/BLOCK/HOLD/ACT.

## Commandes V1

`obsidia plan "<IN>"` — panneau complet (roadmap 12 étapes). Receipt normal.
`obsidia route "<IN>"` — routage + roadmap résumée en une ligne
(`IN → normalize → couche → sortie`). Receipt normal.
`obsidia tools "<IN>"` — étapes 7-9 détaillées (outils/corpus/exclus).
Receipt normal.
`obsidia blockers` — signaux fichiers readonly + commandes git à lancer
toi-même (jamais lancées). Pas de receipt.
`obsidia gates` — liste les gates connus et présents, jamais lancés.
Pas de receipt.
`obsidia scope` / `obsidia next` — en session shell : scope/prochaine
action du dernier IN traité (mémoire de session uniquement) ; en one-shot :
NO_ACTION_TAKEN. Pas de receipt.

Le shell interactif accepte `plan "<IN>"`, `route "<IN>"`, `tools "<IN>"`,
`blockers`, `gates`, `scope`, `next` sans casser help/clear/exit.
Le one-shot classique (`obsidia doctor`, `obsidia "<IN>"`) est inchangé.

## Exemples principaux

`plan "sigma coherence"` → couche sigma, roadmap complète, outils
sigma_guidance_report + collect_file_signals, corpus proofkit/manifest/
merkle(lecture)/proposals/stress[diagnostic], sortie EXECUTE, guidance
CONTINUE si signaux frais, PLAN_STATUS ROUTED.

`plan "commit le kernel"` → couche kernel, policy coupe à l'étape 5
(mot "commit"), sortie POLICY_DENY, guidance HOLD_RECOMMENDED,
PLAN_STATUS POLICY_CUT, prochaine action : workflow gated humain.

`plan "obsidure status"` → couche obsidure, sortie COMMANDS,
run_agent_obsidure.ps1 affiché OUTIL_COMMANDS_ONLY jamais lancé,
corpus _PATCH_PROPOSALS readonly, PLAN_STATUS WAITING_FOR_HUMAN.

`plan "lance les preuves lean"` → couche obsidienne, sortie COMMANDS,
verify_all.py et lake build affichés OUTIL_COMMANDS_ONLY,
PLAN_STATUS WAITING_FOR_HUMAN.

`plan "blabla"` → couche unknown, roadmap coupée à l'étape 4, sortie
STOP_UNKNOWN, guidance REQUEST_CONTEXT, PLAN_STATUS
NEEDS_SCOPE_CONFIRMATION.

## Limites V1

Sortie prévue ≠ sortie exécutée : le plan prédit sans appeler le réseau
(pas de doctor HTTP, pas de sigma live) — l'exécution réelle reste
`obsidia "<IN>"`. L'état git n'est pas lu (zéro subprocess) : `blockers`
délègue à l'humain. La table d'outils vit dans le CLI (pas de migration
registry en V1). `scope`/`next` ne persistent pas entre sessions
(stateless).

## Backlog V2

Persistance optionnelle `.local_obsidia/plan/current_plan.json` +
`plan_history.jsonl` (local, non tracké, non souverain) ; table d'outils
migrée dans le registry ; lecture git readonly si la dérogation zéro
subprocess est un jour levée explicitement ; panneaux SCOPE/CORPUS/
PROPOSAL dédiés (ligne "Claude Code personnel version Obsidia").
