# X108_GATEWAY_DRY_RUN_HARNESS_SPEC
# runtime_contracts/x108_gateway_dry_run_harness/specs/
# Plan 3 P3 — Spec documentaire uniquement — NO RUNTIME EXECUTION
# Date: 2026-06-02
# Status: HARNESS_DOCUMENTATION_ONLY / DRY_RUN_SPEC_ONLY

---

## 1. Purpose

Ce document spécifie la structure documentaire du futur X108 Gateway Dry-Run Harness.

Le harness est un outil de **validation logique documentaire** qui simule le passage
d'une IntentEnvelope à travers le gateway X-108 **sans jamais l'exécuter réellement**.

Il permet de vérifier sur papier :
- qu'un IntentEnvelope est correctement formé
- que les ContextPackets référencés sont complets et readonly
- que les PeripheralSignalPackets ne prétendent pas à la souveraineté
- que la forme théorique du DecisionTicket produit par X108 respecte les invariants
- que tout failure → fail_closed

---

## 2. Status

```
Status:                     HARNESS_DOCUMENTATION_ONLY
Runtime execution:          NO
DecisionTicket réel:        NO
ACT émis:                   NO
Tool call:                  NO
Memory write:               NO
Graphiti write:             NO
Brody write:                NO
Adapter actif:              NO
Packages:                   NO
Python files:               NO
World action:               NO
Commit:                     NO
Push:                       NO
Zips décompressés:          NO
Source packs extraits:      PARTIELLEMENT (External Signals only — F04)
F78B validé:                NON — required before F03/F06/F07/F10
```

---

## 3. Inputs du harness (documentaires)

| Input | Type | Source | Requis | Statut actuel |
|-------|------|--------|--------|---------------|
| IntentEnvelope candidate | JSON shape | module périphérique (spec only) | OUI | SPEC_ONLY |
| ContextPacket(s) | ContextPacket[] | External Signals, Graphiti, Brody, NPL, Atlas (future), Cognitive (future) | OUI ≥1 | SPEC_IMPORTED (External Signals) / SPEC_ONLY (autres) |
| PeripheralSignalPacket(s) | PeripheralSignalPacket[] | External Signals, NPL métriques, P107/P161 advisories | NON | SPEC_ONLY |
| External Signals temporal context | PeripheralSignalPacket + ContextPacket | 51/53 packets | OUI pour test temporel | SPEC_IMPORTED |
| NPL advisory labels | ContextPacket | specs/12_NARRATIVE_PROVENANCE_LAYER/ | OUI si NPL enrichi | SPEC_ONLY |
| P107/P161 advisory metrics | PeripheralSignalPacket | specs/03_ENTROPY_DISCIPLINE/ | NON — advisory uniquement | PYTHON_SPEC_NOT_LEAN_PROVEN |
| Audio/Entropy advisory metrics | ContextPacket | specs/03_ENTROPY_DISCIPLINE/ | NON — source candidate | SOURCE_PARTIAL |
| Cognitive advisory context | ContextPacket (future) | _source_packs/raw/ (non extrait) | NON | COPIED_READONLY — F07 required |
| Atlas readonly context | ContextPacket (future) | _source_packs/raw/ (non extrait) | NON | COPIED_READONLY — F06 required |
| RSSI evidence context | OS3EvidenceTicket (future) | _source_packs/raw/ (non extrait) | NON | COPIED_READONLY — F03+F78B required |
| RGPD compliance guard | BoundaryContract (future) | _source_packs/raw/ (non extrait) | NON | COPIED_READONLY — F03+F10+F78B required |
| Tau status | string | X108 temporal kernel | OUI pour irréversible | KERNEL_ONLY |
| OS3EvidenceTicket refs | string[] | temporal_receipt (P2) | OUI pour CRITICAL | SPEC_ONLY |

---

## 4. Outputs théoriques (documentaires uniquement)

| Output | Type | Qui produit | Interdiction |
|--------|------|------------|-------------|
| Theoretical DecisionTicket shape | JSON shape doc | X108 seul (jamais le harness) | harness ne produit jamais ALLOW/HOLD/BLOCK réels |
| Theoretical OS3EvidenceTicket binding | JSON shape doc | OS3 (jamais le harness) | harness décrit uniquement le lien ticket → evidence |
| Validation report documentaire | Markdown | harness spec | report ne constitue pas une décision |
| Failure mode report | Markdown | harness spec | aucun fail_closed réel — documentaire seulement |

---

## 5. Required contracts

| Contrat | Rôle dans harness |
|---------|------------------|
| IntentEnvelope.contract.md | Structure de l'input |
| ContextPacket.contract.md | Contexte readonly |
| PeripheralSignalPacket.contract.md | Signaux non souverains |
| DecisionTicket.contract.md | Forme théorique de la sortie X108 |
| OS3EvidenceTicket.contract.md | Binding evidence théorique |
| BoundaryContract.contract.md | Droits modules |
| RuntimeAdmissionContract.contract.md | Conditions DRY_RUN admission |

---

## 6. Required schemas

| Schema | Usage |
|--------|-------|
| intent_envelope.schema.json | Validation documentaire structure |
| context_packet.schema.json | Validation documentaire structure |
| peripheral_signal_packet.schema.json | Validation documentaire structure |
| decision_ticket.schema.json | Forme théorique attendue |
| os3_evidence_ticket.schema.json | Binding evidence théorique |
| boundary_contract.schema.json | Droits module admis |
| runtime_admission_contract.schema.json | Critères admission SPEC→DRY_RUN |

---

## 7. Required boundaries

| Boundary | Rôle |
|----------|------|
| NO_ACT_FROM_PERIPHERY | Aucune périphérie ne déclenche d'ACT |
| X108_GATEWAY_REQUIRED | Toute décision → X108 |
| FAIL_CLOSED_PRIORITY | Tout failure → fail_closed |
| READONLY_CONTEXT_ONLY | Graphiti/Brody/Atlas = lecture uniquement |
| EXTERNAL_SIGNALS_SIGNAL_ONLY | Signaux temporels = advisory uniquement |
| NPL_ADVISORY_ONLY | NPL = enrichissement contexte, jamais verdict |
| P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY | P107/P161 = python spec, non Lean-prouvé |
| AUDIO_ENTROPY_ADVISORY_ONLY | Audio/Entropy = source candidate, pas loi |
| COGNITIVE_REINTEGRATION_ADVISORY_ONLY | Cognitive = COPIED_READONLY, F07 required |
| ATLAS_READONLY_ADVISORY_ONLY | Atlas = COPIED_READONLY, F06 required |
| RSSI_EVIDENCE_ONLY | RSSI = evidence non certifié, F03+F78B required |
| RGPD_COMPLIANCE_SCOPE_GUARD | RGPD = scope guard, pas certification |
| NO_PACKAGES_RUNTIME_BOUNDARY | Aucun package Python actif |

---

## 8. Dry-run admission chain (documentaire)

```
SPEC_ONLY → [RuntimeAdmissionContract check] → DRY_RUN_ELIGIBLE
                                                  ↓
                                        IntentEnvelope candidate
                                        + ContextPacket refs ≥1
                                        + boundary X108_GATEWAY_REQUIRED
                                        + requires_x108 = true
                                                  ↓
                                        X108 Gateway Dry-Run Harness
                                        (simulation documentaire)
                                                  ↓
                                        Theoretical DecisionTicket shape
                                        + invariants checked
                                        + failure modes logged
                                                  ↓
                                        NO_WORLD_ACTION
                                        (aucun ACT, aucune écriture, aucun push)
```

Condition de blocage à toute étape :
```
si invariant violé → fail_closed
si boundary violée → fail_closed
si source_pack non audité par F78B → block F03/F06/F07/F10
si P107/P161 claim LEAN_PROVEN → fail_closed (non prouvé)
si RSSI/RGPD claim CERTIFIED → fail_closed (non certifié)
```

---

## 9. X108 authority model

```
Seul producteur de DecisionTicket : X108 kernel
Seule source de ALLOW/HOLD/BLOCK : X108 kernel
Priorité absolue : BLOCK > HOLD > ALLOW

Toute périphérie :
  advisory_only = true
  emits_act = false
  emits_verdict = false
  decision_authority = KX108_ONLY

Invariants kernel utilisés :
  D1_DETERMINISM       — entrée identique → sortie identique
  E2_NO_ACT            — pas d'action sans décision explicite
  aggregate4_fail_closed — BLOCK > HOLD > ALLOW absolu
  X108_NO_ACT_BEFORE_TAU — irréversible → tau check obligatoire
  skew_negative_implies_hold — skew temporel négatif → HOLD
```

---

## 10. DecisionTicket theoretical generation

Le harness P3 décrit la **forme théorique** du DecisionTicket que X108 produirait.
Il ne produit **jamais** un ticket réel.

```yaml
# Forme théorique — documentaire uniquement
theoretical_decision_ticket:
  ticket_id: "DT-<uuid>-THEORETICAL"
  intent_envelope_ref: "<intent_envelope_id>"
  decision: "ALLOW | HOLD | BLOCK"   # X108 seul décide
  decision_priority: "BLOCK > HOLD > ALLOW"
  reason_codes: ["<code1>", "<code2>"]
  x108_gate_status: "PASS | FAIL | PENDING"
  tau_status: "CHECKED | NOT_REQUIRED | FAIL"
  irreversibility_status: "REVERSIBLE | IRREVERSIBLE_GUARDED"
  context_packet_count: <n>
  peripheral_signal_count: <n>
  evidence_ticket_refs: ["<os3_evidence_id>"]
  claim_scope: "THEORETICAL_ONLY"
  dry_run: true
  # JAMAIS emis par le harness P3
  # JAMAIS ALLOW/HOLD/BLOCK réels
  # Seulement shape documentaire
```

---

## 11. OS3EvidenceTicket theoretical binding

```yaml
# Binding théorique — documentaire uniquement
theoretical_os3_evidence:
  evidence_id: "EV-<uuid>-THEORETICAL"
  linked_decision_ticket: "<theoretical_decision_ticket_id>"
  evidence_type: "HASH_CHAIN | REPLAY_LOG | SEAL"
  source: "temporal_receipt_C466 | os3_kernel"
  hash: "sha256(<intent_id>+<tick>+<nonce>)"
  replay_status: "NOT_RUN"           # P3 ne rejoue pas
  verification_status: "UNVERIFIED"  # honnête — non vérifié P3
  seal_status: "NOT_SEALED"          # P3 ne scelle pas
  claim_scope: "THEORETICAL_ONLY"
  dry_run: true
  # Invariants futurs : P13_Immutability, merkleRoot_change_if_leaf_change, P17_AuditGrowth
```

---

## 12. Allowed operations (harness P3)

```
✅ Lire des fichiers specs/external_signals/
✅ Lire des fichiers runtime_contracts/
✅ Créer des fichiers .md documentaires dans x108_gateway_dry_run_harness/
✅ Décrire la forme d'un IntentEnvelope valide
✅ Décrire la forme théorique d'un DecisionTicket
✅ Documenter les conditions de fail_closed
✅ Lister les boundaries requises
✅ Créer des exemples JSON documentaires en Markdown
✅ Créer des rapports de traçabilité
```

---

## 13. Forbidden operations (harness P3)

```
❌ Exécuter X108 réel
❌ Produire un DecisionTicket réel (ALLOW/HOLD/BLOCK)
❌ Émettre ACT
❌ Appeler un outil réel
❌ Écrire mémoire / Graphiti / Brody
❌ Déclencher une action monde réel
❌ Modifier kernel, periphery, proofs, formal, sigma, tests
❌ Créer fichier .py
❌ Créer packages/
❌ Décompresser un zip
❌ Importer un source pack sans F78B
❌ Prétendre que Cognitive/Atlas/RSSI/RGPD sont runtime-ready
❌ Prétendre que P107/P161 sont Lean-prouvés
❌ Prétendre que RSSI/RGPD sont certifiés/conformes
❌ Prétendre que les zips sont tous extraits
❌ Committer / pousser
❌ Lancer F03/F06/F07/F10 sans F78B
```

---

## 14. Failure modes (résumé)

23 failure modes documentaires — voir `failure_modes/X108_GATEWAY_DRY_RUN_HARNESS_FAILURE_MODES.md`.
Règle universelle : `fail_closed / no_act / requires_x108_review / never_allow_by_default`.

---

## 15. Claim-scope locks

| Composant | Claim autorisé | Claim interdit |
|-----------|---------------|----------------|
| External Signals | SIGNAL_ONLY / TEMPORAL_PREFILTER | décision, autorisation |
| NPL | ADVISORY_ONLY / enrichissement contexte | verdict, NPL_PROVES |
| P107/P161 | PYTHON_SPEC_ADVISORY | LEAN_PROVEN, autorité runtime |
| Audio/Entropy | SOURCE_CANDIDATE / advisory metric | loi physique certifiée |
| Cognitive | COPIED_READONLY / F07_PENDING | runtime-ready, branchable actif |
| Atlas | COPIED_READONLY / F06_PENDING | runtime-ready, branchable actif |
| RSSI | COPIED_READONLY / F03_F78B_PENDING | certifié, sécurité prouvée |
| RGPD | COPIED_READONLY / F03_F10_F78B_PENDING | conforme, ISO certifié |
| DecisionTicket | KX108_ONLY | tout autre producteur |
| OS3EvidenceTicket | HASH_CHAIN / SPEC_ONLY (P3) | sealed, replay vérifié (P3) |

---

## 16. Future implementation gates

| Gate | Description | Prérequis |
|------|-------------|-----------|
| P4 | Anti-bypass tests SPEC | P3 ✅ |
| P5 | OS3 Evidence Ticket dry-run SPEC | P3 ✅ |
| P6 | Graphiti/Brody/NPL readonly wrappers SPEC | P3 ✅ |
| P7 | Education benchmark dry-run SPEC | P3 ✅ |
| **F78B** | **SOURCE_PACKS_DEEP_DIFF_AUDIT** | **obligatoire avant F03/F06/F07/F10** |
| F03 | RSSI + RGPD import | F78B ✅ |
| F06 | Atlas import | F78B ✅ |
| F07 | Cognitive import | F78B ✅ |
| F10 | RGPD final compliance | F03 ✅ |

---

## 17. F78B source-pack deep diff gate

```
F78B = SOURCE_PACKS_DEEP_DIFF_AUDIT

Statut actuel (2026-06-02) :
  SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_101014/ présent dans root
  → processus externe amorcé
  → non validé par ce run
  → contenu non inspecté par P3

F78B doit produire pour chaque zip :
  ZIP_SOURCE           — chemin exact du zip
  FILES_INTERNAL       — liste des fichiers internes
  ALREADY_EXTRACTED?   — partiellement ou totalement
  LOCAL_PATH?          — chemin local si extrait
  KEEP?                — à conserver dans repo
  INTEGRATE?           — à intégrer dans specs/
  ARCHIVE_ONLY?        — seulement en archive
  COLLISION?           — conflits avec specs/ existants
  CLAIM_SCOPE?         — scope admissible du contenu
  BOUNDARY_REQUIRED?   — boundary spécifique nécessaire

Zips concernés (non tous extraits) :
  OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL(1).zip — 513 fichiers
  OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS.zip           — 1738 fichiers
  OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1.zip              — 167 fichiers
  OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2.zip                 — 280 fichiers

Interdiction jusqu'à F78B validé :
  Ne pas importer ces zips dans specs/
  Ne pas créer d'adapter pour leur contenu
  Ne pas prétendre que leur contenu est runtime-ready
```

---

## 18. Tests required later (P4)

```
test_intent_without_x108_gate_fails
test_peripheral_cannot_emit_decision
test_external_signal_cannot_authorize_act
test_npl_advisory_only_no_verdict
test_p107_p161_not_proven_claim_blocked
test_rssi_not_certified_claim_blocked
test_rgpd_not_certified_claim_blocked
test_cognitive_atlas_not_runtime_ready_claim_blocked
test_fail_closed_on_missing_context
test_fail_closed_on_stale_temporal
test_source_pack_without_f78b_blocked
test_dry_run_no_world_action
```

---

## 19. Proof expected later

```
Lean proofs attendus (post-P4) :
  periphery_non_sovereign_invariant
  x108_sole_decision_authority
  fail_closed_aggregate4
  temporal_tau_check_before_irreversible

TLA+ specs attendues (post-P5) :
  X108GatewaySpec.tla
  DecisionTicketInvariant.tla
  FailClosedProperty.tla
```
