# OBSIDIA INFERENCE ECONOMY ENGINE — SPEC V0.1

**Statut :** Actif — OIE V0.1 (extension Domain Metrics)
**Commit de référence :** 73444cd (freeze audits INFERENCE_ECONOMY / DOMAIN_TOOL_ABSORPTION / STACK_LAYER_POSITIONING)
**Date :** 2026-07-01
**Autorité :** Kernel X-108 (KX108_ONLY)

---

## 1. Principe fondamental

> OIE mesure le coût. OIE ne décide pas.

Le kernel X-108 reste l'unique autorité de décision. OIE est une couche d'observation pure, non souveraine, qui transforme des mesures d'inférence en **Cost Receipts** vérifiables.

---

## 2. Ce que OIE fait

| Action | OIE V0 |
|---|---|
| Mesurer le coût d'une inférence (EUR / 1M actions) | ✅ |
| Comparer à une baseline Big Tech | ✅ |
| Calculer `savings_ratio` et `avoided_cost` | ✅ |
| Produire un `CostReceipt` JSON sérialisable | ✅ |
| Calculer les indices OSCA / OAPI / ODPI | ✅ |

## 3. Ce que OIE ne fait jamais

| Action interdite | Valeur figée |
|---|---|
| Émettre un signal ACT | `emits_act = False` |
| Modifier le kernel | `kernel_mutation = False` |
| Écrire en mémoire (Brody, Graphiti) | `memory_write = False` |
| Écrire dans Graphiti | `graphiti_write = False` |
| Écrire dans Neo4j | `neo4j_write = False` |
| Être writable depuis l'extérieur | `readonly = True` |
| Revendiquer l'autorité de décision | `decision_authority = KX108_ONLY` |

Ces constantes sont imposées par `__post_init__` et ne peuvent pas être écrasées par le caller.

---

## 4. Architecture OIE V0

```
apps/obsidia_api/inference_economy/
├── __init__.py          # exports publics
├── baselines.py         # constantes Big Tech (EUR / 1M)
├── cost_receipt.py      # CostReceipt dataclass + constantes gouvernance
└── meter.py             # create_cost_receipt() — seul point d'entrée

schemas/
└── obsidia_cost_receipt.schema.json   # schéma JSON validant un receipt

scripts/performance/
└── run_inference_economy_portfolio_benchmark_v0.py

tests/
└── test_inference_economy_cost_receipt.py
```

---

## 5. Baselines Big Tech (source : OBSIDIA_INFERENCE_ECONOMY_AUDIT_V0)

| Label | EUR / 1M actions | Usage |
|---|---|---|
| `BT_ENERGY_LOW` | 102 | Inférence énergétique légère |
| `BT_ENERGY_HEAVY` | 1 296 | Inférence énergétique lourde |
| `BT_API_SIMPLE` | 5 500 | API Big Tech simple |
| `BT_API_NORMAL` | 25 000 | API Big Tech standard (référence OSCA/OAPI/ODPI) |
| `BT_AGENTIC` | 160 000 | Pipeline agentique Big Tech |

---

## 6. Portfolio figé (audit V0)

| Route | EUR / 1M | Baseline | Ratio vs BT_API_NORMAL |
|---|---|---|---|
| Fast Path | 0.0015 | BT_API_NORMAL | ~16 666 667x |
| Brody chat | 0.20 | BT_API_NORMAL | 125 000x |
| Bank | 0.70 | BT_API_NORMAL | ~35 714x |
| Trading | 0.84 | BT_API_NORMAL | ~29 762x |
| GPS/Aviation | 0.91 | BT_API_NORMAL | ~27 473x |
| Lean canon check | 13.29 | BT_API_NORMAL | ~1 881x |
| Obsidure Lean ciblé | 23.92 | BT_API_NORMAL | ~1 045x |

---

## 7. Indices de portefeuille

### OSCA — Obsidia Savings Composite Average
Moyenne géométrique des `savings_ratio` sur l'ensemble du portefeuille.
Capture la performance économique toutes couches confondues.

```
OSCA = geometric_mean(savings_ratio_i  for all i)
```

### OAPI — Obsidia API Portfolio Index
Ratio entre BT_API_NORMAL et le coût moyen Obsidia sur le portefeuille **actions** (Fast Path + Brody + Bank + Trading + GPS).

```
OAPI = BT_API_NORMAL / mean(obsidia_cost_i  for i in API_PORTFOLIO)
```

### ODPI — Obsidia Domain Portfolio Index
Ratio entre BT_API_NORMAL et le coût moyen Obsidia sur le portefeuille **domaines** (Bank + Trading + GPS).

```
ODPI = BT_API_NORMAL / mean(obsidia_cost_i  for i in DOMAIN_PORTFOLIO)
```

---

## 8. Preuve du changement de régime économique

OIE prouve trois choses :

1. **Coût évité** (`avoided_cost_eur_per_1m`) — la différence absolue entre le coût Big Tech et le coût Obsidia, exprimée en EUR / 1M actions. C'est l'argent non dépensé.

2. **Inférence évitée** (`modules_skipped`) — les modules qui ont été court-circuités grâce aux preuves Lean / replays. Chaque module skippé représente de l'inférence non consommée.

3. **Changement de régime** — le `savings_ratio` montre que le coût n'est pas marginalement inférieur, mais structurellement différent (facteurs ×1 000 à ×16 000 000). C'est un régime économique distinct, pas une optimisation.

---

## 9. Gouvernance et contraintes

- OIE ne peut pas être instancié avec `emits_act=True` — `__post_init__` l'écrase.
- Tout `CostReceipt` est validable contre `schemas/obsidia_cost_receipt.schema.json`.
- Les constantes de gouvernance sont vérifiées par `tests/test_inference_economy_cost_receipt.py`.
- OIE ne fait jamais appel à des APIs externes, ne lit pas de secrets, ne pousse pas vers Neo4j ou Graphiti.

---

## 10. Évolutions prévues (hors scope V0)

- Intégration temps réel dans le pipeline Brody (lecture seule des métriques).
- Agrégation par fenêtre temporelle (OSCA glissant 7 jours).
- Export vers le dashboard Grafana (read-only push).
- Corrélation avec les replays Lean pour le calcul d'inférence évitée précis.

---

## 11. Why domain metrics matter (V0.1)

Les métriques OIE ne servent pas uniquement à prouver qu'Obsidia coûte moins cher. Elles servent à rendre chaque domaine pilotable économiquement. Une banque ne veut pas seulement savoir que l'IA coûte moins cher ; elle veut savoir combien coûte une décision de virement, combien coûte un HOLD conformité, combien d'appels API ont été évités, combien de reviews humaines ont été réduites, et quelles décisions restent auditables. Un domaine trading veut savoir combien coûte un signal, une contradiction, un HOLD risque ou un trade bloqué. Un domaine GPS/Aviation veut savoir combien coûte une anomalie terrain, une route non admissible ou une décision sécurité. OIE transforme donc les coûts techniques en métriques métier.

### Bank

- Coût moyen par décision de virement
- Coût moyen par alerte fraude
- Coût moyen par HOLD conformité
- Appels LLM/API évités
- Reviews humaines réduites
- Taux HOLD/BLOCK/ACT
- Contradictions et unknowns détectés
- Preuve/replay pour audit bancaire

### Trading

- Coût moyen par signal traité
- Coût moyen par décision trade ou HOLD
- Signaux contradictoires
- Risque excessif détecté
- Appels LLM/API évités
- Retries évités
- Latence moyenne
- Preuve/replay décisionnelle

### GPS/Aviation

- Coût moyen par signal terrain
- Coût moyen par anomalie détectée
- Coût moyen par décision HOLD/BLOCK sécurité
- Incohérences signal
- Pertes de confiance
- Routes non admissibles détectées
- Appels API/LLM évités
- Preuve/replay terrain

### Brody

- Coût moyen par réponse
- Contexte utilisé vs contexte évité
- Mémoire utilisée vs mémoire non lue
- Modules activés vs modules skippés
- Preuve que Brody reste non souverain (emits_act = False toujours)

### Obsidure

- Coût moyen par patch Lean
- Coût moyen par run Lean
- Coût moyen par réparation
- Coût moyen par audit ciblé
- Retries évités
- Faux FAIL détectés
- Preuve/replay disponible
- Coût évité face à un agent code externe (DCA_AGENTIC)

---

## 12. DCA — Domain Cost Advantage (V0.1)

`DCA = baseline_cost / obsidia_cost`

Deux baselines de référence :
- `DCA_API_NORMAL` : vs BT_API_NORMAL (25 000 EUR / 1M) — comparaison API standard
- `DCA_AGENTIC`    : vs BT_AGENTIC (160 000 EUR / 1M) — comparaison agent externe

| Domaine | Coût Obsidia EUR/1M | DCA_API_NORMAL | DCA_AGENTIC |
|---|---|---|---|
| Brody | 0.20 | 125 000x | 800 000x |
| Bank | 0.70 | ~35 714x | ~228 571x |
| Trading | 0.84 | ~29 762x | ~190 476x |
| GPS/Aviation | 0.91 | ~27 473x | ~175 824x |
| Obsidure | 23.92 | ~1 045x | ~6 690x |

Le DCA est calculé par `apps/obsidia_api/inference_economy/domain_metrics.py::compute_dca()` et agrégé dans `summarize_domain_metrics()`.
