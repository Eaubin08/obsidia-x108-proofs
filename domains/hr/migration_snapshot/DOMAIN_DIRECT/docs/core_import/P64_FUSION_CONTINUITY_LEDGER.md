# P64 — Fusion Continuity Ledger

**Status :** P64_FUSION_CONTINUITY_LEDGER_READY
**Mode :** LEDGER_ONLY — zéro import, zéro modification
**Branche :** p64-fusion-continuity-ledger
**Date :** 2026-06-07

---

## 1. Phrase verrou

> **Core apporte la rigueur et la matière brute.**
> **Proof porte déjà la gouvernance avancée.**
> **La fusion garde le supérieur et adapte le reste.**

Règle : pour chaque surface, proof gagne si déjà en place. Core contribue uniquement si la surface est absente, complémentaire ou adaptable sans risque.

---

## 2. Décisions déjà validées

### P56 — Core/Proof Metric Reconciliation (LOCKED)

| Décision | Valeur | Autorité |
|---|---|---|
| OS2 gamma proof | **1.0** (P56B strengthening) | PROOF_WINS_BY_OS3_AUTHORITY |
| OS2 gamma core | 0.5 (historique, jamais réimporter) | SUPERSEDED |
| OS3 gamma | **1.0** (confirmé inchangé) | CONFIRMED_UNCHANGED |
| Sigma post-Guard | **veto-only** (P56D) | LOCKED |
| Chaîne domaine | State→Agents→Aggregation→MetaAgents→GuardX108→CanonicalDecisionEnvelope | VALIDATED 4 domaines |
| sigma_config.json | SHA EXACT_MATCH core/proof — proof utilise sigma/sigma_config.json | DO_NOT_IMPORT agents/sigma_config.json |
| KX108_ONLY | decision_authority confirmé sigma/contracts.py L356 | LOCKED |
| emits_act | false systématique | LOCKED |
| runtime_allowed_now | false effectif (5 faux-positifs documentés P56E) | LOCKED |

### P57 — Core Machinery Inventory (DONE)

- 282 fichiers core inventoriés, zéro import.
- Chaque fichier : layer, family, role, import_candidate, runtime_candidate, proof_equivalent_path, sha256.

### P58 — Path-Aware Triage (DONE)

| Lot | Taille | Statut |
|---|---|---|
| SAFE_BATCH_1 | 10 | importé P59 |
| TEST_BATCH_2 | 32 | traité P60 |
| BUS_ADAPTER_BATCH | 4 | adapté P61 (partiel) |
| MANUAL_REVIEW_DEFERRED | 77 | classifié P62 |
| DO_NOT_TOUCH | 30 | bloqué définitif |
| PRIVATE_UI | 6 | exclu définitif |

### P59 — SAFE_BATCH_1 (DONE — 10 fichiers)

`generate_hashes`, `verify_hashes`, `anchor_merkle_root`, `calibrate_sigma`, `check_traces_x108`, `run_conformance`, `x108_trace_check`, `x108_vectors_check`, `verify_chain_anchor`, `verify_threat_model` → `scripts/`

### P60 — TEST_BATCH_2 (DONE — 27+4+1)

- 27 copiés, 4 déjà identiques (evidence CSVs = data/ CSVs), 1 bloqué SHA différent (test_agents_functional.py doublon).

### P61 — BUS_ADAPTER_BATCH (PARTIEL — 2/4)

- `bus/message.py` + `bus/router.py` : adaptés DRY_RUN_ONLY ✓
- `bus/__init__.py` : bloqué (proof supérieur)
- `bus/registry.py` : bloqué — import manquant `modules.os_trad.adapter` → **débloqué par P65**

### P62 — MANUAL_REVIEW_DEFERRED (DONE — 0 import)

| Décision | Nombre |
|---|---|
| BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW | 40 |
| DO_NOT_IMPORT | 20 |
| KEEP_PROOF_VERSION | 6 |
| IMPORT_DOC_ONLY | 5 |
| IMPORT_AFTER_ADAPTER | 3 |
| SAFE_READONLY_ADAPTER_CANDIDATE | 3 |

### P63 — Global Fusion Reality Audit (DONE — 8 surfaces)

- Sigma : complet, 58 fichiers P56B/P56E ✓
- Runtime wiring : complet, 49 fichiers ✓
- Routes API : 21 présentes ✓
- GPS defense aviation : 6 agents + 6 exemples + 3 tests + 2 connectors ✓
- Graphiti/memory : write=False systématique, isolés ✓
- Wording : 95% OK, 3 termes à réviser ✓
- Agents : sigma/ supérieur sur 5 fichiers P56B, 2 candidats d'import ✓
- Engine/runtime : 4 adapter candidates P62, 5 bloqués HIGH ✓

---

## 3. Matrice proof vs core

| Surface | Core apporte | Proof contient déjà | Décision | Prochain geste |
|---|---|---|---|---|
| **metrics** | OS2 gamma 0.5 (dépassé) | OS2=1.0, OS3=1.0, guard calibré, KX108_ONLY | KEEP_PROOF_VERSION | Surveillance seule |
| **sigma** | agents/* doublons pre-P56B | 58 fichiers P56B/P56E, 5 domaines, GPS intégré | KEEP_PROOF_VERSION | P67 extensions ciblées |
| **agents** | sigma_dashboard.py, indicators.py (absents proof) | prompts/*.md, registry.json, sigma/domains/* | IMPORT_SAFE 2 fichiers | P66 import ciblé |
| **engine/runtime** | engine_final, engine_runtime, kernel (live actif) | proofs/V18_3_1 (sealed), runtime_wiring (dry-run) | BLOCK + ADAPT 4 OS candidats | P65 (os0/os1/os3/os_trad), P68 (risk review) |
| **runtime_wiring** | Aucun équivalent core | 49 fichiers complets, dry-run, readonly, BLOCK>HOLD | KEEP_PROOF_VERSION | Aucune action |
| **routes API** | audit_log.py (comparer) + worm_uploader (DO_NOT_IMPORT) | 21 routes (readonly, dry-run, contrôlées) | KEEP_PROOF + IMPORT_AFTER_ADAPTER audit_log | P68 comparaison audit_log |
| **bus** | registry.py (bloqué — os_trad manquant) | message/router DRY_RUN_ONLY (P61), __init__.py proof supérieur | UNBLOCK via P65 | P65 → P61 registry.py débloqué |
| **GPS/aviation** | os0/os1/os3 SAFE_READONLY + os_trad IMPORT_AFTER | 6 agents, 6 exemples, 3 tests, 2 connectors terrain | ADAPT_READONLY + KEEP_PROOF | P65 + P69 |
| **graphiti/brody/memory** | worm_uploader (DO_NOT_IMPORT) | readonly proxy, write=False partout, isolation testée | KEEP_PROOF_VERSION | Surveillance |
| **canon wording** | Aucun (wording est proof-natif) | ~95% justifié — 3 termes à nuancer | PATCH_TARGETED_ONLY | P70 (3 termes) |
| **presentation docs** | Aucun (docs proof-natifs) | docs/demo/ mixte opérateur/investisseur | SEPARATE_PUBLIC_FROM_PROOF | P71 |
| **tests/tooling** | Déjà importés P59-P60 | 176 tests passants (P56E→P63) | KEEP_PROOF_VERSION | +tests par palier P65-P72 |

---

## 4. À ne pas oublier

1. **Ne pas écraser sigma avec core** — proof wins sur 5 fichiers P56B : `aggregation.py`, `contracts.py`, `guard.py`, `protocols.py`, `run_pipeline.py`
2. **Ne pas réintroduire le gamma OS2=0.5** — P56E locked, PROOF_WINS_BY_OS3_AUTHORITY, jamais régresser
3. **Ne pas importer `engine/obsidia_runtime/*` brut** — `engine_final.py`, `engine_runtime.py` activent un runtime live sans bornes
4. **Ne pas brancher ACT hors X108 final gate** — sigma post-Guard veto-only P56D, invariant verrouillé
5. **Ne pas mélanger PRIVATE_UI/Gemini avec proof** — 6 fichiers exclus définitifs P58
6. **Ne pas activer `graphiti_write` / `memory_write` / `neo4j_write`** — maintenir `False` systématique
7. **Ne pas traiter `docs/demo/F41`-series comme preuve technique** — narratif investisseur, séparer P71
8. **Ne pas faire passe wording globale violente** — 3 termes ciblés seulement P70
9. **Ne pas perdre GPS terrain** — `connectors/aviation_robo.py` + `periphery/adapters/gps_adapter.py` + sigma pipeline déjà connecté
10. **Ne pas oublier P61 `registry.py` bloqué** — débloqué uniquement via `engine/core_full/modules/os_trad/adapter.py` en P65
11. **Ne jamais stager `.claude/settings.json`** — exclu systématique
12. **Ne pas merger / rebase / squash** les branches P59-P64 sans instruction explicite
13. **Ne pas importer `engine/api_server/worm_uploader.py`** — DO_NOT_IMPORT définitif
14. **Ne pas importer `agents/sigma_config.json`** — SHA EXACT_MATCH proof/core, sigma utilise déjà `sigma/sigma_config.json`

---

## 5. Plan de reprise

### P65 — OS_ADAPTERS_TO_UNLOCK_BUS_REGISTRY `[PRIORITÉ 1]`

**But :** Adapter `engine/os0/determinism.py`, `engine/os1/parse_input.py`, `engine/os3/svg.py` (SAFE_READONLY_ADAPTER_CANDIDATE) et `engine/core_full/modules/os_trad/adapter.py` (IMPORT_AFTER_ADAPTER) pour débloquer `apps/obsidia_api/bus/registry.py`.

**Entrée :** P62 SAFE_READONLY_ADAPTER_CANDIDATE ×3 + IMPORT_AFTER_ADAPTER ×1
**Sortie :** 4 fichiers adaptés DRY_RUN_ONLY/READONLY + `registry.py` P61 débloqué
**Risque :** LOW-MEDIUM

---

### P66 — AGENTS_COMPLEMENTARY_RECONCILIATION `[PRIORITÉ 2]`

**But :** Importer `agents/sigma_dashboard.py` et `agents/utils/indicators.py` — aucun doublon dans proof, surface AUDIT_TOOLING.

**Entrée :** P63 core_candidates agents
**Sortie :** 2 fichiers importés avec tests
**Risque :** LOW

---

### P67 — SIGMA_SAFE_EVOLUTION `[PRIORITÉ 3]`

**But :** Modifier sigma uniquement par patchs chirurgicaux. Extension via `sigma/connectors.py` et `sigma/packets.py`. Jamais toucher les 5 fichiers P56B protégés.

**Entrée :** P63 safe_modification_candidates sigma
**Sortie :** sigma étendu sans régression P56B
**Risque :** MEDIUM — toute modification sigma nécessite diff minimal reviewé

---

### P68 — RUNTIME_CORE_RISK_REVIEW `[PRIORITÉ 4]`

**But :** Analyse détaillée de `engine_final.py`, `engine_runtime.py`, `kernel.py`, `unified/orchestrator.py`. **Pas d'import brut.** Review architectural, décision BLOCK/ADAPT/PHASE.

**Entrée :** P62 BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW engine/obsidia_runtime/*
**Sortie :** Plan d'adaptation ou confirmation BLOCK définitif
**Risque :** HIGH si importé brut

---

### P69 — GPS_TERRAIN_PORTABLE_RECONCILIATION `[PRIORITÉ 5]`

**But :** Relier GPS terrain (`connectors/aviation_robo.py`, `periphery/adapters/gps_adapter.py`) au proof sigma. Valider endpoint `sigma_monitoring` GPS. Tests terrain portables après P65.

**Entrée :** P63 gps terrain_existing + P65 adapters OS
**Sortie :** Tests terrain GPS validés, pipeline attesté bout-en-bout
**Risque :** LOW

---

### P70 — CANON_WORDING_TARGETED_CLEANUP `[PRIORITÉ 6]`

**But :** Corriger exactement 3 termes :
1. `docs/GLOSSAIRE.md` : "moins de 5 millisecondes" → "conçu pour interception avant exécution"
2. `docs/GLOSSAIRE.md` : "garantissant la sécurité" → "visant à assurer la sécurité"
3. `docs/KERNEL_OVERVIEW.md` : "Décision ex ante garantie" → "Décision ex ante by design"

**Risque :** LOW

---

### P71 — PRESENTATION_PROOF_SEPARATION `[PRIORITÉ 7]`

**But :** Séparer docs narratifs/publics des preuves techniques. Créer `docs/public/`. Déplacer uniquement, ne pas supprimer.

**Candidats déplacement :** `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md`, `OBSIDIA_F41_INVESTOR_JURY_FAQ.md`, `OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md`, `docs/civilization/`

**Conserver en place :** `docs/demo/F43-F59` (opérateur), `docs/architecture/` (technique)

**Risque :** LOW

---

### P72 — FULL_REGRESSION_FREEZE `[PRIORITÉ 8]`

**But :** `pytest` complet P56E→P72, `proofs/verify_all.py`, `scripts/check_forbidden_content.py`, `scripts/generate_recursive_manifest.py`, `scripts/verify_recursive_manifest.py`. Freeze si tout vert.

**Entrée :** Tous paliers P65-P71 terminés
**Risque :** NONE — validation uniquement

---

## Périmètres non touchés par P64

| Périmètre | Modifié |
|---|---|
| sigma/ | NON |
| apps/obsidia_api/routes/ | NON |
| runtime_wiring/ | NON |
| proofs/V18_3_1/ | NON |
| ACT | NON |
| memory_write | NON |
| graphiti_write | NON |
| kernel_mutation | NON |
