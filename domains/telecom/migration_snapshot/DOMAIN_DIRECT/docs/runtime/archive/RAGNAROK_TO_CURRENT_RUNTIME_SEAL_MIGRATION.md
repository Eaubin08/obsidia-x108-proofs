# RAGNAROK → CURRENT RUNTIME SEAL — MIGRATION RECORD

Date de la décision humaine : 2026-07-24
Contexte : consolidation `integration/final-local-consolidation-20260722` → `main`
Décision : `MERKLE_B: APPROVED_AS_RUNTIME_SCOPE_MIGRATION` + `MERKLE_REMEDIATION: REQUIRED_BEFORE_MAIN`

---

## 1. Ancien seal (archivé)

| Champ | Valeur |
|---|---|
| root | `1bc96a52bdbcc4d0538c3bf2` |
| count | 8007 preuves |
| last_seal | `2026-04-28T11:35:22` |
| status | `FINAL_SCELLÉ_RAGNAROK` |

Copie byte-for-byte : [`RAGNAROK_SEAL_1bc96a52_8007.json`](RAGNAROK_SEAL_1bc96a52_8007.json)

Provenance git :
- Dernier commit portant ce seal : `f7c111438d158033785027d8aa329673f90b2175` (parent de `075ce763`)
- Commits de scellement d'origine : `679f219` (« FINAL: Audit Surface Sealed at 8007 Proofs »), `47b7dba` (« stabilize kernel at 8007 proofs »)
- Remplacé par le commit : `075ce763ac8a8587621b4aeaf29df6a14daa59b4` (« fix: rebind Ragnarok runtime Merkle to current repo », 2026-06-10)

## 2. Seal runtime courant

| Champ | Valeur |
|---|---|
| merkle_root | `b8a69ce98ee86f3871ef2f75a50bf8acb138865adfaba77009bb6e57e569d6b2` |
| total_proofs_count | 2 |
| status | `INTEGRITY_VERIFIED` |
| corpus | `MonProjet/allData/decision_bank_1780995571691.json`, `MonProjet/allData/decision_bank_1780995941797.json` (non trackés par git) |

## 3. Relation entre les deux seals

- **Les deux seals couvrent des corpus différents.** L'ancien scellait un ensemble de 8007 preuves ; le courant scelle les 2 preuves présentes dans `MonProjet/allData` au moment du rebind.
- **Le seal courant ne constitue pas une continuité cryptographique de l'ancien**, ni une extension de celui-ci. Les formats de root diffèrent (root court 12 octets vs SHA-256 complet) et aucun chaînage n'existe entre eux.
- **La transition est une migration de périmètre runtime**, ratifiée par décision humaine (`MERKLE_B: APPROVED_AS_RUNTIME_SCOPE_MIGRATION`).

## 4. Préservation historique

L'ancien seal reste préservé :
1. Dans ce dossier d'archive (`RAGNAROK_SEAL_1bc96a52_8007.json`, reproduction exacte).
2. Dans l'historique git (`git show 075ce763^:merkle_seal.json`).
3. Dans deux fichiers trackés au HEAD : `_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/graphiti_readonly_records_v2.jsonl` et `docs/runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md`.

**Le corpus complet des 8007 preuves n'est pas déclaré intégralement reconstitué par ce commit.** Des restes existent dans `runtime_terrain_bank_trading_gps/allData_legacy_archive/` et `allData_legacy_quarantine/` (inventaire non exhaustif).

## 5. RFC3161

**Aucune relation RFC3161 n'est revendiquée entre ces deux seals.** L'ancre `proofs/rfc3161_anchor.json` couvre un root distinct (`fb264799…`, projet Obsidia-lab-trad, horodaté 2026-03-03 par freetsa.org) et ne référence ni `1bc96a52…` ni `b8a69ce9…`.

## 6. Garanties de ce commit

Ce commit est purement additif (2 fichiers de documentation). Il ne modifie pas :
- `merkle_seal.json`
- `runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs`
- `proofs/merkle_root.json`
- `proofs/rfc3161_anchor.json`

Aucune ancre n'est régénérée.
