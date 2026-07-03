# OBSIDIA_TERMINAL_UX_COMPACT_V2 — spécification

## 0. Identité V2

Scope : `OBSIDIA_TERMINAL_UX_COMPACT_V2`. Première évolution V2 après le
Post-Router Freeze V1 (9397e6e). Amélioration UX pure : **aucun nouveau
droit**, aucun subprocess, aucune écriture nouvelle, aucune modification
de policy/registry/routes/vocabulaire. Les freezes V1 restent vrais.

## 1. Motivation

OBSIDIA_RESPONSE en vue complète fait ~40 lignes par IN — précieux pour
l'audit, lourd à l'usage quotidien. Le compact rend le terminal utilisable
en continu sans perdre les blocs de sécurité.

## 2. Différence compact / verbose

Compact (défaut) : INPUT, REPONSE, MODE, COUCHE, SORTIE, LIMITES, NEXT.
Verbose (`-v` / `--verbose`) : format complet du Router V1 — INPUT,
REPONSE, MODE DE REPONSE, COUCHE, CAPACITES/ORGANES MOBILISES, OUTILS
TECHNIQUES MOBILISES, CORPUS UTILISE, LIMITES, PROCHAINE ACTION HUMAINE,
SORTIE TERMINAL. Mêmes données calculées dans les deux cas ; seule la
présentation change. Le receipt contient toujours tout.

## 3. Commandes concernées

```
obsidia "<IN libre>"              → compact
obsidia answer "<IN libre>"       → compact
obsidia> <IN libre>               → compact
obsidia -v "<IN>"                 → verbose
obsidia --verbose "<IN>"          → verbose
obsidia answer -v "<IN>"          → verbose
obsidia> -v <IN>                  → verbose
obsidia> verbose <IN>             → verbose
obsidia> answer -v <IN>           → verbose
```

## 4. Commandes non concernées

raw, json (ancien JSON intact), doctor (JSON intact), plan/route/tools
(détaillés par nature, non compactés), blockers, gates, scope, next,
help, clear, exit — tous inchangés.

## 5. Blocs obligatoires du compact

INPUT, REPONSE, MODE, COUCHE, SORTIE, LIMITES, NEXT — jamais moins.

## 6. Sécurité : LIMITES et NEXT restent visibles

LIMITES (dont la règle de droits « répondre complètement exigerait X
[INTERDIT]... ») et NEXT (prochaine action humaine) sont les deux blocs de
sécurité : ils sont présents dans le compact comme dans le verbose.

## 7. Dédoublonnage des listes

`dedupe_preserve_order(items)` : dédoublonnage stable appliqué aux listes
d'exclusions (outils_exclus, organes_interdits) — supprime notamment le
doublon « mutation Sigma Core » (couche sigma + interdits permanents).
Purement cosmétique : aucune policy, aucun droit, aucune route modifiés.

## 8. Non-objectifs

Pas de couleurs/UI riche, pas d'export de fichier, pas de POST Brody,
pas d'extension de corpus, pas de modification des specs V1 gelées —
chacun de ces sujets a ou aura son propre scope.

## 9. Backlog suivant

`LOCAL_CORPUS_EXTENSION_V2` (sujets + sources fournis par l'humain, dont
Thermo) ; alias naturels supplémentaires (liste à valider) ; ergonomie
cockpit au-delà du compact (à définir après usage réel) ; Brody readonly
et export markdown : designs dédiés avec dérogation explicite obligatoire.
