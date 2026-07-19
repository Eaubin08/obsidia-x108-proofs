# OBSIDURE_APPLY_PROTOCOL

## 1. Purpose

Standardiser le workflow d'application Obsidure : forge de code, preuves,
corrections. Obsidure construit, prouve et corrige. Obsidure ne décide pas.

## 2. Scope

S'applique à toute génération/application de patch via le workflow Obsidure
(proposals, sandbox Lean, checks, apply gated). Hors scope : décisions
d'admissibilité (X108), guidance (Sigma), runtime applicatif.

## 3. Authority boundary

Obsidure est non souverain. Aucun proposal, aucun receipt, aucun théorème
généré ne vaut décision. `decision_authority = KX108_ONLY`. L'apply est
toujours conditionné à un scope humainement approuvé.

## 4. Proposal-first workflow

Toute mutation passe par un proposal identifié (`proposal_id`) déposé dans
`_PATCH_PROPOSALS/<id>/` avec `proposal.json` et receipt. Ordre obligatoire :
proposal → checks (Lean, forbidden tokens, diff) → approbation humaine du
scope exact → apply → vérification → rapport. Jamais d'apply direct sans
proposal préalable.

## 5. Allowed files

Uniquement les fichiers explicitement listés dans le scope approuvé du
proposal. Un fichier absent de la liste est hors scope, même s'il semble
lié.

## 6. Forbidden files

Sauf scope explicite contraire : Kernel/X108, Sigma Core (contracts, guard,
aggregation, protocols), manifests scellés, seals Merkle, RFC3161, surface
Lean officialisée (GeneratedPeripheral), fichiers gelés/freeze, fichiers
dirty préexistants d'un chantier parallèle.

## 7. Lean checks

Tout patch touchant une surface Lean passe par la sandbox Lean avant apply.
Condition de poursuite : LEAN_EXIT=0. Un échec Lean interrompt le workflow ;
aucun commit n'est autorisé tant que le check Lean échoue.

## 8. Forbidden Lean tokens

La surface de preuve officielle n'admet pas : `sorry`, `admit`, `axiom`
non déclaré, `unsafe`. Un check forbidden-token doit passer avant apply et
avant commit. Exception : fichiers intentionnellement cassés et documentés
comme tels, qui ne font jamais partie de la surface officielle.

## 9. Manifest checks

Un apply Obsidure ne régénère ni manifest scellé ni seal. Si un manifest
doit évoluer, c'est un scope dédié, approuvé séparément, avec plan de
vérification. Vérifier après apply qu'aucun manifest/seal n'apparaît au diff.

## 10. Diff/status checks

Avant commit : montrer le diff complet, la liste des fichiers touchés, le
résultat des tests, et `git status`. Tout fichier au diff hors du scope
approuvé = STOP et correction avant toute suite.

## 11. Commit preconditions

Commit autorisé seulement si : scope exact respecté, LEAN_EXIT=0 quand
applicable, forbidden tokens absents, tests pertinents PASS, diff/status
montrés, aucun fichier parallèle ou protégé stagé. Sinon : pas de commit.

## 12. Failure handling

En cas d'échec d'un check : arrêt, rapport d'échec avec cause exacte,
aucune tentative de contournement, proposal marqué non appliqué. Les
échecs répétés remontent en revue humaine, pas en retry automatique.

## 13. Final report format

Rapport final : proposal_id, scope approuvé, fichiers touchés, résultats
Lean/forbidden/diff/tests, statut commit (fait/non fait), et rappel
explicite qu'Obsidure n'a pris aucune décision d'admissibilité.
