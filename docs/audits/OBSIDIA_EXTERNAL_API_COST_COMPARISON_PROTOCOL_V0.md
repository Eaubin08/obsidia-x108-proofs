# OBSIDIA EXTERNAL API COST COMPARISON — PROTOCOL V0

**Statut :** Protocole préparatoire — aucun appel réseau, aucune clé API
**Date :** 2026-07-01
**Périmètre :** Définir le protocole de benchmark réel futur entre Obsidia et des APIs externes
**Autorité :** Kernel X-108 (KX108_ONLY) — OIE reste non souverain

---

## 1. Principe

> Même entrée. Même tâche. Même contrainte de sortie. Même mesure.

Un benchmark est valide uniquement si les deux systèmes comparés reçoivent exactement la même entrée, sont soumis aux mêmes contraintes de sortie, et sont mesurés avec les mêmes métriques. Ce protocole définit les règles de comparaison avant toute intégration d'API externe.

**Ce document ne contient aucune clé API, aucun appel réseau, aucune dépendance externe.**

---

## 2. Systèmes comparés

| Identifiant | Description |
|---|---|
| `OBSIDIA_LOCAL` | Obsidia tournant en local / edge / PC |
| `EXT_LLM_SIMPLE` | API LLM simple (ex: endpoint chat basique) |
| `EXT_LLM_NORMAL` | API LLM normale (ex: endpoint avec context et tools) |
| `EXT_AGENTIC` | Workflow agentique externe multi-step |
| `EXT_CODE_AGENT` | Agent code externe (pour comparaison Obsidure) |
| `EXT_DOMAIN_LLM` | Analyse domaine LLM externe (Bank / Trading / GPS) |

---

## 3. Métriques à mesurer pour chaque run

Pour chaque run des deux systèmes :

### Coût
- `api_cost_eur` : coût API réel facturé (EUR)
- `tokens_input` : nombre de tokens en entrée
- `tokens_output` : nombre de tokens en sortie
- `api_calls_count` : nombre d'appels API effectués
- `tools_called` : liste des outils appelés
- `retries_count` : nombre de retries nécessaires

### Performance
- `latency_ms` : latence totale (ms)
- `latency_p50_ms` : latence médiane
- `latency_p99_ms` : latence p99

### Qualité
- `output_quality_score` : score de qualité de sortie (0-1, défini par domaine)
- `errors_count` : nombre d'erreurs
- `human_correction_needed` : correction humaine nécessaire (bool)
- `output_matches_spec` : la sortie respecte la contrainte de sortie (bool)

### Traçabilité
- `proof_or_replay_available` : preuve ou replay disponible (bool)
- `decision_auditable` : décision auditable après coup (bool)

### Comparaison Obsidia
- `obsidia_equivalent_cost_eur_per_1m` : coût Obsidia équivalent (EUR / 1M actions)
- `savings_ratio` : ratio d'économie (ext_cost / obsidia_cost)
- `avoided_cost_eur_per_1m` : coût évité (EUR / 1M)
- `inference_avoided` : inférence évitée (modules skippés)

---

## 4. Familles de tests

### 4.1 Fast Path vs LLM simple

**Tâche :** Dispatcher une requête sans raisonnement
**Obsidia :** Fast Path (0.0015 EUR / 1M)
**Externe :** EXT_LLM_SIMPLE
**Contrainte de sortie :** route correcte identifiée en < 5ms
**Baseline attendue :** BT_API_SIMPLE (5 500 EUR / 1M)

```json
{
  "test_family": "fast_path_vs_llm_simple",
  "input_spec": "single dispatch request, no reasoning required",
  "output_spec": "correct_route: string",
  "latency_constraint_ms": 5,
  "obsidia_cost_eur_per_1m": 0.0015,
  "expected_external_baseline": "BT_API_SIMPLE"
}
```

### 4.2 Brody vs assistant LLM

**Tâche :** Répondre à une question conversationnelle avec contexte utilisateur
**Obsidia :** Brody chat (0.20 EUR / 1M)
**Externe :** EXT_LLM_NORMAL
**Contrainte de sortie :** réponse cohérente avec le contexte, non souveraine
**Baseline attendue :** BT_API_NORMAL (25 000 EUR / 1M)

```json
{
  "test_family": "brody_vs_assistant_llm",
  "input_spec": "conversational query with user context",
  "output_spec": "coherent_response: string, sovereignty_check: false",
  "obsidia_cost_eur_per_1m": 0.20,
  "expected_external_baseline": "BT_API_NORMAL"
}
```

### 4.3 Bank vs analyse LLM domaine

**Tâche :** Décision de virement avec contraintes conformité
**Obsidia :** Bank connector (0.70 EUR / 1M)
**Externe :** EXT_DOMAIN_LLM
**Contrainte de sortie :** ALLOW / HOLD / BLOCK + justification auditable
**Baseline attendue :** BT_API_NORMAL (25 000 EUR / 1M)

```json
{
  "test_family": "bank_vs_domain_llm",
  "input_spec": "wire_transfer_request with compliance_context",
  "output_spec": "decision: ALLOW|HOLD|BLOCK, justification: string, auditable: true",
  "obsidia_cost_eur_per_1m": 0.70,
  "expected_external_baseline": "BT_API_NORMAL"
}
```

### 4.4 Trading vs analyse LLM domaine

**Tâche :** Traitement d'un signal de marché avec détection contradiction
**Obsidia :** Trading connector (0.84 EUR / 1M)
**Externe :** EXT_DOMAIN_LLM
**Contrainte de sortie :** signal validé ou HOLD risque + contradictions identifiées
**Baseline attendue :** BT_API_NORMAL (25 000 EUR / 1M)

```json
{
  "test_family": "trading_vs_domain_llm",
  "input_spec": "market_signal with risk_context",
  "output_spec": "validated_signal: bool, contradictions: list, hold_reason: string|null",
  "obsidia_cost_eur_per_1m": 0.84,
  "expected_external_baseline": "BT_API_NORMAL"
}
```

### 4.5 GPS/Aviation vs analyse LLM terrain

**Tâche :** Validation d'un signal terrain avec décision HOLD/BLOCK sécurité
**Obsidia :** Aviation connector (0.91 EUR / 1M)
**Externe :** EXT_DOMAIN_LLM
**Contrainte de sortie :** route admissible ou BLOCK sécurité + anomalies identifiées
**Baseline attendue :** BT_API_NORMAL (25 000 EUR / 1M)

```json
{
  "test_family": "gps_vs_domain_llm",
  "input_spec": "terrain_signal with safety_context",
  "output_spec": "route_admissible: bool, anomalies: list, safety_decision: ALLOW|HOLD|BLOCK",
  "obsidia_cost_eur_per_1m": 0.91,
  "expected_external_baseline": "BT_API_NORMAL"
}
```

### 4.6 Obsidure vs agent code externe

**Tâche :** Générer et vérifier un patch Lean ciblé
**Obsidia :** Obsidure Lean ciblé (23.92 EUR / 1M)
**Externe :** EXT_CODE_AGENT
**Contrainte de sortie :** patch syntaxiquement valide + preuve Lean disponible
**Baseline attendue :** BT_AGENTIC (160 000 EUR / 1M)

```json
{
  "test_family": "obsidure_vs_code_agent",
  "input_spec": "lean_proof_target with repair_context",
  "output_spec": "valid_patch: bool, lean_proof_available: bool, retries: int",
  "obsidia_cost_eur_per_1m": 23.92,
  "expected_external_baseline": "BT_AGENTIC"
}
```

### 4.7 Lean/proof vs raisonnement LLM long

**Tâche :** Vérifier un invariant formel
**Obsidia :** Lean canon check (13.29 EUR / 1M)
**Externe :** EXT_LLM_NORMAL (raisonnement long)
**Contrainte de sortie :** vérification formelle ou FAIL attesté
**Baseline attendue :** BT_API_NORMAL (25 000 EUR / 1M)

```json
{
  "test_family": "lean_check_vs_llm_reasoning",
  "input_spec": "formal_invariant_statement",
  "output_spec": "verified: bool, proof_hash: string|null, formal: true",
  "obsidia_cost_eur_per_1m": 13.29,
  "expected_external_baseline": "BT_API_NORMAL"
}
```

---

## 5. Structure d'un résultat de benchmark comparatif

```json
{
  "benchmark_run_id": "<uuid>",
  "test_family": "<string>",
  "timestamp": "<ISO8601>",
  "obsidia": {
    "cost_eur_per_1m": 0.70,
    "latency_ms": 42.0,
    "output_quality_score": 0.97,
    "errors_count": 0,
    "human_correction_needed": false,
    "proof_or_replay_available": true,
    "tokens_input": null,
    "tokens_output": null,
    "api_calls_count": 0,
    "retries_count": 0
  },
  "external": {
    "system_id": "EXT_LLM_NORMAL",
    "cost_eur_per_1m": 25000.0,
    "latency_ms": null,
    "output_quality_score": null,
    "errors_count": null,
    "human_correction_needed": null,
    "proof_or_replay_available": false,
    "tokens_input": null,
    "tokens_output": null,
    "api_calls_count": null,
    "retries_count": null
  },
  "comparison": {
    "savings_ratio": 35714.29,
    "avoided_cost_eur_per_1m": 24999.30,
    "inference_avoided": ["lean_checker"],
    "quality_delta": null,
    "latency_delta_ms": null
  }
}
```

---

## 6. Contraintes d'intégration (futures)

Quand un vrai benchmark réel sera réalisé :

- Ne stocker aucune clé API dans le repo.
- Utiliser des variables d'environnement (`EXT_API_KEY_*`).
- Ne jamais logguer les clés ou les réponses brutes contenant des données sensibles.
- Limiter les appels à un budget fixe par run (`MAX_TOKENS_PER_RUN`, `MAX_COST_PER_RUN_EUR`).
- Toujours produire un `CostReceipt` OIE pour chaque run Obsidia.
- Le benchmark comparatif est lui-même non souverain : il ne prend aucune décision, il mesure.

---

## 7. Fichiers à créer lors de l'intégration réelle

```
scripts/performance/
  run_external_api_benchmark_<family>_v1.py    # un script par famille
  external_api_benchmark_results_<family>.json # résultats par famille

tests/
  test_external_api_benchmark_protocol.py      # vérifie la structure des résultats

docs/audits/
  OBSIDIA_EXTERNAL_API_BENCHMARK_RESULTS_V1.md # rapport de résultats réels
```

---

## 8. Gouvernance du protocole

- Ce document est **non souverain** : il définit un protocole, il n'autorise rien.
- Toute exécution réelle doit être approuvée explicitement (clé API, budget, domaine).
- Le kernel X-108 (KX108_ONLY) reste l'unique autorité de décision sur les actions.
- Les résultats de benchmark ne peuvent pas déclencher d'action automatique.
- `emits_act = False` pour tout composant OIE, y compris le benchmark comparatif.
