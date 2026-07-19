# Freeze A → main : statut d'intégration — 2026-07-19

## Verdict

`READY_FOR_INTEGRATION_PR`

L'intégration auditée de Freeze A est fermée sur la branche
`integration/freeze-a-to-main-20260717`.

Aucun push, merge direct dans `main`, changement de tag ou force-push n'a
été effectué pendant la préparation locale.

## Identité de l'intégration

| Élément | Valeur |
|---|---|
| Base `origin/main` | `67329b0c3192e1c45449572fd5d3b1cecf394f27` |
| Source canonique Freeze A | `0b144e65e9ad00645b14e5c84aeb10c3465ffeb4` |
| Tag historique immuable | `freeze/a-20260716-build-maximal` |
| Branche d'intégration | `integration/freeze-a-to-main-20260717` |
| Branche d'incubation préservée | `preserve/freeze-a-local-candidates-20260717 @ 92fb803b` |
| Méthode | Intégration auditée en trois commits |
| Autorité de décision | `KX108_ONLY` |

La branche d'incubation n'a pas été fusionnée globalement. Les originaux,
sauvegardes, worktrees et tags historiques restent préservés.

## Commits produits

| Ordre | SHA | Message |
|---:|---|---|
| 1 | `36a5255c7c7b90a24ba09e6654d27c91bada05ba` | `feat(main): integrate audited Freeze A canonical stack` |
| 2 | `3b24043c21599e7c5f3912aed8b3feee2b660ecc` | `fix(connectors): preserve Brody UTF-8 terminal transport` |
| 3 | Ce document | `docs(main): record Freeze A integration boundaries` |

## Périmètre du commit 1

Le premier commit intègre la pile canonique Freeze A auditée, notamment :

- API Obsidia et Brody ;
- couches readonly, CIC et inference economy ;
- agents et shims de compatibilité ;
- OS adapters, bus et routes live readonly ;
- cockpit terminal, gates et guidance ;
- preuves Lean, surfaces périphériques et manifestes de preuve ;
- protocoles, audits, freezes et documentation ;
- tests API, gates, intégration, Sigma, UI et racine ;
- correctifs de compatibilité détectés pendant la validation.

Corrections finales ajoutées pendant l'audit :

- exécution directe de `agents/run_pipeline.py` redirigée vers le pipeline
  Sigma canonique ;
- contrat compact Brody complété avec `topic`, `compact_mode`,
  `deep_snapshots_omitted` et `debug_payload_omitted` ;
- fallbacks du pack éducation complétés avec la politique Ragnarok ;
- taxonomie mémoire SRL V2 alignée dans les tests ;
- nouvelle source readonly Graphiti/Neo4j ajoutée à la whitelist ;
- encodages UTF-8 des corrections auditées restaurés.

## Périmètre du commit 2

Le deuxième commit contient uniquement :

`scripts/run_brody_terminal_enriched.ps1`

Le fichier correspond au blob audité issu de `8fe4583` et conserve le
transport terminal Brody avec encodage UTF-8 explicite.

SHA-256 validé :

`50a9fd88318fbd8e9b8c906852c2cfb2199a55d3dbcb0526872e483f2f2a98f8`

Contrôles effectués :

- correspondance exacte du blob ;
- correspondance SHA-256 ;
- parsing PowerShell valide ;
- aucun chemin machine ;
- aucun secret ;
- aucune commande Git destructive ;
- aucune autorité souveraine ajoutée.

## Validation locale

La validation a été réalisée par couverture segmentée afin de
conserver les résultats après interruptions et redémarrages Windows.

| Surface | Résultat |
|---|---:|
| `tests/api` | Couverture segmentée complète ; dernier segment `1074 passed, 1 skipped` |
| `tests/gates` | `559 passed` |
| `tests/integration` | `53 passed` |
| `tests/cli` | `11 passed` |
| `tests/legacy_root` | `4 passed` |
| `tests/non_sovereignty` | `139 passed` |
| `tests/periphery` | `326 passed` |
| `tests/sigma` | `817 passed` |
| `tests/ui` | `33 passed` |
| Tests racine | Couverture segmentée complète |
| CIC readonly provider | `23 passed` |
| P73 | `91 passed` |
| P74 | `84 passed` |
| P75 | `78 passed` |
| P76 | `98 passed` |
| P77 | Couverture segmentée complète |
| Contrôles finaux P77 | `2 passed`, exit `0` |
| Nettoyage ciblé final | `78 passed`, exit `0` |
| `verify_all` | PASS |
| Forbidden-content check | PASS |

Les résultats segmentés et les relances se chevauchent. Ils ne sont donc
pas additionnés pour produire un total artificiel.

Trois fichiers nommés `test_*.py` sont des helpers et ne collectent aucun
test Pytest :

- `tests/test_seal_tamper.py` ;
- `tests/test_signature_tamper.py` ;
- `tests/test_threshold_fuzz.py`.

Leur exit Pytest `5` signifie `no tests collected`, et non un échec
fonctionnel.

## Artefacts locaux exclus

Les éléments suivants restent physiquement présents mais ne sont pas
publiés :

- `.mcp.json` ;
- `audit/obsidia_gateway_usage.jsonl` ;
- `audit/local_test_recovery/` ;
- `.local_audits/` ;
- `.local_exports/` ;
- caches et rapports locaux.

Ils sont exclus localement sans suppression des originaux.

## Intégrité et limites connues

`MANIFEST_SHA256.json` est régénéré dans le commit 3 depuis la
liste des fichiers suivis par Git. Le manifeste s'exclut lui-même afin
d'éviter une auto-référence instable.

Les espaces de fin de ligne historiques présents dans certains rapports,
snapshots et artefacts Freeze A ont été conservés. Aucun nettoyage
global n'a été appliqué, afin de préserver la traçabilité
des artefacts importés.

Un credential historique révoqué reste connu dans d'anciens commits
distants. Sa valeur n'est pas reproduite ici. Aucun credential actif n'est
présent dans l'arbre courant audité.

## Invariants de gouvernance

```text
DECISION_AUTHORITY = KX108_ONLY
ADVISORY_ONLY      = TRUE
NO_AUTO_ACT        = TRUE
NO_VERDICT         = TRUE hors kernel
NO_MEMORY_WRITE    = TRUE hors journaux append-only explicitement bornés
NO_KERNEL_MUTATION = TRUE
NO_X108_MUTATION   = TRUE
Suite autorisée

La seule suite autorisée après ce commit est :

pousser integration/freeze-a-to-main-20260717 ;
ouvrir une pull request vers main ;
examiner les contrôles GitHub ;
fusionner uniquement après revue explicite.

Aucun merge direct dans main n'est autorisé par cette clôture.
