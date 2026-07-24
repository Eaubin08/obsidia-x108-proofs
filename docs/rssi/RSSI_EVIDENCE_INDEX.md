# RSSI Evidence Index — Obsidia X-108

**Généré :** P79  
**Date :** 2026-06-09

---

## Index par catégorie

### RSSI_EVIDENCE_CORE

| Fichier | Décision |
|---|---|
| `proofs/merkle_root.json` | INCLUDE_RSSI_PACK |
| `proofs/rfc3161_anchor.json` | INCLUDE_RSSI_PACK |
| `proofs/metadata.json` | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_FORMAL_PROOF

| Groupe | Fichiers | Décision |
|---|---|---|
| `proofs/lean/` | 9 théorèmes Lean | INCLUDE_RSSI_PACK |
| `proofs/tla/` | 17 specs TLA+ | INCLUDE_RSSI_PACK |
| `specs/_invariant_graph/` | 10 fichiers graphe | INCLUDE_RSSI_PACK |
| `docs/core_import/P72_INVARIANT_GRAPH_*` | Alignement formel | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_AUDIT_TRAIL

| Groupe | Fichiers | Décision |
|---|---|---|
| `docs/core_import/` | 82 fichiers P56A→P78 | INCLUDE_INTERNAL_RSSI_ONLY |
| `audit/sovereign_tickets.jsonl` | Tickets souverains | INCLUDE_INTERNAL_RSSI_ONLY |
| `docs/core_import/P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md` | Gel P56D | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_HASH_MANIFEST

| Fichier | Décision |
|---|---|
| `scripts/generate_recursive_manifest.py` | INCLUDE_RSSI_PACK |
| `scripts/verify_recursive_manifest.py` | INCLUDE_RSSI_PACK |
| `scripts/generate_hashes.py` | INCLUDE_RSSI_PACK |
| `scripts/verify_hashes.py` | INCLUDE_RSSI_PACK |
| `scripts/check_forbidden_content.py` | INCLUDE_RSSI_PACK |
| `proofs/compute_merkle_root.py` | INCLUDE_RSSI_PACK |
| `proofs/compute_merkle_standalone.py` | INCLUDE_RSSI_PACK |
| `tools/anchor_merkle_root.py` | INCLUDE_RSSI_PACK |
| `tools/verify_chain_anchor.py` | INCLUDE_RSSI_PACK |
| `tools/verify_threat_model.py` | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_REPLAY

| Fichier | Décision |
|---|---|
| `proofs/verify_all.py` | INCLUDE_RSSI_PACK |
| `proofs/verify_decision.py` | INCLUDE_RSSI_PACK |
| `proofs/verify_merkle.py` | INCLUDE_RSSI_PACK |
| `specs/11_PROOF_REPLAY_OS3/` (9 fichiers) | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_BOUNDARY_DOC

| Fichier | Décision |
|---|---|
| `docs/public/README_PUBLIC_BOUNDARY.md` | INCLUDE_RSSI_PACK |
| `docs/proof/README_PROOF_BOUNDARY.md` | INCLUDE_RSSI_PACK |
| `docs/core_import/P78_PRESENTATION_PROOF_PUBLIC_PRIVATE_SPLIT.json` | INCLUDE_INTERNAL_RSSI_ONLY |
| `SECURITY.md` | KEEP_PUBLIC_SAFE |

### RSSI_EVIDENCE_PUBLIC_SAFE

| Groupe | Fichiers | Décision |
|---|---|---|
| `specs/00_SCOPE_DISCIPLINE/` | 9 | INCLUDE_RSSI_PACK |
| `specs/01_X108_AUTHORITY/` | 7 | INCLUDE_RSSI_PACK |
| `specs/09_CRITICAL_WORLDS/` | 14 | INCLUDE_RSSI_PACK |
| `docs/RFC3161.md` | 1 | INCLUDE_RSSI_PACK |

### RSSI_EVIDENCE_INTERNAL_ONLY

| Fichier | Note | Décision |
|---|---|---|
| `proofs/PROOFKIT_REPORT.json` | Gitignore conflict — revue requise | INCLUDE_INTERNAL_RSSI_ONLY |

### RSSI_EVIDENCE_DO_NOT_PUBLISH

| Zone | Décision |
|---|---|
| `sigma/` | DO_NOT_PUBLISH |
| `runtime_wiring/` | DO_NOT_PUBLISH |
| `connectors/` | DO_NOT_PUBLISH |
| `audit/world_action_bus.jsonl` | DO_NOT_PUBLISH |
