# Public Boundary — Obsidia X-108 Proof

**Généré :** P78 — Presentation Proof Public Private Split  
**Date :** 2026-06-09  
**Mode :** DOC_INDEX_ONLY — aucune modification runtime

---

## Principe

Ce répertoire marque la frontière entre la surface proof publique et le moteur propriétaire interne.

> **Public proof ≠ moteur propriétaire complet.**  
> **Support présentation ≠ preuve technique.**

---

## Fichiers public safe (surface minimum)

| Fichier | Catégorie | Note |
|---|---|---|
| `README.md` | DOC_PUBLIC_SAFE | Freeze P1, tag `p1-freeze-2026-04-22` |
| `docs/LIMITS.md` | DOC_PUBLIC_SAFE | Limites claims P1 |
| `docs/GLOSSAIRE.md` | DOC_PUBLIC_SAFE | Glossaire technique |
| `docs/KERNEL_OVERVIEW.md` | DOC_PUBLIC_SAFE | Vue d'ensemble kernel |
| `docs/SIGMA.md` | DOC_PUBLIC_SAFE | Vue Sigma dispatcher |
| `docs/PROOF_SCOPE.md` | DOC_PUBLIC_SAFE | Périmètre proof P1 |
| `docs/BANK_SCENARIOS.md` | DOC_PROOF_TECHNICAL | Scénarios P2 bank |
| `docs/BANK_OUTPUTS.md` | DOC_PROOF_TECHNICAL | Format sorties Sigma |
| `docs/RFC3161.md` | DOC_RSSI_EVIDENCE_CANDIDATE | Ancre RFC3161 |
| `docs/AUDIT_GUIDE.md` | DOC_PUBLIC_SAFE | Guide audit |
| `docs/AUDIT_TOOLS.md` | DOC_PUBLIC_SAFE | Tools audit |
| `docs/act/` | DOC_PROOF_TECHNICAL | ACT lifecycle policy |
| `docs/agents/` | DOC_PROOF_TECHNICAL | Contrats agents non-souverains |
| `docs/os3/` | DOC_PROOF_TECHNICAL | OS3 hash chain, proof ticket |
| `docs/blockchain/` | DOC_PROOF_TECHNICAL | Policies blockchain dry-run |
| `specs/INDEX.md` | DOC_PUBLIC_SAFE | Index specs |
| `specs/OBSIDIA_READING_GUIDE.md` | DOC_PUBLIC_SAFE | Guide lecture |
| `specs/00_SCOPE_DISCIPLINE/` | DOC_RSSI_EVIDENCE_CANDIDATE | Claims bornés |
| `specs/01_X108_AUTHORITY/` | DOC_RSSI_EVIDENCE_CANDIDATE | Autorité GuardX108 |
| `specs/02_INTERLAYER_CONSTITUTION/` | DOC_FORMAL_PROOF_MAP | Constitution interlayer |
| `specs/07_AGENTS_CONNECTORS_MCP/` | DOC_PROOF_TECHNICAL | No-act boundary |
| `specs/08_MEMORY_BRODY_GRAPHITI/` | DOC_PROOF_TECHNICAL | Memory readonly |
| `specs/09_CRITICAL_WORLDS/` | DOC_RSSI_EVIDENCE_CANDIDATE | GPS/bank/trading |
| `specs/11_PROOF_REPLAY_OS3/` | DOC_RSSI_EVIDENCE_CANDIDATE | RFC3161/Merkle/attestation |
| `specs/_invariant_graph/` | DOC_FORMAL_PROOF_MAP | Graphe invariants |
| `proofs/lean/` | DOC_PROOF_TECHNICAL | Théorèmes Lean LEAN_PROVEN |
| `proofs/tla/` | DOC_PROOF_TECHNICAL | TLA+ specs |
| `proofs/merkle_root.json` | DOC_RSSI_EVIDENCE_CANDIDATE | Racine Merkle |
| `proofs/rfc3161_anchor.json` | DOC_RSSI_EVIDENCE_CANDIDATE | Timestamp RFC3161 |
| `proofs/verify_all.py` | DOC_PROOF_TECHNICAL | Vérificateur proof |
| `proofs/PROOFKIT_REPORT.json` | DOC_RSSI_EVIDENCE_CANDIDATE | ProofKit report |

---

## Ce qui ne figure PAS ici

| Zone | Raison |
|---|---|
| `sigma/`, `runtime_wiring/` | Protégé P77 — runtime souverain interne |
| `apps/obsidia_api/` | Protégé P77 — API interne |
| `connectors/` | Protégé P77 — P70 BLOCK_CONNECTOR_RUN |
| `periphery/` (3278 fichiers) | Propriétaire — 132 modules cognitifs internes |
| `docs/gencoin/`, `specs/10_*` | DO_NOT_PUBLISH — token non émis, review légale requise |
| `docs/runtime/` (427 fichiers) | DO_NOT_PUBLISH — données terrain locales |
| `docs/freeze/` (83 fichiers) | Archive uniquement |
| `_source_packs/`, `_tmp_core_import/` | Source packs locaux non canonisés |
| `_freezes/` (2455 fichiers) | Archive locale — ne pas publier |
| `.local_audits/` | Protégé P77 — audits locaux |

---

**Verdict :** Surface public safe identifiée en P78. Pack public consolidé en P80.
