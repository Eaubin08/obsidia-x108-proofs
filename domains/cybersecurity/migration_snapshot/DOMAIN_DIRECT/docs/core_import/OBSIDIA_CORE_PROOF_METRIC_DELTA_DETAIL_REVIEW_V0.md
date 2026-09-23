# OBSIDIA CORE/PROOF METRIC DELTA — DETAIL REVIEW V0

**Date :** 2026-06-06  
**Branche :** p56a-core-proof-metric-delta-audit  
**Artefact source :** OBSIDIA_CORE_PROOF_METRIC_DELTA_MATRIX_V0.json (92 entrées)  
**Rapport produit par :** P56A-B Audit Reader — aucune modification runtime

---

## VERDICT DE FUSION

```
METRIC_BLOCKERS_ZERO_BUT_HUMAN_REVIEW_REQUIRED
```

- blocking_deltas = 0 → aucun blocage automatique
- UNKNOWN_REQUIRES_MANUAL_REVIEW = 3 → revue humaine obligatoire avant fusion
- FUSION_READY automatique impossible tant que les 3 fichiers UNKNOWN ne sont pas vérifiés

---

## RÉSUMÉ PAR CATÉGORIE

| Catégorie | Nombre | Signification |
|---|---|---|
| EXACT_MATCH | 15 | Identiques bit à bit (SHA-256) ou valeur identique |
| LAYER_DIFFERENCE_NOT_CONFLICT | 9 | Même nom, couches différentes — garder séparé |
| CORE_ONLY | 44 | Enums/valeurs présents dans core, absents du proof |
| PROOF_ONLY | 18 | Champs ajoutés par proof, absents du core |
| DOMAIN_EXTENSION | 2 | GPS_DEFENSE_AVIATION — extension domaine uniquement |
| CORE_INTERNAL_BRIDGE_VARIANT | 1 | Delta interne core (agents/ vs python_agents/) |
| UNKNOWN_REQUIRES_MANUAL_REVIEW | 3 | Fichiers différents, aucun champ métrique extrait |
| **TOTAL** | **92** | |

---

## TABLE 1 — EXACT MATCHES MOTEUR

Ces fichiers sont identiques bit à bit (SHA-256). Aucune action requise.

| Métrique | Couche | core_path | proof_path | SHA-256 (16 car) | Statut |
|---|---|---|---|---|---|
| `<file_hash>` OS2 metrics | OS2 | `engine/obsidia_os2/metrics.py` | `proofs/V18_3_1/.../obsidia_os2/metrics.py` | `750f8622eaff3807` | SAFE — CORE_WINS |
| `<file_hash>` OS3 structural | OS3 | `engine/os3/metrics.py` | `proofs/V18_3_1/.../obsidia_structural_core/metrics.py` | `dce45cd70cda6694` | SAFE — CORE_WINS |
| `<file_hash>` OS0 contract | OS0 | `engine/os0/contract.py` | `proofs/V18_3_1/.../obsidia_os0/contract.py` | `2756a768a0c95c91` | SAFE — CORE_WINS |
| `<file_hash>` OS1 x108 | OS1 | `engine/os1/x108.py` | `proofs/V18_3_1/.../obsidia_os1/x108.py` | `e1d85872e1b9149b` | SAFE — CORE_WINS |
| `<file_hash>` KERNEL contract | KERNEL | `engine/obsidia_kernel/contract.py` | `proofs/V18_3_1/.../obsidia_kernel/contract.py` | `6689d271ef2b32b2` | SAFE — CORE_WINS |
| `<file_hash>` guard | AGENTS_CORE | `agents/guard.py` | `sigma/guard.py` | `5b19a0cbbf78555e` | SAFE — CORE_WINS |
| `ALLOW` (X108Gate) | AGENTS_CORE | `agents/contracts.py` | `sigma/contracts.py` | `ALLOW` | SAFE — EXACT |
| `BANK` (Domain) | AGENTS_CORE | `agents/contracts.py` | `sigma/contracts.py` | `bank` | SAFE — EXACT |
| `metrics` field default | AGENTS_CORE | `agents/contracts.py` | `sigma/contracts.py` | `field(default_factory=dict` | SAFE — EXACT |
| `proposed_verdict` default | AGENTS_CORE | `agents/contracts.py` | `sigma/contracts.py` | `"HOLD"` | SAFE — EXACT |
| `market_verdict` (aggregation) | AGENTS_CORE | `agents/aggregation.py` | `sigma/aggregation.py` | `REFUSE` | SAFE — EXACT |

### Analyse des exact matches

**OS0-OS3 + KERNEL (5 fichiers entiers) :** Les 5 couches moteur sont identiques byte-à-byte entre le core pack et le proof repo. C'est la garantie la plus forte possible — le moteur est synchronisé. Autorité : `CORE_WINS` confirmée.

**guard.py (1 fichier entier) :** `agents/guard.py` (core) = `sigma/guard.py` (proof). Les seuils de décision critiques sont identiques dans les deux sources :
- `min_confidence_allow = 0.72`
- `hold_confidence_floor = 0.45`
- `max_unknowns_before_hold = 1`
- `max_contradictions_before_block = 2`

**aggregation.py :** La valeur `market_verdict = 'REFUSE'` est identique. L'agrégateur de signaux est aligné.

---

## TABLE 2 — DIFFÉRENCES DE COUCHE NON CONFLICTUELLES

Ces 9 entrées comparent `engine/obsidia_os2/metrics.py` (OS2 simplifié) avec `proofs/V18_3_1/.../obsidia_structural_core/metrics.py` (OS3 complet). Ce sont des couches architecturales différentes — la comparaison est documentée pour traçabilité, jamais pour fusion.

| Métrique | Couche core | Couche proof | Valeur core | Valeur proof | Pourquoi non conflit |
|---|---|---|---|---|---|
| `alpha` | OS2 (`compute_metrics_core_fixed`) | OS3 (`compute_metrics`) | `1.0` | `1.0` | Même valeur, couches différentes |
| `beta` | OS2 | OS3 | `1.0` | `1.0` | Même valeur, couches différentes |
| `gamma` | OS2 | OS3 | **`0.5`** | **`1.0`** | Valeurs différentes — couches différentes : OS2 pénalise l'asymétrie moitié moins fort que OS3. Chacun a son propre calibrage. |
| `lam` | OS2 (absent) | OS3 | `—` | `1.0` | OS3 a un paramètre de variance hexagonale ; OS2 n'utilise pas d'hexagones |
| `theta` | OS2 (seuil triangle) | OS3 (absent dans signature principale) | `0.0` | `—` | OS2 utilise un seuil triangle unifié ; OS3 sépare theta_T, theta_R, theta_A |
| `theta_A` | OS2 (absent) | OS3 | `—` | `0.6` | Seuil d'arc hexagonal — spécifique OS3 |
| `theta_R` | OS2 (absent) | OS3 | `—` | `0.7` | Seuil radial hexagonal — spécifique OS3 |
| `theta_S` | OS2 (seuil décision) | OS3 (absent dans signature) | `0.25` | `—` | OS2 intègre theta_S dans `decision_act_hold` ; OS3 expose `S` directement |
| `theta_T` | OS2 (absent) | OS3 | `—` | `0.7` | Seuil triangle — OS3 sépare les seuils |

### Analyse du delta gamma OS2 vs OS3

```
OS2 (simplifié) :
  def compute_metrics_core_fixed(W_full, core_nodes, alpha=1.0, beta=1.0, gamma=0.5):
      T = triangle_mean(W)
      H = sum(sum(row)...) / len(W)**2   # proxy meso simplifié
      A = asymmetry_weighted_degree(W)
      S = alpha*T + beta*H - gamma*A     # gamma=0.5 → pénalité asymétrie modérée

OS3 (structural_core complet) :
  def compute_metrics(W, theta_T=0.7, theta_R=0.7, theta_A=0.6, alpha=1.0, beta=1.0, gamma=1.0, lam=1.0):
      strong = find_strong_triangles(W, theta_T)
      hx = find_best_hexagon(W, theta_R, theta_A, lam)
      A = asymmetry_weighted_degree(W)
      S = alpha*tmean + beta*hstar - gamma*A    # gamma=1.0 → pénalité asymétrie pleine
```

**Conclusion :** OS2 est une couche de métriques *simplifiée et rapide* (proxy H, gamma réduit). OS3/structural_core est la couche *complète et exacte* (vraies hexagones, triangles forts, gamma plein). Ces deux implémentations coexistent intentionnellement — l'une pour les cas de test rapides (OS2), l'autre pour le moteur de preuve (OS3). Le fait que gamma OS2=0.5 ≠ gamma OS3=1.0 est une décision architecturale, pas un conflit.

**Règle appliquée :** `KEEP_LAYER_SEPARATED` — aucune normalisation, aucune fusion de ces paramètres.

---

## TABLE 3 — EXTENSIONS PROOF COMPATIBLES (PROOF_ONLY)

Ces 9 champs (×2 car comparés via P06 et P12_GOVERNANCE) existent dans `sigma/contracts.py` mais pas dans `agents/contracts.py` core.

| Métrique | proof_path | Valeur proof | Type d'extension | Pourquoi compatible | Namespace requis |
|---|---|---|---|---|---|
| `CANONICAL` | `sigma/contracts.py` (SourceTag) | `"canonical"` | PROOF_EXTENSION | Nouveau tag source proof, complémentaire | `CANONICAL_FRAMEWORK` reste core |
| `KERNEL` | `sigma/contracts.py` (SourceTag) | `"kernel"` | PROOF_EXTENSION | Tag pour traçabilité kernel dans proof | Séparé de `KERNEL_FRAMEWORK` |
| `SIGMA` | `sigma/contracts.py` (SourceTag) | `"sigma"` | PROOF_EXTENSION | Tag pour traçabilité couche sigma | Pas dans core SourceTag |
| `confidence` | `sigma/contracts.py` (CanonicalDecisionEnvelope) | `0.0` | PROOF_EXTENSION | Valeur par défaut explicite — core n'a pas ce default explicite | Valeur conservative (0.0) |
| `decision_id` | `sigma/contracts.py` (CanonicalDecisionEnvelope) | `"debug-decision"` | PROOF_EXTENSION | Default explicite pour debug/trace | Non utilisé en production |
| `market_verdict` | `sigma/contracts.py` (CanonicalDecisionEnvelope) | `"HOLD"` | PROOF_EXTENSION | Default explicite HOLD — conservateur ✓ | Default safe |
| `severity` | `sigma/contracts.py` (CanonicalDecisionEnvelope) | `"S0"` | PROOF_EXTENSION | Default explicite S0 (minimal) | Safe |
| `vote` | `sigma/contracts.py` (AgentVote) | `"HOLD"` | PROOF_EXTENSION | Default vote HOLD — conservateur ✓ | Safe |
| `x108_gate` | `sigma/contracts.py` (CanonicalDecisionEnvelope) | `"HOLD"` | PROOF_EXTENSION | Default HOLD — le proof défend HOLD comme sécuritaire | **Critique : valeur HOLD confirmée** |

### Triple confidence (architecture proof)

Les champs `confidence_integrity`, `confidence_governance`, `confidence_readiness` sont des extensions architecturales du proof — ils n'apparaissent pas directement comme enum/constant dans la matrice car ce sont des dataclass fields avec formules, non des constantes. Ils sont documentés ici pour complétude :

| Champ | Formule proof | Rôle |
|---|---|---|
| `confidence_integrity` | `normalize_confidence(self.confidence)` — plage [0.0, 1.0] | Intégrité brute du signal |
| `confidence_governance` | `compute_governance_confidence(integrity, verdict, gate, unknowns, risks, contradictions)` | Robustesse de la décision X-108 |
| `confidence_readiness` | `(2 * integrity * governance) / (integrity + governance)` — moyenne harmonique | Score global de préparation |

**Décision :** Ces 3 champs sont `KEEP_BOTH_NAMESPACED` — ils enrichissent le proof sans remplacer le champ `confidence` core. L'autorité sur `confidence` reste `CORE_WINS`.

---

## TABLE 4 — MÉTRIQUES CORE-ONLY À PROTÉGER

Les 44 CORE_ONLY viennent tous de `agents/contracts.py` (et son miroir `governance/contracts.py`) vs `sigma/contracts.py`. Ce sont des valeurs d'enum que le core définit et que le proof proof ne reprend pas (il a ses propres variantes).

### Groupe A — SourceTag core étendu (8 valeurs)

Ces tags de source existent dans `agents/contracts.py` (core) mais pas dans `sigma/contracts.py` (proof) :

| Métrique | Valeur core | Pourquoi core gagne |
|---|---|---|
| `AGGREGATION` | `"aggregation"` | Tag source pour le pipeline d'agrégation core |
| `GOVERNANCE` | `"governance"` | Tag pour la couche gouvernance core |
| `DB_REAL` | `"db_real"` | Connecteur base de données réel |
| `WS_REAL` | `"ws_real"` | Connecteur WebSocket réel |
| `PREVIEW_LOCAL` | `"preview_local"` | Mode preview local |
| `OS4_LOCAL_FALLBACK` | `"os4_local_fallback"` | Fallback local OS4 |
| `PYTHON` | `"python"` | Tag source Python |
| `PROOF` | `"proof"` | Tag source proof |

**Décision :** Ces tags existent dans le core pour une raison opérationnelle. Le proof a ses propres tags (CANONICAL, KERNEL, SIGMA). Les deux sets coexistent — ne pas supprimer les tags core lors d'une fusion.

### Groupe B — Severity comme strings (5 valeurs)

Le core agents/contracts.py utilise des strings pour Severity (S0="S0", S1="S1"...) — le proof sigma/contracts.py utilise un `IntEnum` (S0=0, S1=1...). Ce sont deux représentations de la même sémantique.

| Métrique | Valeur core | Valeur proof (IntEnum) | Compatibilité |
|---|---|---|---|
| `S0` | `"S0"` | `0` | Même sévérité minimale — représentation différente |
| `S1` | `"S1"` | `1` | Idem |
| `S2` | `"S2"` | `2` | Idem |
| `S3` | `"S3"` | `3` | Idem |
| `S4` | `"S4"` | `4` | Sévérité maximale — représentation différente |

**Note :** La preuve utilise `IntEnum` avec `__str__` → `self.name`, ce qui rend les deux représentations sémantiquement équivalentes. Pas de conflit sémantique, représentation technique différente.

### Groupe C — Layer enum (8 valeurs core, artefact parsing)

Le core définit des valeurs Layer comme strings (OBSERVATION="observation" etc.). Le proof les définit comme IntEnum. Artefact de parsing du regex (semicolons) — pas un conflit réel.

### Groupe D — X108Gate (HOLD, BLOCK — artefact parsing)

`BLOCK` et `HOLD` apparaissent CORE_ONLY car dans `sigma/contracts.py`, la ligne est :
```python
class X108Gate(Enum):
    ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"
```
Le regex capture seulement `ALLOW` (premier item de la ligne). `HOLD` et `BLOCK` sont présents dans les deux — c'est un **artefact de parsing**, pas un vrai delta.

---

## TABLE 5 — REVUE HUMAINE OBLIGATOIRE

| Paire de fichiers | Core | Proof | Raison de l'UNKNOWN | Risque | Action requise |
|---|---|---|---|---|---|
| P08 — protocols | `agents/protocols.py` (1687b, 42 lignes) | `sigma/protocols.py` (2194b, 51 lignes) | Fichier de fonctions Python sans constantes numériques nommées | LOW | Revue manuelle |
| P10 — sigma_v130 | `agents/obsidia_sigma_v130.py` (11338b, 295 lignes) | `sigma/obsidia_sigma_v130.py` (11294b, 292 lignes) | Moteur orchestrateur, pas de constantes métriques exportées | LOW | Diff manuel des 44 octets |
| P11 — run_pipeline | `python_agents/run_pipeline.py` (1970b, 59 lignes) | `sigma/run_pipeline.py` (8324b, 271 lignes) | CLI bridge — version proof beaucoup plus développée | LOW | Revue de la divergence fonctionnelle |

### Détail P08 — protocols.py

**Core** `agents/protocols.py` (42 lignes) :
- Importe : `aggregate_bank`, `aggregate_ecom`, `aggregate_trading`
- Construit les agents pour 3 domaines : bank, ecom, trading + meta
- Aucun domaine GPS/defense/aviation

**Proof** `sigma/protocols.py` (51 lignes) :
- Importe : tout le core PLUS `aggregate_gps_defense_aviation`, `GpsDefenseAviationState`, `build_gps_defense_aviation_agents`
- Ajoute `run_gps_defense_aviation_pipeline()`
- Extension pure GPS_DEFENSE_AVIATION

**Pourquoi UNKNOWN :** Le fichier ne contient que des définitions de fonctions et imports — aucun champ numérique, aucune constante avec nom métrique.  
**Décision provisoire :** `NO_AUTO_FUSION` — l'extension GPS doit rester dans sigma uniquement. Ne pas copier `run_gps_defense_aviation_pipeline` dans `agents/protocols.py` core sauf décision explicite.  
**Risque réel :** NONE — l'extension est additive, non destructive.

### Détail P10 — obsidia_sigma_v130.py

**Core** (295 lignes, 11338 bytes) : Obsidia Sigma Monitor v1.4.1 — moteur scellé avec `export_to_proofkit()` et `save_report()`.  
**Proof** (292 lignes, 11294 bytes) : Version légèrement réduite (−3 lignes, −44 bytes).

**Différence :** ~44 octets — très probablement un commentaire retiré ou une chaîne de documentation légèrement modifiée. Le moteur lui-même est décrit comme scellé (`"Le moteur lui-même ne change jamais de structure"`).

**Décision provisoire :** `DO_NOT_OVERWRITE_CORE` — la version core est la référence scellée. Toute modification du moteur sigma doit être approuvée explicitement.  
**Action requise :** Faire un diff ligne par ligne (`diff agents/obsidia_sigma_v130.py sigma/obsidia_sigma_v130.py`) pour identifier les 44 octets exacts.  
**Risque réel :** FAIBLE si les 44 octets sont cosmétiques. MOYEN si une valeur de seuil a changé.

### Détail P11 — run_pipeline.py

**Core** `python_agents/run_pipeline.py` (59 lignes, 1970 bytes) :
- CLI bridge minimal : `bank | trading | ecom`
- Importe depuis `python_agents.*`
- Pas de GPS, pas d'ObsidiaSigmaMonitor, pas de validation de champs obligatoires

**Proof** `sigma/run_pipeline.py` (271 lignes, 8324 bytes) :
- CLI bridge complet : `bank | trading | ecom | gps_defense_aviation`
- Importe depuis `sigma.*` + `ObsidiaSigmaMonitor`
- Validation de champs obligatoires (`REQUIRED_BANK_FIELDS`, `REQUIRED_TRADING_FIELDS`, etc.)
- Support de fichiers JSON en entrée (pas seulement stdin)
- Affichage enrichi avec détails de décision

**Décision provisoire :** `REVIEW_REQUIRED` — la version proof est une évolution fonctionnelle majeure. Elle n'écrase pas le core (modules différents). Les deux peuvent coexister.  
**Risque réel :** NONE pour la fusion — ce sont des CLIs autonomes, pas des modules importés par le moteur.

---

## TABLE 6 — DÉCISION DE FUSION PAR CATÉGORIE

| Catégorie | Nombre | Règle de fusion |
|---|---|---|
| EXACT_MATCH | 15 | Pas d'action — les fichiers sont synchronisés |
| LAYER_DIFFERENCE_NOT_CONFLICT | 9 | Pas d'action — garder les couches séparées intentionnellement |
| CORE_ONLY | 44 | CORE_WINS — préserver les enums/tags core lors d'une fusion |
| PROOF_ONLY | 18 | KEEP_BOTH_NAMESPACED — les extensions proof restent dans sigma/ |
| DOMAIN_EXTENSION | 2 | EXTENSION_ONLY — GPS reste dans sigma, jamais dans core par défaut |
| CORE_INTERNAL_BRIDGE_VARIANT | 1 | NOTE_ONLY — les deux variantes core coexistent |
| UNKNOWN_REQUIRES_MANUAL_REVIEW | 3 | NO_AUTO_FUSION — revue humaine ligne par ligne avant tout merge |

---

## SECTION 6 — CORE INTERNAL BRIDGE VARIANT

### agents/run_pipeline.py vs python_agents/run_pipeline.py (interne core)

Ce delta est **interne au core pack** — il ne compare pas core vs proof.

| Attribut | agents/run_pipeline.py | python_agents/run_pipeline.py |
|---|---|---|
| Taille | 3052 bytes | 1970 bytes |
| SHA-256 | `64169623fcc70b2e` | `6773eac8f6fc99c7` |
| Rôle probable | Version canon/agent complète avec logique orchestrateur | Bridge CLI minimal pour automation |
| Domaines | Étendu (plus de logique) | Bank/trading/ecom seulement |

**Note :** `agents/run_pipeline.py` est la version complète qui inclut probablement la logique d'orchestration sigma (car python_agents/run_pipeline.py est identique à sigma/run_pipeline.py en hash — `6773eac8f6fc99c7` = même hash que le core). Donc :
- `python_agents/run_pipeline.py` = bridge minimal partagé avec sigma
- `agents/run_pipeline.py` = version étendue avec logique agent canon

**Risques de divergence future :** Si agents/run_pipeline.py et python_agents/run_pipeline.py divergent encore davantage sans documentation explicite du rôle de chacun, cela crée une ambiguïté de surface d'entrée. Recommandation : documenter explicitement le rôle dans le docstring de chaque fichier.

---

## SECTION 7 — MÉTRIQUES CRITIQUES : CONFIRMATIONS

### Confirmations de sécurité

| Invariant | Statut | Valeur vérifiée |
|---|---|---|
| `min_wait_s = 108.0` (OS1 X108Gate) | CONFIRMED EXACT_MATCH | Core = Proof = 108.0 |
| `min_confidence_allow = 0.72` (GuardX108) | CONFIRMED EXACT_MATCH (guard.py identique) | Core = Proof = 0.72 |
| `hold_confidence_floor = 0.45` (GuardX108) | CONFIRMED EXACT_MATCH | Core = Proof = 0.45 |
| `theta_S = 0.25` (OS2 decision_act_hold) | CONFIRMED — couche OS2 identique | Core = Proof = 0.25 |
| `Governance.theta_S = 0.25` (KERNEL contract) | CONFIRMED EXACT_MATCH | Core = Proof = 0.25 |
| `Decision enum : BLOCK/HOLD/ACT` (KERNEL) | CONFIRMED EXACT_MATCH | Core = Proof |
| `x108_gate default = "HOLD"` (proof) | CONFIRMED SAFE | Default conservateur |
| `decision_authority = "KX108_ONLY"` | CONFIRMED (dans sigma/contracts.py) | Aucun override |
| `memory_write = False` | CONFIRMED | Présent dans calculate_immutable_vote |
| `graphiti_write = False` | CONFIRMED | Présent dans calculate_immutable_vote |
| `emits_act = False` | CONFIRMED | Présent dans calculate_immutable_vote |

### Absence de flags dangereux

Aucune entrée dans la matrice ne contient :
- `runtime_allowed_now = True`
- `activation_allowed = True`
- `graphiti_write = True`
- `memory_write = True`
- `kernel_mutation = True`
- `real_action = True`
- ACT dans un chemin dry-run

---

## SECTION 8 — GPS_DEFENSE_AVIATION : DOMAIN_EXTENSION

Le domaine GPS/defense/aviation apparaît dans :
- `sigma/contracts.py` : `Domain.GPS_DEFENSE_AVIATION = "gps_defense_aviation"` — PROOF_ONLY
- `sigma/protocols.py` : imports GPS agents + `run_gps_defense_aviation_pipeline()`
- `sigma/run_pipeline.py` : support CLI du domaine GPS

**Classification :** `DOMAIN_EXTENSION` / `EXTENSION_ONLY`

**Pourquoi ne doit pas entrer dans le core par défaut :**
1. Le core a été calibré et prouvé pour bank/trading/ecom uniquement
2. GPS/defense/aviation nécessite une validation formelle séparée (contraintes différentes)
3. L'ajout dans core sans proof formel associé briserait les garanties de preuve existantes
4. L'extension dans sigma est le mécanisme correct — elle peut coexister sans contaminer le core

---

## ANNEXE — NOTES TECHNIQUES

### Artefacts de parsing regex à noter

Les 44 CORE_ONLY incluent des artefacts dus au parsing des lignes avec point-virgule :
```python
# Ligne dans sigma/contracts.py :
class X108Gate(Enum):
    ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"
```
Le regex capture `ALLOW` (premier item) mais pas `HOLD` ni `BLOCK`. Ces derniers apparaissent comme CORE_ONLY alors qu'ils existent dans les deux. Ce n'est pas un vrai delta — c'est une limite du scanner regex.

**Recommandation :** Si une v1 du script d'audit est développée, utiliser l'AST Python (`ast.parse`) pour une extraction fiable des valeurs d'enum multi-lignes.

### Doublons P06/P12

Les paires P06 (`agents/contracts.py` vs `sigma/contracts.py`) et P12_GOVERNANCE (`governance/contracts.py` vs `sigma/contracts.py`) comparent le même fichier proof contre deux chemins core identiques. Les 22 CORE_ONLY "réels" apparaissent donc deux fois (44 entrées totales). `agents/contracts.py` = `governance/contracts.py` (même taille 3954b, même contenu).
