# KERNEL_BOUNDARY_CHECK_PROTOCOL

## 1. Purpose

Définir le check de frontière protégeant Kernel/X108 et les surfaces
sensibles contre toute modification ou tout staging accidentel. Le check
lit, compare et signale ; il ne modifie rien et ne décide rien à la place
de X108.

## 2. Protected files and layers

Protégés par défaut : Kernel/X108 (dont serveurs kernel scellés, ex.
`server.kernel.sealed.cjs`), Sigma Core (`sigma/contracts.py`,
`sigma/guard.py`, `sigma/protocols.py`, `sigma/aggregation.py`),
`proofs/LEAN_PROOF_SURFACE_MANIFEST.json`, surface Lean officialisée
(`proofs/lean/Obsidia/GeneratedPeripheral/`), `merkle_seal.json`,
`MANIFEST_SHA256.json`, ancres RFC3161, dossiers freeze, `runtime/`,
`apps/` hors scope explicite.

## 3. Read-only boundary check

Le check de frontière s'appuie exclusivement sur la lecture de
`git diff --name-only` et `git diff --cached --name-only`. Il ne modifie
aucun fichier, n'écrit rien, ne stage rien, ne commit rien.

## 4. Staged scope check

Tout fichier protégé présent dans le staging sans autorisation explicite
et écrite du scope = STOP immédiat. Le staging doit correspondre
exactement à la liste de fichiers du scope approuvé, ni plus ni moins.

## 5. Runtime/app exclusion

`runtime/` et `apps/` sont exclus des scopes de build par défaut. Leur
présence au diff d'un scope docs/gates/terminal est un signal d'erreur
de périmètre, à corriger avant toute suite.

## 6. Sigma Core protection

Sigma Core est protégé par défaut. Les scopes guidance (introspection,
terminal) lisent Sigma mais ne le modifient pas. Toute modification de
Sigma Core exige un scope dédié explicitement approuvé.

## 7. Lean manifest protection

Le manifest Lean et la surface de preuve officialisée sont protégés sauf
scope explicite. Aucun scope ordinaire ne les régénère, ne les édite, ne
les renomme.

## 8. Merkle/seal protection

Seals Merkle, manifests SHA256 et ancres temporelles ne sont jamais
régénérés par un check ni par un scope de build. Le check les lit pour
constater, jamais pour reconstruire.

## 9. Failure categories

PROTECTED_STAGED (fichier protégé stagé sans autorisation),
PROTECTED_DIRTY (fichier protégé modifié au working tree),
OUT_OF_SCOPE_STAGED (fichier hors liste approuvée stagé),
PARALLEL_DIRTY_RISK (fichier dirty préexistant risquant d'être embarqué),
UNKNOWN_PATH (chemin non classable — traité comme protégé par prudence).

## 10. Stop conditions

STOP si : catégorie PROTECTED_STAGED ou OUT_OF_SCOPE_STAGED détectée ;
divergence entre scope déclaré et staging ; fichier dirty préexistant sur
le point d'être stagé ; incapacité à lire l'état git de façon fiable.
Un fichier dirty préexistant n'est jamais "réparé" par le check : il est
signalé et laissé intact.

## 11. Final report format

Rapport : liste des chemins protégés vérifiés, état diff/staged constaté,
catégories d'échec le cas échéant, verdict KERNEL_BOUNDARY_PASS ou
KERNEL_BOUNDARY_FAIL, et rappel que ce verdict est un garde-fou de scope,
pas une décision d'admissibilité X108.
