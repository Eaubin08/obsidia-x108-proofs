# PLAN3_CLAIM_SCOPE_LOCKS
# runtime_contracts/freeze_audit/
# Plan3 Freeze Audit — Verrous de claim-scope
# Date: 2026-06-02
# Status: FREEZE_AUDIT_ONLY

---

## Objet

Ce document verrouille les claims autorisés et interdits pour la couche runtime_contracts/.
Ces verrous s'appliquent à toute communication, tout rapport, tout document produit à partir de runtime_contracts/.

---

## INTERDICTIONS — Claims jamais autorisés

| # | Claim interdit | Formulation interdite | Raison |
|---|---------------|----------------------|--------|
| CL-01 | Runtime actif | "runtime_contracts/ est un runtime actif" | Couche docs-only — aucun runtime démarré |
| CL-02 | Packs branchés fichier par fichier | "tous les packs sont branchés" | F03/F06/F07/F10 non encore exécutés |
| CL-03 | Zips importés | "tous les zips sont importés" | F78B = audit readonly uniquement |
| CL-04 | RSSI sécurise automatiquement | "RSSI sécurise automatiquement" | RSSI_EVIDENCE_ONLY boundary — non automatique |
| CL-05 | RGPD conforme | "système RGPD conforme" | F03 RGPD import non exécuté |
| CL-06 | ISO certifié | "ISO 27001 certifié" | Aucune certification auditée |
| CL-07 | NPL prouve | "NPL prouve la vérité" | NPL_ADVISORY_ONLY boundary |
| CL-08 | P107/P161 Lean-proven | "P107/P161 est prouvé Lean" | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY boundary |
| CL-09 | Audio/Entropy prouvé | "Audio/Entropy est prouvé" | AUDIO_ENTROPY_ADVISORY_ONLY — candidat métrique |
| CL-10 | Graphiti/Brody décident | "Graphiti/Brody prennent des décisions" | READONLY_CONTEXT_ONLY — advisory uniquement |
| CL-11 | Education benchmark exécuté | "le benchmark éducatif est exécuté" | P7 = SPEC_ONLY |
| CL-12 | Score réel | "score réel calculé pour un étudiant" | CANDIDATE_ONLY — P7 |
| CL-13 | OS3 produit preuve réelle | "OS3EvidenceTicket est une preuve réelle" | THEORETICAL_ONLY — P5 |
| CL-14 | Hash/seal/Merkle réels | "hash Merkle réel calculé" | PLACEHOLDER_ONLY — modèle théorique |
| CL-15 | Diagnostic éducatif posé | "diagnostic éducatif posé" | NO_DIAGNOSIS boundary |
| CL-16 | Décision scolaire prise | "décision scolaire prise automatiquement" | NO_GRADING_AUTHORITY boundary |
| CL-17 | Comparaison réelle | "Obsidia est meilleur que X" | Aucun dataset réel disponible |

---

## FORMULATIONS AUTORISÉES

| # | Formulation autorisée | Contexte |
|---|----------------------|---------|
| FA-01 | `docs-only` | Nature de runtime_contracts/ |
| FA-02 | `contract skeleton` | Contrats P0 |
| FA-03 | `dry-run spec` | P2/P3 pipelines |
| FA-04 | `readonly wrapper spec` | P6 Graphiti/Brody/NPL |
| FA-05 | `evidence placeholder` | OS3EvidenceTicket P5 |
| FA-06 | `source copied readonly` | F78B audit |
| FA-07 | `future import audit` | F03/F06/F07/F10 |
| FA-08 | `X108 remains sole passage` | Toute action critique |
| FA-09 | `pack branchable later` | Source packs future |
| FA-10 | `CANDIDATE_ONLY` | Scores P7 |
| FA-11 | `THEORETICAL_ONLY` | OS3Evidence, IntentEnvelope P7 |
| FA-12 | `advisory only` | NPL, Cognitive, Atlas |
| FA-13 | `SPEC_ONLY` | Benchmark, pipeline, anti-bypass P7 |
| FA-14 | `PLACEHOLDER_ONLY` | Hash, seal, Merkle P5 |
| FA-15 | `no runtime execution` | Toute confirmation de scope |
| FA-16 | `fail_closed` | Failure modes |
| FA-17 | `no_act` | Boundaries periphery |

---

## Verrous par couche

### Couche P0 — Contrats + Boundaries + Schemas

```
Claim autorisé  : contract skeleton — docs-only
Claim interdit  : runtime actif, packs branchés, RSSI automatique
```

### Couche P2 — External Signals

```
Claim autorisé  : dry-run spec — SIGNAL_ONLY
Claim interdit  : signaux actifs, runtime déclenché
```

### Couche P3 — X108 Gateway

```
Claim autorisé  : dry-run harness spec — X108 sole passage
Claim interdit  : X108 implémenté, gateway réelle active
```

### Couche P4 — Anti-bypass

```
Claim autorisé  : anti-bypass spec — tests futurs
Claim interdit  : tests exécutés, bypass détecté en production
```

### Couche P5 — OS3 Evidence

```
Claim autorisé  : evidence placeholder — THEORETICAL_ONLY
Claim interdit  : OS3 produit preuve réelle, hash réel, Merkle signé
```

### Couche P6 — Readonly Wrappers

```
Claim autorisé  : readonly wrapper spec — advisory only
Claim interdit  : Graphiti/Brody décident, NPL prouve, écriture mémoire
```

### Couche P7 — Education Benchmark

```
Claim autorisé  : dry-run spec — SPEC_ONLY — CANDIDATE_ONLY
Claim interdit  : benchmark exécuté, score réel, diagnostic, notation
```

### Couche F78B/F78C — Source Packs

```
Claim autorisé  : source copied readonly — future import audit
Claim interdit  : tous les zips importés, packs actifs, implémentation complète
```

---

## Règle universelle

```
∀ claim c sur runtime_contracts/ :
  si c ∉ FORMULATIONS_AUTORISÉES → REFUSED
  si c ∈ INTERDICTIONS → REFUSED + FAIL_CLOSED
  si c.scope > DOCS_ONLY → REFUSED
```
