# OBSIDIA OIE External Benchmark Results V0.3

**Statut :** Analyse des resultats V0.2 — base pour protocole V0.3
**Date :** 2026-07-01
**Branche :** feat/path-brody-r02-thermo-mcp-closure
**Autorite :** Kernel X-108 (KX108_ONLY) — OIE reste non souverain

---

## 1. Executive result

### Ce que V0.2 a prouve

- Claude Code CLI (2.1.179) peut classifier des routes Obsidia avec **6/7 route match** (routing full run).
- Claude peut produire des sorties metier structurees (ALLOW/HOLD/BLOCK) avec **4/6 label match** (domain-output run).
- La separation routing/domain-output (V0.2) etait necessaire : les taches metier evaluees comme routing produisaient des faux negatifs.
- L'infrastructure de benchmark est fonctionnelle : receipts JSON, gouvernance non-souveraine, dry-run par defaut, UTF-8 safe.

### Ce que V0.2 ne prouve pas

- **Le cout reel** : `usage_available = 0/7` dans tous les runs. Claude Code CLI ne retourne pas les compteurs tokens. Aucune comparaison de cout n'est valide a ce stade.
- **La difference Obsidia vs API inference** : le benchmark V0.1/V0.2 testait Claude comme routeur ou comme executeur de sortie metier. Il ne mesurait pas le cas central : Obsidia remplace une inference externe par une decision deterministe (model-call avoided).
- **La qualite semantique** : le benchmark mesure si un label correspond, pas si la decision est correcte metier.

### Pourquoi V0.3 existe

V0.3 recentre le benchmark sur les metriques OIE initiales :
- **API inference avoided** : combien d'appels modele Obsidia evite-t-il ?
- **Cost avoided** : quel est le cout evite par decision deterministe vs appel API externe ?
- **Latency avoided** : quelle est la difference de latence ?
- **Quality penalty** : quelle est la degradation de qualite quand Obsidia est compare a un LLM general ?
- **Model call avoided rate** : fraction des taches ou Obsidia n'a pas besoin d'appel modele.

---

## 2. Original objective

Le benchmark OIE externe a ete concu pour mesurer :

1. **API inference avoided** : Obsidia Fast Path, Bank, Trading, GPS n'appellent pas de LLM pour des decisions deterministes. Un LLM externe devrait. La difference est le nombre d'inferences evitees.

2. **Cost avoided** : `avoided_cost_eur_per_1m = external_cost - obsidia_cost`. Avec `BT_API_NORMAL = 25 000 EUR/1M`, une decision bank a `0.70 EUR/1M` produit un ratio de `25 000 / 0.70 = 35 714x`. Ce chiffre n'est valide que si `cost_source = MEASURED`.

3. **Inference avoided** : `model_call_avoided = external_model_call_required AND NOT obsidia_model_call_required`. Fast Path, Bank, Trading, GPS evitent l'appel modele.

4. **Quality and errors** : quand Obsidia choisit une route ou produit une sortie, la qualite est-elle equivalente, meilleure ou moins bonne qu'un LLM general ?

5. **Routing difference** : Claude classe-t-il les memes requetes dans les memes routes qu'Obsidia ? Les desaccords indiquent soit une erreur de classification externe, soit une limitation du prompt.

L'objectif n'etait pas de tester Claude comme meilleur routeur — il etait de mesurer ce qu'Obsidia remplace.

---

## 3. Frozen commits context

| Commit | Description | Statut |
|---|---|---|
| `73444cd` | Portfolio benchmark OIE V0.1 frozen — OSCA 38241x, OAPI 47143x, ODPI 30612x | Fige |
| `8c724df` | Raw seven-family benchmark — premier run complet Claude CLI | Fige |
| V0.2 (branch) | Split routing/domain-output, token estimate strategy | Non commis |
| V0.3 (branch) | Metriques differentielles OIE, failure tracking, UTF-8 safe, document resultat | Non commis |

---

## 4. Observed V0.2 routing results

Run reel : `OIE_EXTERNAL_BENCHMARK_FULL=1` + `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1`

| Family | Expected | Detected | Match | Quality | Latency (ms) | Cost source |
|---|---|---|---|---|---|---|
| fast_path_vs_llm_simple | FAST_PATH | FAST_PATH | True | 1.0 | ~800 | USAGE_UNAVAILABLE |
| brody_vs_assistant | BRODY | FAST_PATH | False | 0.2 | ~900 | USAGE_UNAVAILABLE |
| bank_vs_domain_llm | BANK | BANK | True | 1.0 | ~850 | USAGE_UNAVAILABLE |
| trading_vs_domain_llm | TRADING | TRADING | True | 1.0 | ~800 | USAGE_UNAVAILABLE |
| gps_aviation_vs_domain_llm | GPS | GPS | True | 1.0 | ~850 | USAGE_UNAVAILABLE |
| obsidure_vs_code_agent | OBSIDURE | OBSIDURE | True | 1.0 | ~900 | USAGE_UNAVAILABLE |
| lean_proof_vs_long_reasoning | OBSIDURE | OBSIDURE | True | 1.0 | ~850 | USAGE_UNAVAILABLE |

**Resultats :**
- external_success : 7/7
- route_match : 6/7
- avg_routing_quality : 0.90
- usage_available : 0/7
- Seul Brody mal classe (FAST_PATH au lieu de BRODY) — sous-routage, score 0.2

**Note :** Le mismatch Brody/FAST_PATH est coherent : un LLM sans contexte Obsidia ne distingue pas facilement une question sur le kernel d'une requete triviale. Obsidia classe deterministiquement grace au contexte session.

---

## 5. Observed V0.2 domain-output results

Run reel : `OIE_EXTERNAL_BENCHMARK_DOMAIN=1` + `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1`

| Family | Expected labels | Detected | Match | Quality | Failure type |
|---|---|---|---|---|---|
| bank_vs_domain_llm | ALLOW, HOLD, BLOCK | None | False | 0.0 | UNPARSEABLE_OUTPUT |
| trading_vs_domain_llm | VALID, HOLD_RISK, BLOCK | VALID | True | 1.0 | NONE |
| gps_aviation_vs_domain_llm | ALLOW, HOLD, BLOCK | ALLOW | True | 1.0 | NONE |
| brody_vs_assistant | ANSWER_OK, ANSWER_FAIL | None | False | 0.0 | UNPARSEABLE_OUTPUT |
| obsidure_vs_code_agent | PATCH_OK, PATCH_FAIL | PATCH_OK | True | 1.0 | NONE |
| lean_proof_vs_long_reasoning | PROOF_OK, PROOF_FAIL | PROOF_OK | True | 1.0 | NONE |

**Resultats :**
- external_success : 6/6
- label_match : 4/6
- avg_domain_quality : 0.67
- usage_available : 0/6

**Analyse des echecs :**
- **Bank** : le prompt V0.1 ne demandait pas "Return exactly one label". Claude a explique sa decision au lieu de retourner un label seul. Corrige en V0.3 avec "Return exactly one label from: ... Do not explain."
- **Brody** : meme probleme — Claude a produit une explication complete plutot qu'un label ANSWER_OK/ANSWER_FAIL. Corrige en V0.3.

---

## 6. Cost and token status

### Claude Code CLI : usage_available = 0

Claude Code CLI (`claude -p`) ne retourne pas les compteurs tokens dans stdout. Consequence :

```
external_usage_available = False  (tous les runs)
savings_ratio_vs_external = None
avoided_cost_eur_per_1m   = None
cost_source               = USAGE_UNAVAILABLE
```

**Aucune comparaison de cout n'est valide** avec `cost_source = USAGE_UNAVAILABLE`.

### Estimation locale (CHAR_ESTIMATE)

V0.2 a introduit `estimate_tokens_from_text(text) = ceil(len(text) / 4)`. Cette estimation :
- Ne remplace pas un comptage reel
- Est marquee `cost_source = ESTIMATED`
- Sert uniquement au pre-budgeting
- **N'est jamais presentee comme un cout final**

### Regles d'interpretation

| cost_source | Signification | Comparaison valide ? |
|---|---|---|
| `USAGE_UNAVAILABLE` | Aucune donnee | **Non** |
| `CHAR_ESTIMATE` | Estimation locale ceil(len/4) | Non — indicatif seulement |
| `ESTIMATED` | Prix fournis via env, tokens estimes | Avec reserve — non final |
| `MEASURED` | Usage reel via SDK Anthropic | **Oui** |

**Regle absolue : `ESTIMATED != MEASURED`. Un benchmark cout final requiert `cost_source = MEASURED`.**

### Acces au cout reel

Pour obtenir le cout reel, il faut utiliser le SDK Anthropic directement (pas le CLI) :

1. Appeler l'API avec `anthropic.Anthropic()` depuis le SDK Python
2. Lire `response.usage.input_tokens` et `response.usage.output_tokens`
3. Calculer `external_cost_eur_per_1m_estimate` selon la grille tarifaire du modele
4. Renseigner `cost_source = MEASURED`

Ce flux est hors scope V0.3 (CLI uniquement) et sera ajoute en V1 SDK.

---

## 7. Obsidia difference matrix

| Axis | External API inference behavior | Obsidia / OIE behavior | Difference measured |
|---|---|---|---|
| Fast Path | Appel LLM complet, ~800ms, ~25 000 EUR/1M | Cache deterministe, <1ms, 0.0015 EUR/1M | model_call_avoided=True, latency_ratio~1600x |
| Routing | Classification LLM (6/7 correct) | Router deterministe base sur contexte session | Obsidia ne fait pas d'inference — la decision est reglee |
| Domain bridge | LLM general sans contexte domaine | Bridge deterministe Bank/Trading/GPS | model_call_avoided=True pour Bank, Trading, GPS |
| Brody | Pas de session persistante, reprise zero-shot | Session enrichie avec contexte Graphiti/Neo4j | Qualite contextuelle superieure (non mesurable ici) |
| Obsidure | LLM long reasoning, ~1200ms | Lean 4 targeted patch, reproductible | Obsidure fait un appel mais cible uniquement l'invariant |
| Lean proof | Long reasoning stochastique | Verification formelle deterministe | Correctness guarantie vs probable |
| Cost source | CLI : tokens indisponibles | OIE : cout par layer mesure, OSCA 38241x | Comparaison directe impossible sans SDK |
| Traceability | Sortie LLM — non reproductible | Receipt signe, Merkle sealed | Auditabilite complete |
| Non-sovereignty | LLM decide | OIE mesure, Kernel X-108 decide | EMITS_ACT=False toujours |

---

## 8. Metrics that matter now

| Metric | Definition | Source | Current status | Next action |
|---|---|---|---|---|
| OSCA | Geometric mean savings_ratio all layers | OIE V0.1 portfolio | **38 241x** (frozen 73444cd) | Stable — ne pas recalculer sans nouveau layer |
| OAPI | BT_API_NORMAL / mean cost (Fast+Brody+Bank+Trading+GPS) | OIE V0.1 | **47 143x** | Stable |
| ODPI | BT_API_NORMAL / mean cost (Bank+Trading+GPS) | OIE V0.1 | **30 612x** | Stable |
| DCA_API_NORMAL | baseline_cost / obsidia_cost par domaine | OIE V0.1 | Calcule par domaine | Stable |
| route_accuracy | route_match / routing_tasks_attempted | External run | **6/7 = 0.857** | Ameliorer prompt Brody |
| domain_label_accuracy | label_match / domain_tasks_attempted | External run | **4/6 = 0.667** | Prompts "Return exactly one label" en V0.3 |
| model_call_avoided_rate | receipts avec model_call_avoided / total | V0.3 diff metrics | Non calcule (dry-run) | Lancer run reel V0.3 |
| cost_available_rate | receipts avec cost source != UNAVAILABLE / total | V0.3 | **0/13** via CLI | Activer SDK pour MEASURED |
| estimated_cost_rate | receipts ESTIMATED / total | V0.3 | 0 (prix non fournis) | Fournir prix env |
| timeout_rate | receipts timeout / total | V0.3 | 0 (dry-run) | Mesurer en run reel |
| provider_refusal_rate | receipts PROVIDER_REFUSAL / total | V0.3 | 0 (dry-run) | Mesurer en run reel |
| encoding_error_rate | receipts encoding_error_occurred / total | V0.3 | 0 (dry-run) | Mesurer en run reel |
| quality_penalty | mean(1 - quality_score) | V0.3 diff metrics | N/A (dry-run) | Calculer sur run reel |

---

## 9. V0.3 next benchmark protocol

Les etapes recommandees pour le prochain cycle de mesure :

**Etape 1 — Routing full V0.3**
```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
$env:OIE_EXTERNAL_BENCHMARK_FULL = "1"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```
Objectif : confirmer que les prompts routing corriges maintiennent 6/7 ou ameliorent.

**Etape 2 — Domain-output full V0.3**
```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
$env:OIE_EXTERNAL_BENCHMARK_DOMAIN = "1"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```
Objectif : verifier que "Return exactly one label" corrige Bank et Brody (4/6 -> 6/6).

**Etape 3 — Cost estimate run (optionnel)**
```powershell
$env:OIE_EXTERNAL_INPUT_COST_PER_1M  = "<prix_input>"
$env:OIE_EXTERNAL_OUTPUT_COST_PER_1M = "<prix_output>"
$env:OIE_EXTERNAL_MODEL_LABEL        = "<modele>"
$env:OIE_EXTERNAL_COST_ESTIMATE      = "1"
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```
Objectif : produire `cost_source = ESTIMATED` par tache. **Non final — indicatif seulement.**

**Etape 4 — SDK/API measured cost (V1 futur)**
- Remplacer `run_claude_cli` par un appel SDK Anthropic direct
- Lire `response.usage.input_tokens`, `response.usage.output_tokens`
- Produire `cost_source = MEASURED`
- Activer `compute_oie_differential_metrics` avec `external_cost_eur_per_1m_measured`

**Etape 5 — Document resultat final**
- Archiver le JSON de receipts dans `docs/audits/`
- Mettre a jour ce document avec les resultats V0.3 reels
- Verifier coherence avec OSCA/OAPI/ODPI frozen

---

## 10. V0.4 — Mode SDK Anthropic mesure optionnel

### Objectif

V0.4 ajoute un second provider au harness : le SDK Anthropic Python.
Quand `OIE_EXTERNAL_PROVIDER=anthropic_sdk`, le harness appelle l'API directement (pas via le CLI `claude -p`) et lit `response.usage.input_tokens` / `response.usage.output_tokens`.
Cela produit des compteurs reels de tokens — condition necessaire pour obtenir `cost_source = SDK_USAGE_MEASURED`.

### Nouveaux champs de receipt (V0.4)

| Champ | Type | Valeur par defaut | Description |
|---|---|---|---|
| `external_model_label` | str | `""` | Identifiant du modele SDK appele |
| `external_cost_eur_measured` | float | `None` | Cout reel calcule depuis usage SDK (EUR) |
| `external_cost_eur_per_1m_measured` | float | `None` | Cout reel pour 1M tokens (EUR/1M) |
| `cost_source` | str | `USAGE_UNAVAILABLE` | Source du cout : `SDK_USAGE_MEASURED`, `SDK_USAGE_MEASURED_NO_PRICE`, `ESTIMATED`, `USAGE_UNAVAILABLE` |

### Nouveaux sources de cout (V0.4)

| cost_source | Signification | Comparaison valide ? |
|---|---|---|
| `SDK_USAGE_MEASURED` | Usage reel SDK + prix fournis | **Oui — cout final** |
| `SDK_USAGE_MEASURED_NO_PRICE` | Usage reel SDK, prix non fournis | Non — tokens connus, cout inconnu |
| `ESTIMATED` | Estimation locale, prix fournis | Avec reserve — non final |
| `USAGE_UNAVAILABLE` | CLI sans usage tokens | **Non** |

### Provider modes (V0.4)

| Variable env | Comportement |
|---|---|
| `OIE_EXTERNAL_PROVIDER` absent ou `cli` | Claude Code CLI (comportement V0.3 inchange) |
| `OIE_EXTERNAL_PROVIDER=anthropic_sdk` | SDK Anthropic Python, usage tokens reels |
| `OIE_EXTERNAL_MODEL_LABEL` | Modele a appeler (requis si provider=anthropic_sdk) |
| `ANTHROPIC_API_KEY` | Cle API — lue uniquement depuis env, jamais logguee, jamais dans les receipts |

### Regles de securite (immuables)

- `ANTHROPIC_API_KEY` est lue via `os.environ.get("ANTHROPIC_API_KEY", "")` uniquement.
- Elle n'est jamais ecrite dans les receipts, jamais dans les logs, jamais dans les JSON produits.
- La console affiche uniquement `ANTHROPIC_API_KEY set: True/False` — jamais la valeur.
- `secrets_redacted = True` reste immutable dans chaque receipt (gouvernance kernel X-108).
- Si le SDK Anthropic n'est pas installe : failure controlee (`FAILURE_SDK_NOT_AVAILABLE`), pas d'exception non geree.
- Si `OIE_EXTERNAL_MODEL_LABEL` est absent : failure controlee (`FAILURE_MODEL_NOT_CONFIGURED`), pas d'appel reseau.

### Activation du mode SDK

```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
$env:OIE_EXTERNAL_PROVIDER                = "anthropic_sdk"
$env:OIE_EXTERNAL_MODEL_LABEL             = "claude-haiku-4-5-20251001"
$env:ANTHROPIC_API_KEY                    = "<cle_non_committee>"
# Optionnel — pour cost_source = SDK_USAGE_MEASURED :
$env:OIE_EXTERNAL_INPUT_COST_PER_1M       = "0.80"   # EUR / 1M tokens input
$env:OIE_EXTERNAL_OUTPUT_COST_PER_1M      = "4.0"    # EUR / 1M tokens output
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

Sans les prix, le harness produit `cost_source = SDK_USAGE_MEASURED_NO_PRICE` : les tokens sont connus mais le cout EUR n'est pas calcule.
Avec les prix, il produit `cost_source = SDK_USAGE_MEASURED` et `external_cost_eur_per_1m_measured` — seul type valide pour une comparaison cout finale.

### Ce que V0.4 ne change pas

- Le mode CLI (`OIE_EXTERNAL_PROVIDER=cli` ou absent) est identique au comportement V0.3.
- Les receipts V0.3 (failure tracking, differential metrics, benchmark_kind) sont inchanges.
- Les 249 tests V0.3 restent valides.
- Aucun appel reseau sans `OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK=1`.
- Aucun commit automatique. Aucune modification kernel / sigma / Brody / Obsidure.

### Statut V0.4

- Implementation : completee (external_comparison.py, run_oie_external_claude_benchmark_v0.py).
- Tests : 11 nouveaux tests V0.4 ajoutes (TestV04ProviderSelection, TestRunAnthropicSdk, TestComputeMeasuredSdkCost, TestReceiptV04Fields, TestOIEDifferentialMetricsV04, TestV04DryRunAndImportSafety).
- Run reel : non effectue (necessite cle API externe et approbation explicite).
- Commit : non effectue (politique no-auto-commit).

---

## 11. V0.5 — Provider Gemini SDK

### Pourquoi V0.5 existe

V0.4 a introduit le provider SDK Anthropic. En pratique, l'acces peut etre bloque
par un manque de credit ou une configuration compte. Gemini API propose un free tier
accessible sans credit prepaye — utile pour valider le harness avec des tokens reels.

V0.5 ajoute `OIE_EXTERNAL_PROVIDER=gemini_sdk` via le package Python `google-genai`.
Les modes CLI et Anthropic SDK sont inchanges.

### Modele recommande

```
gemini-2.0-flash-lite
```

Choix : le modele le plus economique de la famille Gemini 2.0.
Adapte aux taches courtes du benchmark (un label, une route).

### Activation

```powershell
$env:OIE_EXTERNAL_BENCHMARK_ALLOW_NETWORK = "1"
$env:OIE_EXTERNAL_PROVIDER                = "gemini_sdk"
$env:OIE_EXTERNAL_MODEL_LABEL             = "gemini-2.0-flash-lite"
$env:GEMINI_API_KEY                       = "<cle_non_committée>"
# Optionnel — pour cost_source = SDK_USAGE_MEASURED :
$env:OIE_EXTERNAL_INPUT_COST_PER_1M       = "0.036"   # EUR / 1M tokens input
$env:OIE_EXTERNAL_OUTPUT_COST_PER_1M      = "0.144"   # EUR / 1M tokens output
python scripts/performance/run_oie_external_claude_benchmark_v0.py
```

`GOOGLE_API_KEY` est aussi accepte comme fallback si `GEMINI_API_KEY` est absent.

### Usage tokens Gemini

Le SDK `google-genai` expose les tokens via :

```python
interaction.usage.total_input_tokens
interaction.usage.total_output_tokens
interaction.usage.total_tokens
```

Ces champs alimentent `compute_measured_sdk_cost()` — meme fonction que pour Anthropic.
Si les tokens sont disponibles sans prix : `cost_source = SDK_USAGE_MEASURED_NO_PRICE`.
Si tokens + prix fournis : `cost_source = SDK_USAGE_MEASURED`.

### Regles de securite (inchangees et etendues)

- `GEMINI_API_KEY` et `GOOGLE_API_KEY` lues uniquement depuis env, jamais logguees.
- Les messages d'erreur sont passes dans `sanitize_external_error_message()` avant tout log.
- Patterns masques : `AIza...` (Google), `sk-ant-...` (Anthropic), valeurs d'env litterales.
- `secrets_redacted = True` reste immutable dans chaque receipt.
- La console affiche uniquement `GEMINI_API_KEY set: True/False` — jamais la valeur.

### Failure types Gemini (V0.5)

| Failure type | Cause |
|---|---|
| `GEMINI_SDK_NOT_AVAILABLE` | Package `google-genai` non installe |
| `GEMINI_MODEL_NOT_CONFIGURED` | `OIE_EXTERNAL_MODEL_LABEL` absent |
| `GEMINI_AUTH_ERROR` | Cle absente (`GEMINI_API_KEY` et `GOOGLE_API_KEY` absentes) |
| `GEMINI_API_ERROR` | Exception pendant l'appel API |
| `TIMEOUT` | Delai depasse |

### Statut V0.5

- Implementation : completee (external_comparison.py, run_oie_external_claude_benchmark_v0.py).
- Tests : 22 nouveaux tests V0.5 (TestV05GeminiConstants, TestSanitizeExternalErrorMessage, TestRunGeminiSdk, TestComputeMeasuredSdkCostGemini, TestV05ProviderDispatch).
- Run reel : non effectue (necessite package google-genai et cle API).
- Commit : non effectue (politique no-auto-commit).

---

## 12. V0.5.1 — Correction cost_source Gemini + rapport full routing

### Bug corrige

`build_real_receipt` verifiait `provider == PROVIDER_SDK` pour decider d'appeler
`compute_measured_sdk_cost()`. Cela excluait `PROVIDER_GEMINI` : quand Gemini
retournait des tokens reels, le chemin tombait dans `elif cost_estimate_enabled`,
qui requiert `OIE_EXTERNAL_COST_ESTIMATE=1`. Resultat : `cost_source = USAGE_UNAVAILABLE`
meme avec des tokens reels.

**Correction** : condition changee en `provider in (PROVIDER_SDK, PROVIDER_GEMINI)`.

Les deux providers SDK appellent maintenant `compute_measured_sdk_cost()` des que
`usage_available = True` et `input_tokens is not None`, independamment de
`OIE_EXTERNAL_COST_ESTIMATE` (flag reserve au chemin CLI / estimation texte).

### Impact

| Scenario | Avant V0.5.1 | Apres V0.5.1 |
|---|---|---|
| Gemini + tokens + prix env | `USAGE_UNAVAILABLE` | `SDK_USAGE_MEASURED` |
| Gemini + tokens sans prix | `USAGE_UNAVAILABLE` | `SDK_USAGE_MEASURED_NO_PRICE` |
| Gemini + cost_estimate=False | `USAGE_UNAVAILABLE` | `SDK_USAGE_MEASURED` si prix |
| Anthropic SDK | inchange | inchange |
| CLI dry-run | inchange | inchange |

### Rapport full routing

Nouveau document : `docs/audits/OBSIDIA_OIE_GEMINI_FULL_ROUTING_BENCHMARK_V0_5_1.md`

Contient :
- Protocole run 7 familles routing avec Gemini
- Tables A–H : summary, per-family, cost/tokens, latency, route quality, OIE differential, governance, valid/invalid claims
- Smoke observe (1 tache) : `route_match=True`, `usage_available=True`, `quality_score=1.0`
- Templates a remplir lors du run reel

### Positionnement

> Obsidia is not compared as a larger model. Obsidia is compared as an inference-avoidance and governance layer.

### Statut V0.5.1

- Bug cost_source corrige dans `run_oie_external_claude_benchmark_v0.py` (ligne 505).
- Table compact per-task ajoutee avant `--- Receipts summary ---`.
- Label benchmark mis a jour : `OIE_EXTERNAL_BENCHMARK_V0.5`.
- Tests : 12 nouveaux tests V0.5.1 (`TestV051GeminiCostFix`).
- Rapport full routing cree : `docs/audits/OBSIDIA_OIE_GEMINI_FULL_ROUTING_BENCHMARK_V0_5_1.md`.
- Run reel : non effectue (necessite GEMINI_API_KEY + ALLOW_NETWORK).
- Commit : non effectue (politique no-auto-commit).

---

## 13. Conclusion

Le benchmark OIE externe ne teste pas si Claude est un bon routeur.

Il teste si Obsidia peut remplacer des appels API d'inference classiques par des decisions deterministes, reproductibles, auditables — et a quel cout.

Les resultats V0.2 confirment que Claude peut classifier correctement les routes Obsidia dans 6/7 cas. Cela valide que les categories de routes sont semantiquement distinctes. Mais ce n'est pas la metrique finale.

La metrique finale est :

> **Obsidia does not win by making tokens cheaper; it wins by proving when tokens are not needed.**

Fast Path, Bank, Trading, GPS — ces layers n'appellent pas de LLM. Ils remplacent une inference par une decision prouvee. Le cout evite n'est pas un ratio de prix — c'est une inference qui n'a pas eu lieu.

Quand `model_call_avoided = True` et `comparison_status = OK`, le benchmark est complet.
Jusqu'a `cost_source = MEASURED`, les chiffres de cout sont indicatifs uniquement.
