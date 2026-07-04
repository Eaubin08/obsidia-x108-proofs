# OBSIDIA_TERMINAL_RESPONSE_ROUTER_NL_INTENT_V2 — spécification

## Identité

Scope : `OBSIDIA_ANSWER_ROUTER_NL_INTENT_V2`. **Extension** de la couche
existante `OBSIDIA_ANSWER_ROUTER` (spec V1 gelée). Pas une nouvelle couche :
le rôle « OS Langage Uni » (normaliser l'IN, structurer l'intention) est
déjà tenu par `normalize()` + `select_answer_mode()` +
`classify_local_read_intent()`. Cette extension mappe les **paraphrases
humaines** vers les intents déjà bornés — données + branches, aucun droit,
aucun subprocess, aucune nouvelle sortie.

## Ce qui change

1. `_LOCAL_VERBS` enrichi : synonymes de lecture (`montre`, `parcours`,
   `jette un oeil`, `regarde` → READ), de recherche (`trouve`, `localise`),
   de comparaison (`difference`, `ecart`), de résumé (`synthetise`,
   `essentiel`), d'explication (`detaille`, `clarifie`).
2. `_SEARCH_NL_MARKERS` : paraphrases sans verbe (`parle de`, `ou parle`,
   `passage sur`, `a quel endroit`) → SEARCH_LOCAL_TEXT.
3. Extraction de requête multi-marqueurs (parle de / trouve / localise /
   cherche / passage sur).
4. Branche IS_DIR de la lecture : `regarde <dossier>` liste réellement
   (au lieu d'un renvoi).
5. `_NEXT_WORDS` : `quoi faire`, `la suite`, `prochaine etape`,
   `prepare la suite`... → `select_answer_mode` renvoie ANSWER_PLAN.

## Intents activables maintenant (V2A)

- regarde/montre/parcours/affiche `<fichier>` → READ_LOCAL_WINDOW (EXECUTE).
- montre les lignes X à Y de `<fichier>` → READ_LOCAL_RANGE (EXECUTE).
- où (ça) parle de X / trouve X / localise X dans `<fichier>` →
  SEARCH_LOCAL_TEXT (EXECUTE). contexte autour de X → SEARCH_LOCAL_CONTEXT.
- regarde `<dossier>` → LIST_LOCAL_DIR (EXECUTE).

## Intents reconnus mais différés (GUIDE V2B_REQUIRED)

résume / synthétise / essentiel / explique / détaille / clarifie / compare
/ différence / écart sur fichier → mode ANSWER_PLAN, sortie GUIDE, message
`V2B_REQUIRED` (capacité reconnue, non appliquée). Le résumé, l'explication
et la comparaison ne sont **pas** implémentés ici — c'est le chantier V2B.

## Intents plan

quoi faire maintenant / la suite / prochaine étape / prepare la suite (sans
muter) → ANSWER_PLAN (GUIDE). Aucune action déclenchée.

## Priorité de routage (inchangée)

1. policy deny (mutation/action/secrets), 2. lecture locale V2A si chemin
détecté, 3. corpus si sujet indexé, 4. plan (suite/travail/méta),
5. unknown si ambigu. Le mapping NL s'insère à l'intérieur de ces règles ;
il ne les réordonne pas et ne crée aucun raccourci vers une action.

## Garanties

Sorties inchangées (EXECUTE/COMMANDS/GUIDE/POLICY_DENY/STOP_UNKNOWN).
`normalize`, `policy_check`, registry, freezes intacts. Lecture toujours
streaming bornée (V2A) — jamais de fichier complet. Aucun appel Brody.
Secrets et mutations refusés avant toute lecture, au mot près comme avant.

## Limites

résumé/explication/comparaison restent différés (V2B). Détection lexicale
déterministe (pas de modèle). Les verbes génériques (`essentiel`) ne
déclenchent une capacité que si un fichier est présent ; sinon retour au
flux corpus/plan.
