# SIGMA_GUIDANCE_V0_APPLY_PROTOCOL

## 1. Purpose

Standardiser l'application et l'interprétation de Sigma Guidance V0.
Sigma retrouve, guide et explique. Sigma ne tranche pas : X108 tranche.

## 2. Scope

S'applique à toute production ou consommation d'un SigmaGuidanceReport :
introspection Sigma (`sigma/sigma_guidance.py`), guidance terminale
(`scripts/obsidia_sigma_guidance.py`), et tout consommateur aval.
Hors scope : Sigma Core (contracts/guard/aggregation), Kernel/X108, domaines.

## 3. Authority boundary

Sigma Guidance est readonly et non souveraine. `decision_authority = KX108_ONLY`.
Aucune sortie de guidance ne constitue une admissibilité, une autorisation
ou un blocage. Toute confusion entre guidance et décision est un défaut
de doctrine à corriger immédiatement.

## 4. Inputs

Lectures autorisées uniquement : rapports et manifests existants (ProofKit,
manifest Lean, seal en lecture seule), résultats de stress historiques,
routes HTTP readonly de monitoring, proposals/receipts Obsidure en lecture.
Interdits en entrée : écriture mémoire, mutation d'état, exécution de
verifiers par la guidance elle-même.

## 5. Allowed outputs

Verbes de recommandation autorisés :
CONTINUE, SLOW_DOWN, RELAUNCH_LAYER, REQUEST_CONTEXT, REQUEST_TRACE,
REQUEST_REPLAY, REQUEST_TEST, REQUEST_PROOF, CHECK_INVARIANT,
STOP_UNKNOWN, HOLD_RECOMMENDED.

## 6. Forbidden outputs

Sigma n'émet jamais : ACT, ALLOW, BLOCK, HOLD (souverain), WRITE_MEMORY,
MUTATE_KERNEL, AUTO_APPLY. Toute API qui exposerait ces mots comme sortie
Sigma est non conforme et doit être rejetée en revue.

## 7. Required checks

Avant d'accepter un rapport de guidance : vérifier que la source est
readonly ; vérifier que `guidance_authority = NONE` (ou équivalent) est
présent ; vérifier qu'aucun verbe interdit n'apparaît ; vérifier que les
raisons citent des signaux concrets (fichier, date, route) et non des
affirmations invérifiables.

## 8. SigmaGuidanceReport interpretation

Un rapport se lit comme une recommandation datée : verbe + raisons +
signaux sources. La fraîcheur des signaux prime : un signal frais
contradictoire neutralise un diagnostic ancien. Un rapport sans raison
exploitable se traite comme REQUEST_CONTEXT, pas comme un feu vert.

## 9. x108_required handling

Si un rapport porte `x108_required=true` (ou tout marqueur équivalent
d'escalade), l'opérateur escalade vers X108 et n'improvise aucune décision
locale. La guidance accompagne l'escalade, elle ne la remplace pas.

## 10. STOP_UNKNOWN handling

STOP_UNKNOWN signifie : intention ou état non reconnu. Conduite : arrêt du
flux courant, demande de contexte, revue humaine et/ou passage X108 si une
décision est en jeu. Ne jamais convertir silencieusement STOP_UNKNOWN en
CONTINUE.

## 11. HOLD_RECOMMENDED vs HOLD

HOLD_RECOMMENDED est une recommandation non souveraine émise par la
guidance. HOLD est une décision X108 (`X108Gate.HOLD`). Les deux ne
partagent ni autorité ni canal : un HOLD_RECOMMENDED n'ouvre aucun droit
de bloquer, il invite l'humain ou X108 à statuer.

## 12. Final report format

Tout usage en workflow se conclut par : scope, verbe(s) reçus, signaux
sources datés, action opérateur choisie, mention explicite qu'aucune
décision souveraine n'a été émise par Sigma.
