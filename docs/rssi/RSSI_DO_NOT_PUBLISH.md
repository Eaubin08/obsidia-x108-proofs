# RSSI — Do Not Publish — Obsidia X-108

**Généré :** P79  
**Date :** 2026-06-09

---

> **Ces zones sont exclues du pack RSSI public et de toute publication GitHub.**  
> **Autorité : DO_NOT_PUBLISH P78 + P77 PROTECTED_FILES.**

---

## Zones DO_NOT_PUBLISH (RSSI evidence)

| Zone | Raison | Source autorité |
|---|---|---|
| `sigma/` (136 fichiers) | Runtime souverain KX108_ONLY — logique décision propriétaire | P77 PROTÉGÉ |
| `runtime_wiring/` (111 fichiers) | Wiring interne runtime | P77 PROTÉGÉ |
| `apps/obsidia_api/` | API interne — routes exposées | P77 PROTÉGÉ |
| `connectors/` (10 fichiers) | BLOCK_CONNECTOR_RUN P70 | P77 + P70 |
| `audit/world_action_bus.jsonl` | Données runtime souveraines | P77 PROTÉGÉ |
| `periphery/` (3278 fichiers) | 132 modules cognitifs propriétaires | P78 KEEP_PRIVATE |
| `docs/gencoin/` (7 fichiers) | Token non émis — review légale requise | P78 DO_NOT_PUBLISH |
| `specs/10_VALUE_GENCOIN_JCOIN/` (11 fichiers) | Token non émis — review légale requise | P78 DO_NOT_PUBLISH |
| `docs/runtime/` (427 fichiers) | Archives terrain locales avec chemins sensibles | P78 ARCHIVE_ONLY |
| `_source_packs/` (40 fichiers) | Source packs locaux non canonisés | P78 LOCAL_ONLY |
| `_tmp_core_import/` (282 fichiers) | Import temporaire local | P78 LOCAL_ONLY |
| `_freezes/` (2455 fichiers) | Archives lourdes | P78 ARCHIVE_ONLY |
| `.local_audits/` (42 fichiers) | Audits locaux — gitignored | P78 ARCHIVE_ONLY |

---

## Risques sécurité identifiés

| Fichier | Risque | Action |
|---|---|---|
| `docs/runtime/archive/.../BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md` | NEO4J_PASSWORD `SECRET_VALUE_REDACTED` | **REQUIRES_SECRET_ROTATION** |
| `scripts/brody_terminal_chat.py` | NEO4J_PASSWORD template | REQUIRES_REVIEW |
| `proofs/V18_3_1/.../PUBLIC_DEPLOY.md` | MINIO template `<set-via-env>` | REQUIRES_REVIEW |

**Règle :** Aucune valeur de secret n'est affichée dans ce document.
