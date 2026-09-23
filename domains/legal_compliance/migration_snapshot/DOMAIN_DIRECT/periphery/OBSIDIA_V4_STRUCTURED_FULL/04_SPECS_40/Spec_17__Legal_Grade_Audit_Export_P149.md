# Spec 17 — Legal-Grade Audit Export (P149)

**Statut V4 :** À_FORMALISER_OU_À_PROUVER
**Titre source détaillé :** Legal-Grade Audit Export

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
17) SPEC — Legal-Grade Audit Export
(ZIP + signatures)
17.0 Objectif
Produire un artefact juridique opposable, vérifiable sans Obsidia, utilisable par :
tribunal
administration
commission indépendante
audit tiers
17.1 Format global
obsidia_audit_export.zip
17.2 Structure ZIP canonique
audit_export/
├─ README.txt
├─ manifest.json
├─ policy/
│  └─ policy_compiled.bin
├─ traces/
│  └─ trace_bundle.json
├─ tickets/
│  └─ signed_tickets.json
├─ replay/
│  └─ replay_result.json
├─ violations/
│  └─ violations.json
├─ hashes/
│  └─ merkle_root.txt
├─ signatures/
│  ├─ audit.sig
│  └─ root.sig
└─ report/
   └─ audit_report.pdf
17.3 Manifest.json (clé)
{
  "audit_id": "AUD-2026-001",
  "system": "Obsidia",
  "policy_hash": "abc123",
  "trace_root": "merkle_xyz",
  "start_time": "...",
  "end_time": "...",
  "signed_by": "OS3_ROOT"
}
17.4 Signatures
audit.sig → signature Ed25519 du manifest
root.sig → signature de la racine Merkle
👉 Un tiers peut vérifier sans exécuter Obsidia
17.5 Valeur légale
Le ZIP permet de prouver :
ce qui était autorisé
ce qui a été demandé
ce qui s’est réellement passé
ce qui a été bloqué
que rien n’a été modifié a posteriori
