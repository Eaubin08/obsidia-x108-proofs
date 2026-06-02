# POST_IMPORT_COMMIT_PREFLIGHT_ALLOWLIST_REPORT
# _post_import_commit_prefight/
# Plan3 — Post-import commit preflight — READ_ONLY — NO GIT ADD — NO COMMIT
# Date: 2026-06-03
# Status: POST_IMPORT_COMMIT_PREFLIGHT_ALLOWLIST_READY

---

## 1. Summary

Après Plan3 P0→P7 + F07/F03/F06/F10 post-import + freeze audit, ce rapport identifie
exactement quels chemins sont candidats au commit, lesquels requièrent une revue humaine,
et lesquels ne doivent jamais être commités.

**Aucune commande git n'est exécutée dans ce rapport.**
Toutes les commandes listées sont des propositions READ_ONLY.

---

## 2. Current validated state

| Gate | Statut |
|------|--------|
| PLAN3_FREEZE_AUDIT_AND_INDEX_SYNC_READY | ✅ FOUND_READY |
| F07_COGNITIVE_CANON_CHECK_READY | ✅ FOUND_READY |
| F03_RSSI_RGPD_CANON_CHECK_READY | ✅ FOUND_READY |
| F06_ATLAS_CANON_CHECK_READY | ✅ FOUND_READY |
| F10_COMPLIANCE_DATA_GOVERNANCE_CANON_CHECK_READY | ✅ FOUND_READY |
| POST_IMPORT_FREEZE_AUDIT_READY | ✅ FOUND_READY |
| runtime_contracts/ files | 173 |
| .py under runtime_contracts/ | 0 |
| packages/ | absent |
| _freezes/ zips | 6 — DO NOT COMMIT |
| _source_packs/ zips | 5 — REVIEW REQUIRED |

---

## 3. Git status snapshot

```
## main...origin/main
 M .claude/settings.local.json    ← LOCAL_TOOLING_DIRTY_OUT_OF_SCOPE
?? .local_audits/                 ← DO_NOT_COMMIT
?? GITHUB_MATTER_COUNTS.txt       ← DO_NOT_COMMIT
?? GITHUB_TRACKED_FILES_AUDIT.txt ← DO_NOT_COMMIT
?? LOCAL_MODIFIED_FILES_AUDIT.txt ← DO_NOT_COMMIT
?? LOCAL_ONLY_MATTER_RECONCILIATION_20260602_100455.md ← DO_NOT_COMMIT
?? LOCAL_UNTRACKED_FILES_AUDIT.txt ← DO_NOT_COMMIT
?? OBSIDIA_CANONICAL_COMPONENT_CORPUS_MAP_V4_20260602_130452.csv ← DO_NOT_COMMIT
?? OBSIDIA_COMPONENT_GROUP_REGISTRY_20260602_125346.csv ← DO_NOT_COMMIT
?? OBSIDIA_COMPONENT_GROUP_REGISTRY_V2_20260602_125604/ ← DO_NOT_COMMIT
?? OBSIDIA_COMPONENT_SPLIT_V3_20260602_125929/ ← DO_NOT_COMMIT
?? SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/ ← DO_NOT_COMMIT
?? _freezes/                      ← DO_NOT_COMMIT (2402 fichiers + 6 zips)
?? _source_discovery/             ← SUPPORTING_EVIDENCE_CANDIDATE
?? _source_packs/                 ← REVIEW_REQUIRED (contient 5 .zip)
?? docs/source_packs/             ← SUPPORTING_EVIDENCE_CANDIDATE
?? runtime_contracts/             ← CORE_COMMIT_CANDIDATE ✅
?? specs/                         ← CORE_COMMIT_CANDIDATE ✅
```

---

## 4. Core commit candidates

### A — CORE_COMMIT_CANDIDATE (priorité haute)

| Chemin | Fichiers | .py | .zip | Secrets | Verdict |
|--------|--------:|-----|------|---------|---------|
| `runtime_contracts/` | 173 | 0 | 0 | aucun | ✅ SAFE |
| `specs/` | 212 | 0 | 0 | aucun | ✅ SAFE |

**`runtime_contracts/`** — Couche docs-only. Contrats P0, schémas P1, specs P2→P7,
F07/F03/F06/F10 imports, freeze audit. 0 .py, 0 .zip, 0 secrets.
Claim-scope vérifié : aucun claim runtime actif, aucun benchmark exécuté, aucun score réel.

**`specs/`** — 17 sous-dossiers (00_SCOPE_DISCIPLINE→12_NARRATIVE + _imports_readonly,
_invariant_graph, _source_index, external_signals). 0 .py, 0 secrets.

---

## 5. Supporting evidence candidates

### B — SUPPORTING_EVIDENCE_CANDIDATE (à valider humainement)

| Chemin | Fichiers | .py | .zip | Secrets | Verdict |
|--------|--------:|-----|------|---------|---------|
| `_source_discovery/` | 68 | 0 | 0 | aucun | ✅ CANDIDATE |
| `docs/source_packs/` | 4 | 0 | 0 | aucun | ✅ CANDIDATE |

**`_source_discovery/`** — Contient les audits readonly F78B, F78C, F07, F03, F06, F10.
Tous sont SOURCE_AUDIT_ONLY / NO_IMPORT_EFFECTIVE. Aucun zip. Aucun .py.
Commitable comme preuve d'audit.

**`docs/source_packs/`** — 4 fichiers : MERGE_INSTRUCTIONS.md, README.md,
SHA256SUMS.txt, VALIDATION_REPORT.yaml pour external_signals. Documentation safe.

---

## 6. Review-required candidates

### C — SOURCE_ARCHIVE_CANDIDATE_REVIEW_REQUIRED

| Chemin | Fichiers | .py | .zip | Contenu zip | Verdict |
|--------|--------:|-----|------|------------|---------|
| `_source_packs/` | 25 | 0 | 5 | Source packs Obsidia | ⚠️ REVIEW REQUIRED |

**`_source_packs/`** contient :
```
_source_packs/OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1/
  raw/OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip
  raw/OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip
  raw/OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1.zip
  raw/OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip
  raw/OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip
  + 20 fichiers non-zip (index, manifests, metadata)
```

**Risque zip** : Les zips peuvent contenir des données volumineuses ou sensibles.
Avant de committer `_source_packs/`, valider humainement que :
1. Les zips n'incluent pas de données personnelles
2. Les zips sont intentionnellement versionnés (pas seulement des archives locales)
3. La taille est acceptable pour le repo git

**Option sans zip** : Committer uniquement les métadonnées (exclure raw/*.zip via .gitignore).

---

## 7. Explicit do-not-commit list

| Chemin | Raison |
|--------|--------|
| `.claude/settings.local.json` | LOCAL_TOOLING_DIRTY_OUT_OF_SCOPE — outillage local uniquement |
| `_freezes/` | 2402 fichiers + 6 archives .zip — freeze local uniquement |
| `.local_audits/` | Scratchpad d'audit local |
| `GITHUB_MATTER_COUNTS.txt` | Fichier d'audit local temporaire |
| `GITHUB_TRACKED_FILES_AUDIT.txt` | Idem |
| `LOCAL_MODIFIED_FILES_AUDIT.txt` | Idem |
| `LOCAL_ONLY_MATTER_RECONCILIATION_20260602_100455.md` | Réconciliation locale temporaire |
| `LOCAL_UNTRACKED_FILES_AUDIT.txt` | Idem |
| `OBSIDIA_CANONICAL_COMPONENT_CORPUS_MAP_V4_20260602_130452.csv` | CSV d'audit local — non validé |
| `OBSIDIA_COMPONENT_GROUP_REGISTRY_20260602_125346.csv` | Idem |
| `OBSIDIA_COMPONENT_GROUP_REGISTRY_V2_20260602_125604/` | Dossier de registre local |
| `OBSIDIA_COMPONENT_SPLIT_V3_20260602_125929/` | Idem |
| `SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/` | Audit local dupliqué (déjà dans _source_discovery/) |

---

## 8. Safety checks

| Check | Résultat |
|-------|---------|
| .py sous runtime_contracts/ | 0 ✅ |
| .py sous specs/ | 0 ✅ |
| .py sous _source_discovery/ | 0 ✅ |
| .zip dans runtime_contracts/ | 0 ✅ |
| .zip dans specs/ | 0 ✅ |
| .zip dans _source_discovery/ | 0 ✅ |
| .zip dans _source_packs/ | 5 ⚠️ REVIEW REQUIRED |
| .zip dans _freezes/ | 6 ❌ DO NOT COMMIT |
| packages/ présent | NON ✅ |
| Secrets par nom (*.env, *secret*, *token*) | 0 détecté ✅ |
| node_modules/ | absent ✅ |
| .claude/settings.local.json | hors scope — ne pas committer ✅ |

---

## 9. Claim-scope checks (runtime_contracts/)

| Claim interdit | Présent dans RC? |
|---------------|-----------------|
| "runtime actif" | ❌ NON — docs-only confirmé |
| "RGPD certifié" | ❌ NON — RGPD_COMPLIANCE_SCOPE_GUARD boundary uniquement |
| "ISO certifié" | ❌ NON — hors scope |
| "benchmark exécuté" | ❌ NON — P7 = SPEC_ONLY |
| "score réel" | ❌ NON — CANDIDATE_ONLY |
| "tous les zips importés" | ❌ NON — SOURCE_AUDIT_ONLY |
| "packs branchés runtime" | ❌ NON — DOCS_ONLY |
| "sécurité certifiée" | ❌ NON — RSSI_EVIDENCE_ONLY boundary |

→ **Claim-scope : CLEAN** — aucun claim interdit détecté.

---

## 10. Proposed git add allowlist commands — DO NOT EXECUTE

```bash
# ══════════════════════════════════════════════════════════
# ATTENTION : NE PAS EXÉCUTER SANS VALIDATION HUMAINE
# Ces commandes sont des PROPOSITIONS uniquement.
# ══════════════════════════════════════════════════════════

# Étape 1 — Core (safe, priorité haute)
git add runtime_contracts/
git add specs/

# Étape 2 — Supporting evidence (à valider)
git add _source_discovery/
git add docs/source_packs/

# Étape 3 — Source packs SANS les zips (option recommandée)
# Option A : exclure raw/*.zip via .gitignore avant de stagifier
#   echo "_source_packs/*/raw/*.zip" >> .gitignore
#   git add .gitignore
#   git add _source_packs/
#
# Option B : ne pas committer _source_packs/ pour l'instant
# (attendre validation humaine sur les zips)

# Ce preflight lui-même
git add _post_import_commit_prefight/

# ══════════════════════════════════════════════════════════
# NE PAS AJOUTER :
# .claude/settings.local.json
# _freezes/
# .local_audits/
# GITHUB_*.txt
# LOCAL_*.txt / LOCAL_*.md
# OBSIDIA_CANONICAL_*.csv
# OBSIDIA_COMPONENT_*.csv
# OBSIDIA_COMPONENT_*_V2/
# OBSIDIA_COMPONENT_SPLIT_*/
# SOURCE_PACKS_DEEP_DIFF_AUDIT_*/
# ══════════════════════════════════════════════════════════
```

---

## 11. Proposed commit message — DO NOT EXECUTE

```
# ══════════════════════════════════════════════════════════
# PROPOSITION DE MESSAGE — NE PAS EXÉCUTER SANS VALIDATION
# ══════════════════════════════════════════════════════════

git commit -m "$(cat <<'EOF'
feat(plan3-complete): add Plan3 P0→P7 runtime_contracts docs-only layer + post-import spec imports

Plan3 phases (docs-only, no runtime):
  P0: contract/boundary/schema skeleton (7 contracts, 13 boundaries, 7 schemas)
  P1: JSON schemas + boundary specs
  P2: External Signals dry-run spec
  P3: X108 Gateway dry-run harness spec
  P4: Anti-bypass tests spec
  P5: OS3 Evidence dry-run spec (THEORETICAL_ONLY)
  P6: Readonly wrappers spec (Graphiti/Brody/NPL)
  P7: Education benchmark dry-run spec + reconciliation (20 scenarios, 20 failure modes)

Post-import gates (canon checks only, no runtime import):
  F07 Cognitive, F03 RSSI/RGPD, F06 Atlas, F10 Compliance

Freeze audit:
  173 files, 12/12 FOUND_READY, manifest SHA256 generated
  0 .py, 0 packages, 0 runtime active

specs/: 212 files, 17 subdirectories (00→12 + _imports_readonly + _invariant_graph)
_source_discovery/: F78B/F78C/F07/F03/F06/F10 audit evidence (readonly)
docs/source_packs/: external_signals documentation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## 12. Verdict

```
POST_IMPORT_COMMIT_PREFLIGHT_ALLOWLIST_READY

Core candidates    : runtime_contracts/ (173 files) + specs/ (212 files) → SAFE ✅
Evidence candidates: _source_discovery/ (68 files) + docs/source_packs/ (4 files) → SAFE ✅
Review required    : _source_packs/ (5 .zip dans raw/) → REVIEW_BEFORE_COMMIT ⚠️
Do not commit      : _freezes/, .claude/settings.local.json, root parasites → BLOCKED ❌

Action suivante recommandée :
  1. Valider humainement le périmètre ci-dessus
  2. Décider si _source_packs/ raw/*.zip vont dans le repo (option .gitignore recommandée)
  3. Exécuter les commandes git add proposées ci-dessus
  4. Exécuter le commit avec le message proposé
  5. Push après revue humaine finale
```
