# F78B_ZIP_TO_REPO_DIFF_MATRIX_SUMMARY
# Résumé du CSV F78B_ZIP_TO_REPO_DIFF_MATRIX.csv (2776 lignes)
# Date: 2026-06-02

---

## Note

Le CSV complet `F78B_ZIP_TO_REPO_DIFF_MATRIX.csv` contient 2776 lignes.
Ce fichier est le résumé par pack.

---

## Résumé par pack

| source_pack | total_entries | files | dirs | .py | already_extracted | decision_candidate |
|------------|--------------|-------|------|-----|------------------|--------------------|
| RSSI_EXTERNAL_SIGNALS | 41 | 41 | 0 | 0 | PARTIAL (37/41 F04) | ALREADY_EXTRACTED_F04 |
| RSSI_SECURITY | 167 | 167 | 0 | 16 | NO | INTEGRATE_DOCS_ONLY (F03) |
| RSSI_RGPD_ISO | 311 | 311 | 0 | 23 | NO | INTEGRATE_DOCS_ONLY (F03+F10) |
| BRANCHABLE_ATLAS | 1738 | ~1580 | ~158 | 18 | NO | SELECTIVE_INTEGRATE (F06) |
| COGNITIVE | 519 | ~490 | ~29 | 0 | NO | INTEGRATE_TO_SPECS (F07) |

## Sources hors-zip dans raw/

| Fichier | Taille | Contenu identifié | Décision |
|---------|--------|------------------|----------|
| Fichier markdown (2)(3).md collé | 26316 bytes | RÉPONSE 5/5 — description RSSI_RGPD_ISO zip | AUDIT_SOURCE / SOURCE_ONLY |
| Fichier markdown (3)(3).md collé | 25440 bytes | RÉPONSE 4/5 — description BRANCHABLE_ATLAS zip | AUDIT_SOURCE / SOURCE_ONLY |
| Fichier markdown (4)(1).md collé | 25682 bytes | RÉPONSE 3/5 — description COGNITIVE zip | AUDIT_SOURCE / SOURCE_ONLY |
| Fichier markdown (5).md collé | 31874 bytes | RÉPONSE 2/5 — description RSSI_SECURITY zip | AUDIT_SOURCE / SOURCE_ONLY |
| VERIFY_NON_EMPTY_NAME_METRICS_BOUNDARY_STATUS_V2_PASS.txt | 707 bytes | Validation RSSI_RGPD (280 files PASS) | INTEGRITY_CHECK / SOURCE_ONLY |

### Note sur les 4 markdowns

Ces 4 fichiers sont les **"4 markdowns raw non audités"** référencés dans
`PLAN3_P0_NEXT_STEPS.md` (P1_REQUIRED_SOURCE_AUDITS).

Ils constituent des descriptions narratives du contenu de chaque zip,
rédigées lors de la préparation des packs. Leur contenu confirme les
données du zip inspection (ex : COGNITIVE = 513 fichiers utiles, 458 yaml).

Ils sont dans `raw/` avec des noms non normalisés — à renommer et indexer
lors des F03/F06/F07 correspondants.

**Ces fichiers ne sont PAS encore "audités" au sens F78B** (leur contenu
détaillé n'a pas été parsé et comparé au zip). Audit narratif disponible,
audit structurel complet = F03/F06/F07.

### Note sur VERIFY_NON_EMPTY

Valide l'intégrité de `OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip` :
- zip_sha256 = 319706db7a2284190286cbd9fcfee03d81cc71c636f357a0324f5290714ce2ef
- total_files_checked = 280
- empty_files = 0
- strict_failures = 0
- validation_result = PASS

Ce fichier confirme que le zip RGPD est non-corrompu et structurellement valide.

---

## Collision types summary

| match_type | count_approx | action |
|------------|-------------|--------|
| SAME_NAME (désirés — déjà importés) | 37 (RSSI_EXT) | NO_ACTION |
| SAME_NAME (trivial README.md) | 3 | RENAME lors import |
| NOT_FOUND_LOCAL (non extraits) | ~2695 | INTEGRATE per F-series |
| QUARANTINE (.pytest_cache) | ~20 | DO_NOT_IMPORT |
| PYTHON_DO_NOT_IMPORT | 57 | EXCLUDE lors F03/F06 |
