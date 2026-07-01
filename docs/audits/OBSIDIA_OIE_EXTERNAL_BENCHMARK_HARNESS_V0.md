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

---

## 11. V0.2 — Separation routing / domain-output et strategie cout token

### 11.1 Pourquoi le raw benchmark 8c724df n'est pas un benchmark final

Le commit 8c724df (full run Claude, 7 familles) a revele deux problemes structurels :

**Probleme 1 — Melange routing et sortie metier.**
Le benchmark V0 evaluait des taches metier (bank : ALLOW/HOLD/BLOCK, trading : VALID/HOLD_RISK)
avec l'evaluateur routing qui cherche FAST_PATH/BRODY/BANK/etc. Ces prompts ne demandaient pas
une route — ils demandaient une decision metier. Le "mismatch" observe (5/7) etait en partie
du a ce mauvais couplage prompt/evaluateur, pas a une vraie erreur de routage.

**Probleme 2 — Usage absent.**
Claude Code CLI ne retourne pas les compteurs de tokens dans stdout. `usage_available=0/7` signifie
que le cout reel est inconnu. Les comparaisons de ratio cout sont inutilisables sans usage tokens.

Resultat brut 8c724df :

```
external_success = 7/7
route_match      = 2/7    <- chiffre non representatif (melange routing+metier)
avg_quality      = 0.3571 <- melange des deux evaluateurs
usage_available  = 0/7    <- cout reel indisponible via CLI
```

Ce chiffre ne doit pas etre presente comme un benchmark final.

### 11.2 Separation V0.2 : ROUTING_TASKS vs DOMAIN_OUTPUT_TASKS

V0.2 separe strictement les deux dimensions :

**ROUTING_TASKS (7 taches)**
- Chaque prompt demande explicitement "Return only one route label from this list: FAST_PATH, BRODY, BANK, TRADING, GPS, OBSIDURE."
- Evalue par `evaluate_route_quality` (detect route, OVER/UNDER routing, MISMATCH)
- Champ : `expected_route`, `external_detected_route`, `route_match`
- `benchmark_kind = ROUTING`

**DOMAIN_OUTPUT_TASKS (6 taches)**
- Chaque prompt demande une sortie metier specifique : ALLOW/HOLD/BLOCK, VALID/HOLD_RISK, PATCH_OK/FAIL, PROOF_OK/FAIL, ANSWER_OK/FAIL
- Evalue par `evaluate_domain_output_quality` (detect label dans liste autorisee)
- Champ : `expected_labels`, `external_detected_label`, `label_match`
- `benchmark_kind = DOMAIN_OUTPUT`

Un receipt ROUTING ne porte pas `expected_labels`. Un receipt DOMAIN_OUTPUT ne porte pas `expected_route`. Les deux evaluateurs ne se melangent jamais.

### 11.3 Cout reel indisponible via Claude Code CLI

Claude Code CLI (`claude -p`) ne retourne pas les compteurs de tokens dans stdout.
Par consequent :

- `external_usage_available = False` pour tous les receipts CLI
- `savings_ratio_vs_external = None`
- `avoided_cost_eur_per_1m = None`
- `cost_source = USAGE_UNAVAILABLE`

**Regle : ne jamais comparer cout final si `cost_source = USAGE_UNAVAILABLE`.**
Un ratio de cout calcule sans usage reel est trompeur.

### 11.4 Estimation token locale (CHAR_ESTIMATE)

En l'absence d'usage reel, V0.2 propose une estimation locale :

```
estimate_tokens_from_text(text) -> int
  = ceil(len(text) / 4)
  source = CHAR_ESTIMATE
```

Cette estimation est approximative et sert uniquement au pre-budgeting.
Elle ne remplace pas un comptage reel via SDK.

`compute_estimated_external_cost(input_text, output_text, input_cost_per_1m, output_cost_per_1m)`
retourne `cost_source = ESTIMATED` si les prix sont fournis, `USAGE_UNAVAILABLE` sinon.
Les prix viennent exclusivement des variables d'environnement — jamais hardcodes dans le code.

### 11.5 Usage reel futur via SDK/API

Pour obtenir le cout reel, il faut utiliser le SDK Anthropic directement (pas le CLI) :

1. Appeler l'API avec le SDK Python (`anthropic.Anthropic()`)
2. Lire `response.usage.input_tokens` et `response.usage.output_tokens`
3. Calculer `external_cost_eur_per_1m_estimate` selon la grille tarifaire du modele
4. Renseigner `cost_source = MEASURED`

Ce flux est hors scope V0.2 (CLI uniquement) et sera ajoute en V1.

### 11.6 Regles d'interpretation

| cost_source | Signification | Comparaison valide ? |
|---|---|---|
| `USAGE_UNAVAILABLE` | Pas de donnees usage | **Non** |
| `CHAR_ESTIMATE` | Estimation locale ceil(len/4) | Non (indicatif seulement) |
| `ESTIMATED` | Estimation depuis prix env | Avec reserve — marquer comme non-final |
| `MEASURED` | Usage reel via SDK | **Oui** |

**Regle absolue : `ESTIMATED != MEASURED`.**
Un rapport de benchmark ne peut presenter de ratio cout comme final que si `cost_source = MEASURED`.

### 11.7 Modes d'execution V0.2

| Variable env | Comportement |
|---|---|
| (aucune) | Dry-run, routing smoke uniquement (1 tache) |
| `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1` | Routing smoke reel |
| `OIE_EXTERNAL_BENCHMARK_FULL=1` | Routing full (7 taches) |
| `OIE_EXTERNAL_BENCHMARK_DOMAIN=1` | Domain output benchmark (6 taches) |
| `OIE_EXTERNAL_COST_ESTIMATE=1` | Active estimation cout si prix fournis |

Prix optionnels (ne jamais committer) :

```powershell
$env:OIE_EXTERNAL_INPUT_COST_PER_1M  = "3.0"   # EUR / 1M tokens input
$env:OIE_EXTERNAL_OUTPUT_COST_PER_1M = "15.0"  # EUR / 1M tokens output
$env:OIE_EXTERNAL_MODEL_LABEL        = "claude-sonnet-4"
```
