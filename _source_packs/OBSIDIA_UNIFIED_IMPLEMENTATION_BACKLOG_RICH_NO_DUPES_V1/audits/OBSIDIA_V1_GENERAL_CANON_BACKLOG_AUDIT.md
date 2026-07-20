# OBSIDIA V1 GENERAL CANON BACKLOG — Audit

**Date :** 2026-06-02
**Chantier :** OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1
**Statut :** SOURCE_FROZEN — AUDIT_ONLY — NO_RUNTIME_PATCH

---

## 1. Positionnement

**F74-F77 = socle runtime stabilisé** (chantier précédent)
- F74 Fresh Clone : COMPLETE
- F75 Lean Proofs : périmètre proofs/lean/
- F76 Cloud/Prod : PROD_BLOCKED (CORS, auth, Dockerfile, /health)
- F77 Pack Externe : PACK_PARTIAL (9 fichiers external_pack/ manquants)

**Ce chantier = vision générale V1** — corpus conceptuel complet / specs / atlas / RSSI / RGPD / cognition / external signals

**Ce chantier NE DOIT PAS :**
- être branché directement au runtime F74-F77
- modifier apps/, sigma/, tests/, periphery/
- être committé dans la branche principale sans revue humaine
- produire d'ACT ou de décision autonome

**SPEC_ONLY_FIRST obligatoire** pour tout fichier de ce backlog.

**Boundary globale :** `KX108_ONLY | NO_ACT | NO_DECISION | READONLY_BY_DEFAULT | BACKLOG_ONLY`

---

## 2. Packs inclus

### Pack 1 — External Signals
| Champ | Valeur |
|-------|--------|
| Fichier source | `OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip` |
| Fichiers | 41 |
| Taille dézippée | ~212 KB |
| Couche OS cible | OS1/OS2/OS3 |
| Rôle | Temporal sidecar / anti-replay / bounded tool-call signals |
| Boundary | `KX108_ONLY; SIGNAL_ONLY; NO_ACT; NO_DECISION; TEMPORAL_PREFILTER_ONLY` |
| Priorité | P2_SECURITY_PROOF |
| Dépendances | DecisionTicket + X108 guard + audit receipts |
| Stade XLSX | F04 — après authority + audit, avant memory/action adapters |
| Risque principal | External Signals ne doit jamais réautoriser X108 ou émettre ACT |

### Pack 2 — RSSI Security Presentation
| Champ | Valeur |
|-------|--------|
| Fichier source | `OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip` |
| Fichiers | 167 |
| Taille dézippée | ~2066 KB |
| Couche OS cible | OS3 |
| Rôle | RSSI security posture, audit narrative, controls, evidence |
| Boundary | `KX108_ONLY; DOC_ONLY; NO_RUNTIME_AUTHORITY; EVIDENCE_ONLY` |
| Priorité | F03 — early OS3 audit/security surface |
| Dépendances | OS3 ProofTicket surface |
| Risque principal | RSSI posture ≠ certification réelle — claims compliance à surveiller |

### Pack 3 — RGPD ISO Readiness
| Champ | Valeur |
|-------|--------|
| Fichier source | `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` |
| Fichiers | 280 |
| Taille dézippée | ~2882 KB |
| 8 noms dupliqués | OUI — à résoudre avant import |
| Couche OS cible | OS3 + compliance |
| Rôle | RGPD / ISO / RSSI readiness and compliance evidence |
| Boundary | `KX108_ONLY; DOC_ONLY; COMPLIANCE_CLAIM_SCOPE_GUARD` |
| Priorité | F03/F10 |
| Risque principal | RGPD ISO readiness ≠ certification légale — guard obligatoire |

### Pack 4 — Cognitive Reintegration
| Champ | Valeur |
|-------|--------|
| Fichier source | `OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip` |
| Fichiers | 513 |
| Taille dézippée | ~4089 KB |
| Root dossiers | 6 |
| Couche OS cible | OS1/OS2 |
| Rôle | Cognitive components, packets, schemas, metrics, invariants |
| Boundary | `KX108_ONLY; ADVISORY_ONLY; NO_ACT; NO_DIAGNOSIS; NO_MEMORY_WRITE_WITHOUT_GATE` |
| Priorité | F07 — après memory/atlas boundaries |
| Dépendances | Graphiti/Brody readonly + Atlas registry |
| Risque principal | Cognition peut devenir floue si branchée sans packets contractuels |

### Pack 5 — Branchable Atlas
| Champ | Valeur |
|-------|--------|
| Fichier source | `OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip` |
| Fichiers | 1738 |
| Taille dézippée | ~36444 KB |
| 92 noms dupliqués | OUI — résolution avant import |
| Couche OS cible | Atlas/Graphiti |
| Rôle | World/protocol atlas, branchable contexts, Graphiti-ready content |
| Boundary | `KX108_ONLY; ATLAS_READONLY; NO_ACT; GRAPHITI_READONLY` |
| Priorité | F06 — après Graphiti/Brody readonly |
| Risque principal | Volume massif (1738 fichiers, 36MB) — import trop tôt risque de saturer le repo |
| Action QUARANTINE | 20 fichiers marqués `QUARANTINE_DO_NOT_IMPLEMENT` — à ne pas importer |

### Pack 6 — Markdown source notes (4 fichiers)
| Champ | Valeur |
|-------|--------|
| Fichiers | `Fichier markdown (2)(3).md collé`, `(3)(3)`, `(4)(1)`, `(5)` |
| Taille totale | ~109 KB |
| Rôle | Notes conceptuelles source — documentation complémentaire |
| Boundary | `DOC_ONLY; NO_RUNTIME_AUTHORITY` |
| Priorité | Lecture + extraction de specs — P3 |

### Pack 7 — XLSX file-by-file plan
| Champ | Valeur |
|-------|--------|
| Fichier | `OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx` |
| Sheets | 10 (README, SUMMARY, IMPLEMENT_ORDER, FILE_PLAN_ALL, EXT_SIGNALS, RSSI_SECURITY, COGNITIVE, ATLAS, RGPD_ISO, ACTION_COUNTS) |
| Rows FILE_PLAN_ALL | 2739 lignes planifiées |
| Stades | F00 à F10 définis |
| Rôle | Plan d'implémentation officiel — source de vérité du chantier |
| Usage | READ_ONLY pour orchestrer les phases suivantes |

### Pack 8 — Verification report
| Champ | Valeur |
|-------|--------|
| Fichier | `VERIFY_NON_EMPTY_NAME_METRICS_BOUNDARY_STATUS_V2_PASS.txt` |
| Taille | 707 bytes |
| Rôle | Rapport de validation du backlog (pass/fail/empty check) |
| Statut | PASS |

---

## 3. Ordre d'implémentation recommandé

Conforme au XLSX IMPLEMENT_ORDER (F00-F10) :

| Étape | Priorité | Raison |
|-------|----------|--------|
| **F00 SOURCE FREEZE** | FAIT (ce chantier) | Hashes, manifest, no-dedupe, copie readonly |
| **F01 AUTHORITY CONTRACTS** | P0 — partiellement présent | specs/01_X108_AUTHORITY/ existe — étendre aux nouveaux packs |
| **F02 CENTRAL REGISTRY** | P0 — 2739 fichiers à gérer | Sans registry, le volume est ingérable |
| **F03 OS3 SECURITY/RGPD** | P1 — sources prêtes | RSSI + RGPD copiés — docs/evidence only |
| **F04 EXTERNAL SIGNALS** | P1 — sources prêtes | 41 fichiers, boundary claire, temporel d'abord |
| **F05 MEMORY READONLY** | P2 — Brody/Graphiti déjà partiellement wired | Formaliser ContextPacket exports |
| **F06 BRANCHABLE ATLAS** | P2 — après F05 | Atlas = contexte readonly — Graphiti nodes |
| **F07 COGNITIVE REINTEGRATION** | P3 — après Atlas | Composants cognitifs advisory only |
| **F08 NPL PROVENANCE** | P3 — specs Plan 2 déjà créées | Brancher sur récepteurs existants |
| **F09 EDUCATION VERTICAL** | P4 — dernier vertical | Testbed de validation cognition + NPL |
| **F10 BENCHMARKS + DEMO** | P5 — final | Quantification et publication publique |

**Pourquoi cet ordre :**
- F00-F02 : fondations (source gelée + contrats autorité + registry)
- F03-F04 : proof surface + signals temporels (sécurité first)
- F05-F07 : mémoire + atlas + cognition (readonly puis advisory)
- F08-F10 : NPL + éducation + démo (les plus sensibles sur claim-scope)

---

## 4. Boundaries globales

```
KX108_ONLY           — seule autorité décisionnelle
NO_ACT               — aucun composant de ce backlog n'émet ACT
NO_DECISION          — aucun packet n'est un verdict final
READONLY_BY_DEFAULT  — tous les imports = lecture seule par défaut
NO_RUNTIME_AUTHORITY — aucun pack ne s'auto-exécute
SPEC_ONLY_FIRST      — spec avant runtime, toujours
IMPORT_AS_SOURCE_EVIDENCE — valeur = évidence + spec, pas runtime direct
X108_REQUIRED_FOR_WORLD_ACTION — toute action monde = gate X108
```

---

## 5. Arborescence cible proposée (sans créer runtime)

```
docs/source_packs/
    external_signals/          ← F04
    rssi_security/             ← F03
    rgpd_iso/                  ← F03
    cognitive/                 ← F07
    atlas/                     ← F06

specs/
    external_signals/          ← F04 specs
    compliance/                ← F03
    cognition/                 ← F07
    atlas/                     ← F06
    npl/                       ← F08 (déjà dans specs/12_NARRATIVE_PROVENANCE_LAYER/)

signals/                       ← F04 temporal packets
security/                      ← F03 RSSI controls
compliance/                    ← F03 RGPD ISO
cognition/                     ← F07 packets + components
atlas/                         ← F06 registry + contexts
audit/proof/                   ← OS3 evidence
registry/                      ← F02 central registry
    modules/
    packets/
    metrics/
    boundary/
packages/shared/packets/       ← F01 shared contracts
```

---

## 6. Collision / doublons détectés

### Doublons internes aux zips
| Pack | Noms dupliqués | Action |
|------|---------------|--------|
| BRANCHABLE_ATLAS | 92 basenames | Résoudre avant import — COLLISION_REVIEW_RICHER_VERSION |
| RGPD_ISO | 8 noms | Résoudre avant import — COLLISION_REVIEW_RICHER_VERSION |
| Others | 0 | SAFE_NEW_SOURCE |

### Doublons de target_path dans XLSX
- 48 target paths dupliqués détectés dans FILE_PLAN_ALL
- Action : COLLISION_REVIEW — identifier quelle version est la plus riche

### Collision avec le repo existant
| Chemin cible XLSX | Présent dans repo | Action |
|-------------------|-------------------|--------|
| `docs/source_packs/external_signals/` | NON | SAFE_NEW_SOURCE |
| `specs/external_signals/` | NON | SAFE_NEW_SOURCE |
| `specs/` | OUI (Plan 2) | Sous-dossiers nouveaux — SAFE_NEW_SOURCE |
| `periphery/` | OUI | DO_NOT_IMPORT_RUNTIME |
| `apps/` | OUI | DO_NOT_IMPORT_RUNTIME |
| `sigma/` | OUI | DO_NOT_IMPORT_RUNTIME |
| `tests/` | OUI | DO_NOT_IMPORT_RUNTIME |

### Classification
- **A. SAFE_NEW_SOURCE** : docs/source_packs/, specs/new_domains/
- **B. COLLISION_KEEP_EXISTING** : tout ce qui touche periphery/, apps/, sigma/, tests/
- **C. COLLISION_REVIEW_RICHER_VERSION** : 48 target paths dupliqués dans XLSX, 92 noms Atlas, 8 noms RGPD
- **D. DO_NOT_IMPORT_RUNTIME** : tout ce qui serait dans periphery/ ou apps/
- **E. DUPLICATE_SOURCE_ONLY** : fichiers dupliqués à l'intérieur d'un même zip
- **F. NEEDS_MANUAL_MAPPING** : les 20 fichiers QUARANTINE_DO_NOT_IMPLEMENT

---

## 7. Risques

| Risque | Gravité | Mitigation |
|--------|---------|-----------|
| Import massif trop tôt (1738 fichiers Atlas) | HAUTE | F06 en dernier — F00-F02 d'abord |
| Mélange runtime/spec | HAUTE | DO_NOT_IMPORT_RUNTIME strict |
| Claims compliance trop forts (RGPD ISO ≠ certification) | HAUTE | COMPLIANCE_CLAIM_SCOPE_GUARD obligatoire |
| RSSI posture ≠ certification de sécurité | HAUTE | Guard : "RSSI readiness ≠ certification" |
| Atlas trop volumineux pour le repo | MOYENNE | Importer en registries légers, pas le zip entier |
| Cognition floue si branchée sans packets | MOYENNE | Packets contractuels avant tout import cognitif |
| External Signals réautorisant X108 | HAUTE | Signal only — X108 reste l'autorité |
| 20 fichiers QUARANTINE dans Atlas | BASSE | QUARANTINE_DO_NOT_IMPLEMENT — ne pas importer |
| 92 dupliqués Atlas + 8 dupliqués RGPD | MOYENNE | Résoudre avant import |
| NPL claim-scope si branché trop vite | MOYENNE | NPL_CLAIM_SCOPE_LIMITS.md déjà en place |

---

## 8. Plan par phases

| Phase | Contenu | Statut |
|-------|---------|--------|
| **P0** | Source freeze / manifest SHA256 | **FAIT** (ce chantier) |
| **P1** | SPEC_ONLY index pour les 5 packs | A faire |
| **P2** | External Signals readonly (41 fichiers) | A faire (F04) |
| **P3** | RSSI Security docs/readiness (167 fichiers) | A faire (F03) |
| **P4** | RGPD ISO docs/readiness (280 fichiers) | A faire (F03/F10) |
| **P5** | Cognitive Reintegration specs/packets (513 fichiers) | A faire (F07) |
| **P6** | Atlas registries/proof (1738 fichiers — par registry seulement) | A faire (F06) |
| **P7** | Adapters readonly Brody/Graphiti | A faire (F05) |
| **P8** | Tests no-act/no-decision pour chaque pack | A faire (F04-F07) |
| **P9** | Dashboard OS3 (preuve + compliance) | A faire (F10) |
| **P10** | Runtime gating candidate — plus tard seulement | FUTUR |

---

## 9. Tests à prévoir

```
test_no_act_from_any_backlog_component
test_no_decision_authority_in_backlog
test_no_runtime_authority_granted_to_signals
test_kx108_only_present_in_all_boundaries
test_packets_schema_valid (chaque pack)
test_registry_parse_ok (Atlas + central registry)
test_no_empty_files_in_import
test_no_duplicate_target_paths (48 à résoudre)
test_source_hash_manifest_valid
test_compliance_claim_scope_guard (RGPD ISO)
test_rgpd_iso_not_certified_guard
test_atlas_readonly_guard
test_cognitive_world_action_requires_x108
test_external_signal_cannot_authorize_act
test_quarantine_files_not_imported (20 fichiers Atlas)
```

---

## 10. Décision finale

```
OBSIDIA_V1_GENERAL_CANON_BACKLOG_READY_FOR_REVIEW
```

**Justification :**
- 11/11 fichiers source copiés avec sha256 manifest
- 5 filelists zip créées (2739 lignes planifiées analysées)
- XLSX lu : 10 sheets, F00-F10 définis, 2739 fichiers planifiés
- 48 target paths dupliqués — à résoudre avant import
- 20 fichiers QUARANTINE — à ne pas importer
- Aucun runtime patché
- Boundary KX108_ONLY documentée pour chaque pack
- Ordre F00-F10 conforme au XLSX IMPLEMENT_ORDER
