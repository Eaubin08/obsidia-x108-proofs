# OBSIDIA OIE EXTERNAL BENCHMARK HARNESS — V0

**Statut :** Actif — OIE External Harness V0
**Date :** 2026-07-01
**Base :** OIE V0.1 (CostReceipt, DomainMetrics, DCA)
**Autorite :** Kernel X-108 (KX108_ONLY) — OIE reste non souverain

---

## 1. Ce que ce harness mesure

Le harness compare Obsidia a un provider externe (Claude Code CLI / API) sur les memes taches, avec les memes contraintes de sortie et les memes metriques.

Il produit des **ExternalComparisonReceipts** : des unites de mesure typees, JSON-serialisables, non-souveraines.

Ce que le harness mesure :
- Latence Obsidia vs latence externe
- Succes/echec de la tache externe
- Extrait de sortie externe (500 chars max)
- Usage tokens si disponible (souvent indisponible via CLI)
- Ratio d'economie (`savings_ratio_vs_external`) si le cout externe est mesurable
- Cout evite (`avoided_cost_eur_per_1m`)

Ce que le harness ne fait pas :
- Il n'emet aucun signal ACT
- Il ne mute pas le kernel
- Il n'ecrit pas en memoire, Graphiti ou Neo4j
- Il ne stocke aucune cle API
- Il ne valide pas la qualite semantique de la sortie (hors scope V0)

---

## 2. Difference entre baseline theorique et comparaison reelle

| Type | Source | Fiabilite |
|---|---|---|
| **Baseline theorique** (OIE V0/V0.1) | Audit OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0 | Figee, reproductible, pas de run reel |
| **Comparaison reelle** (ce harness) | Run effectif Claude CLI | Variable, depends on model/pricing |

La baseline theorique dit : "si on utilisait BT_API_NORMAL (25 000 EUR / 1M), on economiserait X". C'est une reference de regime economique.

La comparaison reelle dit : "on a lance la meme tache sur Claude CLI, voici ce qu'on a mesure". Elle peut confirmer ou nuancer la baseline.

Les deux sont complementaires. La baseline est utile pour la gouvernance et les contrats. La mesure reelle est utile pour les audits et les negociations avec des providers.

---

## 3. Pourquoi dry-run par defaut

Par defaut, le script ne fait aucun appel reseau :

```
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

Raisons :
1. **Securite** : aucune cle API ne doit etre exposee accidentellement dans les logs CI.
2. **Reproductibilite** : un run dry-run est toujours reproductible, peu importe l'environnement.
3. **Couts** : les appels API externes ont un cout reel. Un run non intentionne est un budget non prevu.
4. **Gouvernance** : le kernel X-108 ne doit pas declencher d'actions vers des providers externes sans approbation explicite.

En mode dry-run, les receipts produits sont valides et JSON-serialisables, avec :
- `external_network_allowed = false`
- `external_success = false`
- `external_error = "NETWORK_DISABLED"`
- `savings_ratio_vs_external = null`

---

## 4. Comment activer le mode reel

### Prerequis

1. Claude Code CLI doit etre installe et accessible via `claude` dans le PATH.
2. Claude Code doit etre authentifie (via `claude login` ou variable d'environnement appropriee).
3. L'approbation explicite doit etre donnee via la variable d'environnement.

### Mode smoke (une seule tache)

```powershell
# PowerShell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK="1"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

```bash
# Bash
OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1 python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

Cela execute uniquement la tache smoke :
`task_id = "fastpath_route_selection_smoke"`

### Mode complet (toutes les familles)

```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK="1"
$env:OIE_EXTERNAL_BENCHMARK_FULL="1"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

Cela execute les 7 familles de taches.

### Verification avant run

```powershell
# Verifier que Claude est disponible sans appel reseau
python -c "from apps.obsidia_api.inference_economy.external_comparison import detect_claude_cli; print(detect_claude_cli())"
```

---

## 5. Pourquoi les cles API ne doivent jamais etre committees

Le repo `obsidia-x108-proofs` est public ou semi-public. Une cle API committee par erreur :
- Est immediatement indexee par les scanners de secrets (GitHub, GitGuardian, etc.)
- Reste dans l'historique git meme apres suppression du fichier
- Peut etre exploitee avant que la cle soit revoquee

Regles :
- Ne jamais ecrire `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY` ou equivalent dans le code.
- Ne jamais les logguer dans les receipts.
- Utiliser uniquement des variables d'environnement.
- Le champ `secrets_redacted = True` (immutable) dans chaque receipt confirme qu'aucun secret n'a ete inclus.

---

## 6. Comment interpreter usage_unavailable

Quand `external_usage_available = false` :
- Le CLI Claude n'a pas expose les compteurs de tokens dans stdout.
- Le cout externe reel est inconnu.
- `savings_ratio_vs_external = null` et `avoided_cost_eur_per_1m = null`.
- `cost_source = "USAGE_UNAVAILABLE"`.

Cela ne signifie pas que le benchmark a echoue. La latence, le succes et l'extrait de sortie sont toujours disponibles.

Pour obtenir l'usage tokens :
- Utiliser l'API Claude directement (pas le CLI) avec le SDK Anthropic.
- Lire les champs `usage.input_tokens` et `usage.output_tokens` de la reponse.
- Renseigner `external_input_tokens`, `external_output_tokens`, `external_total_tokens`.
- Calculer `external_cost_eur_per_1m_estimate` selon la grille tarifaire du modele.
- Renseigner `external_cost_eur_per_1m_estimate` et `cost_source = "MEASURED"`.

Ce calcul est hors scope V0 (CLI uniquement) et sera ajoute en V1 avec integration SDK.

---

## 7. Comment utiliser les resultats pour completer le protocole

Le protocole `OBSIDIA_EXTERNAL_API_COST_COMPARISON_PROTOCOL_V0.md` definit les familles de tests. Le harness les execute.

Workflow complet :
1. Dry-run : valider que les receipts sont bien formes et que le harness tourne.
2. Detection : confirmer que Claude CLI est disponible (`claude_detected = true`).
3. Smoke run : activer le reseau, lancer uniquement la tache smoke.
4. Analyser l'extrait de sortie : la reponse est-elle dans le bon format ?
5. Full run : activer `OIE_EXTERNAL_BENCHMARK_FULL=1`, lancer toutes les familles.
6. Comparer les latences Obsidia vs Claude CLI.
7. Si l'usage est disponible (via SDK), calculer `savings_ratio_vs_external` et `avoided_cost_eur_per_1m`.
8. Archiver le JSON de receipts dans `docs/audits/` pour traçabilite.

---

## 8. Architecture du harness

```
apps/obsidia_api/inference_economy/
  external_comparison.py          # ExternalComparisonReceipt, detect_claude_cli, run_claude_cli

scripts/performance/
  run_oie_external_claude_benchmark_v0.py    # script principal
  oie_external_claude_benchmark_v0_receipts.json  # sortie JSON

tests/
  test_oie_external_comparison.py            # 35+ tests

docs/audits/
  OBSIDIA_OIE_EXTERNAL_BENCHMARK_HARNESS_V0.md  # ce document
  OBSIDIA_EXTERNAL_API_COST_COMPARISON_PROTOCOL_V0.md  # protocole theorique
```

---

## 9. Familles de taches

| task_family | Route Obsidia | Cout EUR/1M | Baseline externe |
|---|---|---|---|
| fast_path_vs_llm_simple | fast_path | 0.0015 | BT_API_SIMPLE |
| brody_vs_assistant | brody_chat | 0.20 | BT_API_NORMAL |
| bank_vs_domain_llm | bank_connector | 0.70 | BT_API_NORMAL |
| trading_vs_domain_llm | trading_connector | 0.84 | BT_API_NORMAL |
| gps_aviation_vs_domain_llm | aviation_connector | 0.91 | BT_API_NORMAL |
| obsidure_vs_code_agent | obsidure_lean_targeted | 23.92 | BT_AGENTIC |
| lean_proof_vs_long_reasoning | lean_canon_check | 13.29 | BT_API_NORMAL |

---

## 10. Gouvernance

- `emits_act = False` : le harness ne prend aucune decision.
- `kernel_mutation = False` : le harness ne modifie pas le kernel.
- `readonly = True` : les receipts sont en lecture seule.
- `secrets_redacted = True` : aucun secret dans les receipts.
- `decision_authority = KX108_ONLY` : le kernel X-108 reste l'unique autorite.
- Le harness ne peut pas declencher d'action sur les systemes Obsidia.
- Il mesure et rapporte. C'est tout.
