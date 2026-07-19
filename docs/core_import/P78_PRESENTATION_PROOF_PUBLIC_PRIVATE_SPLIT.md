# P78 — Presentation Proof Public Private Split

**Audit ID :** P78  
**Statut :** `P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY`  
**Mode :** `AUDIT_AND_DOC_INDEX_ONLY` — aucun déplacement, aucune suppression, aucune modification runtime  
**Branche :** `p78-presentation-proof-public-private-split`  
**Date :** 2026-06-09

---

## 1. Verdict court

| Métrique | Valeur |
|---|---:|
| Entrées matrice classifiées | 109 |
| Public safe | 18 entrées |
| RSSI evidence candidates | 11 entrées |
| DO_NOT_PUBLISH | 17 entrées |
| Archive only | 11 entrées |
| Private proprietary | 13 entrées |
| Audit trail / ledger | 19 entrées |
| Proof technique | 13 entrées |
| Index docs créés | 4 |
| sigma/ modifié | NON |
| runtime modifié | NON |
| Réseau appelé | NON |
| ACT activé | NON |

**Conclusion principale :**  
La surface proof publique est identifiée et bornée. Les narratifs investisseur sont séparés du proof technique. Les archives, source packs locaux et données terrain restent en place (pas de déplacement massif). 4 index docs créés pour marquer les frontières public/investor/proof/demo.

---

## 2. Réponses aux 13 questions P78

| # | Question | Réponse |
|---|---|---|
| 1 | Fichiers preuves techniques ? | `proofs/lean/`, `proofs/tla/`, `proofs/verify_*.py`, `specs/01-02-07-08-09-11`, `docs/act/`, `docs/agents/`, `docs/os3/`, `docs/blockchain/` |
| 2 | Fichiers audit docs ? | `docs/core_import/P56A→P77` (80 files), `docs/architecture/` (45), `audit/` (11) |
| 3 | Fichiers supports publics ? | README.md, LIMITS.md, GLOSSAIRE.md, KERNEL_OVERVIEW.md, SIGMA.md, PROOF_SCOPE.md, BANK_SCENARIOS.md, BANK_OUTPUTS.md, RFC3161.md, `specs/INDEX.md`, `docs/release/BRODY_GPT_V1_*.md` |
| 4 | Fichiers supports investisseurs ? | `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md`, `docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md`, `docs/civilization/` (4), `docs/roadmap/`, `docs/P2_ROADMAP.md` |
| 5 | Fichiers narratifs/doctrine/pitch ? | `docs/civilization/` (AGI governance), `docs/demo/F41_*` (pitch/FAQ) |
| 6 | Fichiers démos ? | `docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md`, `docs/demo/F40-F60 archives` (17), `docs/demo/OBSIDIA_F59_BUS_LAYER_PUBLIC_DEMO_INDEX.md` |
| 7 | Fichiers archives ? | `docs/freeze/` (83), `docs/runtime/` (427), `docs/real_engine/` (31), `_freezes/` (2455), `.local_audits/` (42) |
| 8 | Fichiers source packs locaux ? | `_source_packs/` (40), `_tmp_core_import/` (282), `docs/source_packs/` (8), `specs/_source_index/` (7) |
| 9 | Fichiers privés/propriétaires ? | `periphery/` (3278), `specs/04-05-06-12` (55), `docs/translation/`, `docs/hackathons/`, `docs/gencoin/`, `docs/math/`, `apps/obsidia-workbench/` |
| 10 | Fichiers publiables ? | 18 groupes `KEEP_AS_PUBLIC_SAFE` + 13 groupes `KEEP_AS_TECHNICAL_PROOF` |
| 11 | Fichiers hors pack public ? | `sigma/`, `runtime_wiring/`, `connectors/`, `periphery/`, `docs/gencoin/`, `specs/10_*`, `docs/runtime/`, `_source_packs/` |
| 12 | Fichiers RSSI evidence pack ? | Voir section 4 — 11 candidats identifiés |
| 13 | Fichiers à séparer avant freeze P80 ? | `docs/demo/F41_PITCH + FAQ` → investor/, `docs/civilization/` → investor/, `docs/gencoin/` → DO_NOT_PUBLISH strict |

---

## 3. Catégories et décisions

### 3.1 DOC_PROOF_TECHNICAL — KEEP_AS_TECHNICAL_PROOF

| Groupe | Fichiers |
|---|---|
| `proofs/lean/` | 9 fichiers — théorèmes Lean LEAN_PROVEN |
| `proofs/tla/` | 17 fichiers — TLA+ specs |
| `proofs/V18_3_1/+V18_7/+V18_8/` | 12 fichiers — versions proof formelles |
| `proofs/verify_all.py + verify_decision.py + verify_merkle.py` | Vérificateurs |
| `docs/BANK_SCENARIOS.md` + `docs/BANK_OUTPUTS.md` | Proof Sigma bank |
| `docs/TEST_RESULTS_FINAL.md` | Résultats tests finaux |
| `docs/architecture/OBSIDIA_F60_SIGMA_REGISTRY_CANONICAL_DOMAINS.md` | Registry Sigma |
| `docs/agents/` (3) | Contrats agents non-souverains |
| `docs/act/` (4) | ACT lifecycle policy |
| `docs/os3/` (3) | OS3 hash chain/proof ticket/replay |
| `docs/blockchain/` (13) | Policies blockchain dry-run |
| `specs/02_INTERLAYER_CONSTITUTION/` (8) | Constitution interlayer |
| `specs/07_AGENTS_CONNECTORS_MCP/` (10) + `specs/08_MEMORY_BRODY_GRAPHITI/` (7) | Policies agents/mémoire |

### 3.2 DOC_RSSI_EVIDENCE_CANDIDATE — 11 candidats

| Candidat | Raison |
|---|---|
| `proofs/merkle_root.json` | Ancre cryptographique Merkle |
| `proofs/rfc3161_anchor.json` | Timestamp RFC3161 cryptographique |
| `proofs/PROOFKIT_REPORT.json` | Rapport complet proof |
| `docs/RFC3161.md` | Doc ancre RFC3161 |
| `docs/core_import/P72_INVARIANT_GRAPH_*` | Graphe invariants LEAN_PROVEN vs PYTHON_TESTED |
| `docs/core_import/P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md` | Sigma post-guard veto boundary |
| `specs/00_SCOPE_DISCIPLINE/` (9) | Scope discipline, claims bornés |
| `specs/01_X108_AUTHORITY/` (7) | Autorité GuardX108 Lean-proven |
| `specs/09_CRITICAL_WORLDS/` (14) | GPS/bank/trading/aviation |
| `specs/11_PROOF_REPLAY_OS3/` (9) | Replay/RFC3161/Merkle/attestation |
| `specs/_invariant_graph/` (10) | Graphe invariants formel |

### 3.3 DOC_PUBLIC_SAFE — 18 entrées

| Groupe | Note |
|---|---|
| README.md | Tag `p1-freeze-2026-04-22` |
| docs/LIMITS.md | Limites claims P1 |
| docs/GLOSSAIRE.md | Glossaire technique |
| docs/KERNEL_OVERVIEW.md | Vue d'ensemble kernel |
| docs/SIGMA.md | Vue Sigma |
| docs/PROOF_SCOPE.md | Périmètre proof P1 |
| docs/REPO_MAP.md + REPO_BOUNDARY.md | Carte/boundary repo |
| docs/AUDIT_GUIDE.md + AUDIT_TOOLS.md | Guide et tools audit |
| docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md | Séparateur proof/pitch |
| docs/demo/OBSIDIA_F46_PUBLIC_READINESS_GATE.md | Gate readiness public |
| docs/release/BRODY_GPT_V1_PUBLIC_RELEASE_PACKAGE.md + LIMITATIONS.md | Release Brody GPT V1 |
| docs/status/PUBLIC_STATUS.md | Statut public |
| docs/P2_BANK_REPLAY_RESULTS.md | Replay bank P2 |
| specs/INDEX.md + OBSIDIA_READING_GUIDE.md | Index et guide |
| docs/education/ + docs/benchmarks/ | READMEs publics |

### 3.4 DOC_DO_NOT_PUBLISH — 17 entrées (dont protégés P77)

| Zone | Raison |
|---|---|
| `sigma/` (136 fichiers) | PROTÉGÉ P77 — runtime souverain |
| `runtime_wiring/` (111 fichiers) | PROTÉGÉ P77 — wiring interne |
| `apps/obsidia_api/` | PROTÉGÉ P77 — API interne |
| `connectors/` (10 fichiers) | PROTÉGÉ P77 — P70 BLOCK_CONNECTOR_RUN |
| `audit/world_action_bus.jsonl` | PROTÉGÉ P77 — données runtime |
| `docs/gencoin/` (7 fichiers) | Token non émis — review légale requise |
| `specs/10_VALUE_GENCOIN_JCOIN/` (11 fichiers) | Token non émis — review légale requise |
| `docs/runtime/` (427 fichiers) | Données terrain locales |
| `docs/brody/` + `docs/memory/` + `docs/graphiti/` | API/mémoire interne |
| `docs/context/` + `docs/interface/` + `docs/periphery/` | API/runtime interne |
| `docs/world_calls/` + `docs/mcp/` | Runtime interne |
| `docs/WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md` | Chemins locaux |

### 3.5 DOC_PRIVATE_PROPRIETARY — 13 entrées

| Zone | Raison |
|---|---|
| `periphery/` (3278 fichiers) | 132 modules cognitifs — AGI/BDF/Tree34/MMonde |
| `specs/04_AGI_TREE34_FLUX/` | Propriétaire |
| `specs/05_BALANCE_BUV_GEOMETRIES/` | Propriétaire |
| `specs/06_HIGH_PERIPHERY_SYSTEMS/` | Propriétaire |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/` (34) | Propriétaire, contenu philosophique |
| `docs/translation/` | OS Trad/IR pipeline |
| `docs/hackathons/` | Échecs hackathons, données propriétaires |
| `docs/math/` | Math formelle non revue |
| `docs/language/` | Language routing propriétaire |
| `docs/GENCOIN_SANDBOX_INGESTION_REPORT.md` | Token sandbox |
| `apps/obsidia-workbench/` | Workbench UI propriétaire |

---

## 4. Frontières identifiées

```
PUBLIÉ (public safe + proof technique)
├── README.md, docs/LIMITS.md, docs/GLOSSAIRE.md, docs/KERNEL_OVERVIEW.md
├── docs/SIGMA.md, docs/PROOF_SCOPE.md, docs/BANK_SCENARIOS.md, docs/BANK_OUTPUTS.md
├── docs/act/, docs/agents/, docs/os3/, docs/blockchain/
├── specs/00_SCOPE_DISCIPLINE/, specs/01_X108_AUTHORITY/
├── specs/02_INTERLAYER_CONSTITUTION/, specs/07-08-09-11/
├── specs/_invariant_graph/, specs/INDEX.md
├── proofs/lean/, proofs/tla/, proofs/verify_*.py
└── proofs/merkle_root.json, proofs/rfc3161_anchor.json

INVESTISSEUR (review claims requis)
├── docs/demo/F41_PUBLIC_INVESTOR_PITCH.md
├── docs/demo/F41_INVESTOR_JURY_FAQ.md
├── docs/civilization/ (4 fichiers)
└── docs/roadmap/

DÉMO UNIQUEMENT
├── docs/demo/F41_DEMO_SCRIPT_3_5_MIN.md
└── docs/demo/F59_BUS_LAYER_PUBLIC_DEMO_INDEX.md

AUDIT TRAIL (interne)
├── docs/core_import/P56A→P77 (80 fichiers)
├── docs/architecture/ (45 fichiers)
└── audit/ (11 fichiers)

ARCHIVÉ
├── docs/freeze/ (83 fichiers)
├── docs/runtime/ (427 fichiers)
├── docs/real_engine/ (31 fichiers)
├── _freezes/ (2455 fichiers)
└── .local_audits/ (42 fichiers)

PROPRIÉTAIRE (ne pas publier)
├── periphery/ (3278 fichiers)
├── specs/04-05-06-12/
├── docs/translation/, docs/hackathons/, docs/math/
└── apps/obsidia-workbench/

DO NOT PUBLISH (protégé + légal)
├── sigma/ (PROTÉGÉ P77)
├── runtime_wiring/ (PROTÉGÉ P77)
├── connectors/ (PROTÉGÉ P77 + P70)
├── docs/gencoin/ + specs/10_* (review légale token)
└── audit/world_action_bus.jsonl (PROTÉGÉ P77)
```

---

## 5. Index docs créés

| Fichier | Contenu |
|---|---|
| `docs/public/README_PUBLIC_BOUNDARY.md` | Surface public safe complète |
| `docs/investor/README_INVESTOR_BOUNDARY.md` | Narratifs investisseur + règles claims |
| `docs/proof/README_PROOF_BOUNDARY.md` | Surface proof technique + RSSI candidates |
| `docs/demo/README_DEMO_BOUNDARY.md` | Classification docs/demo/ complète |

---

## 6. Contraintes P72/P77 appliquées

| Contrainte | Application P78 |
|---|---|
| `GUARD_X108_FINAL_AUTHORITY` | specs/01_X108_AUTHORITY/ → RSSI candidate |
| `SIGMA_POST_GUARD_VETO_ONLY` | sigma/ → DO_NOT_PUBLISH |
| `NO_ACT_BEFORE_TAU` | connectors/ → DO_NOT_PUBLISH |
| `NO_MEMORY_WRITE_WITHOUT_GATE` | audit/world_action_bus.jsonl → DO_NOT_PUBLISH |
| `LEAN_PROVEN_VS_PYTHON_TESTED` | proofs/lean/ → DOC_PROOF_TECHNICAL public safe |
| `NETWORK_EGRESS_REVIEW_REQUIRED` | connectors/ → DO_NOT_PUBLISH |
| `P77 REGROUP_CANDIDATE` | docs/source_packs/ → SOURCE_PACK_LOCAL_ONLY |
| `P76_BOM_NORMALIZATION_SAFE` | sigma/examples/gps_omega_chaos.json → RUNTIME_INTERNAL |

---

## 7. Findings

| ID | Type | Action |
|---|---|---|
| P78-F1 | SEPARATION_PROOF_VS_DEMO | docs/demo/ F41 pitch/FAQ → MOVE_LATER_INVESTOR avant P80 |
| P78-F2 | DO_NOT_PUBLISH_TOKEN | docs/gencoin/ + specs/10_* (18 fichiers) → DO_NOT_PUBLISH |
| P78-F3 | RSSI_EVIDENCE_PACK_CANDIDATES | 11 candidats → socle P79 |
| P78-F4 | PERIPHERY_MASSIVE_PROPRIETARY | periphery/ 3278 fichiers → KEEP_PRIVATE_PROPRIETARY |
| P78-F5 | PUBLIC_SAFE_SURFACE_IDENTIFIED | 18 entrées public safe → pack public P80 |
| P78-F6 | ARCHIVE_LOAD | 5 zones massives (2455+427+3278+282+42 fichiers) → ne pas charger |
| P78-F7 | INDEX_DOCS_CREATED | 4 index docs frontières créés |

---

## 8. Décision

P78 conclut que la **frontière public/proof/investisseur/propriétaire est clairement établie**.

- **Surface public safe** : 18 groupes, clairement bornés par `specs/00_SCOPE_DISCIPLINE/` et le tag `p1-freeze-2026-04-22`.
- **RSSI evidence candidates** : 11 groupes — RFC3161, Merkle, P72, specs/01/09/11, invariant graph.
- **Propriétaire** : `periphery/` 3278 fichiers + specs/04-05-06-12 + OS Trad — DO NOT PUBLISH.
- **Token** : `docs/gencoin/` + `specs/10_*` — 18 fichiers DO_NOT_PUBLISH sans review légale.
- **Aucun déplacement** de fichiers effectué — index docs uniquement créés.

**split_decision : CLASSIFY_AND_INDEX_ONLY**

**Prochain geste : P79 — RSSI Evidence Pack and GitHub Security Audit.**

---

**Verdict :** `P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT_READY`
