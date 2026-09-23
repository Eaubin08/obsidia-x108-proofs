# X108_GATEWAY_DRY_RUN
# runtime_contracts/dry_run/X108_GATEWAY_DRY_RUN.md
# Status: DRY_RUN_DOCUMENTAIRE / NO_RUNTIME_EXECUTION

---

## Statut

Ce document décrit la future chaîne d'exécution X-108 en mode documentaire uniquement.
Aucun code n'est exécuté. Aucune action réelle n'est déclenchée.
Ce dry-run existe pour préparer la Phase P3 (X108 Gateway Dry-Run Harness).

---

## Chaîne complète documentée (future — non exécutée)

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 1 — RÉCEPTION DU CONTEXTE (PERIPHERIES)                  │
│                                                                   │
│  Graphiti → ContextPacket(readonly=true, advisory=true)          │
│  Brody    → ContextPacket(readonly=true, advisory=true)          │
│  NPL      → ContextPacket(labels=[NPL_ADVISORY_NOT_SOVEREIGN])   │
│  External Signals → PeripheralSignalPacket(EXTERNAL_TEMPORAL)    │
│  P107 advisory → PeripheralSignalPacket(L_value, PYTHON_SPEC..)  │
│  P161 advisory → PeripheralSignalPacket(thermo_debt, PYTHON..)   │
│  Atlas (F06) → ContextPacket(ATLAS_READONLY_FUTURE)              │
│  Cognitive (F07) → ContextPacket(COGNITIVE_ADVISORY_FUTURE)      │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 2 — VALIDATION BOUNDARY                                   │
│                                                                   │
│  CHECK: readonly=true sur tous les ContextPackets                │
│  CHECK: emits_act=false sur tous les packets                     │
│  CHECK: labels présents selon source_layer                       │
│  CHECK: anti_replay_check via External Signals                   │
│  CHECK: stale_execution_check via External Signals               │
│  FAIL: fail_closed si champ critique manquant                    │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 3 — CONSTRUCTION DE L'INTENTENVELOPE                      │
│                                                                   │
│  IntentEnvelope(                                                  │
│    intent_id = uuid(),                                           │
│    source_module = "module_source",                              │
│    irreversibility_level = "REVERSIBLE|PARTIALLY|IRREVERSIBLE",  │
│    criticality_level = "LOW|MEDIUM|HIGH|CRITICAL",               │
│    context_packet_refs = [cp.id for cp in context_packets],     │
│    peripheral_signal_refs = [psp.id for psp in signals],        │
│    requires_x108 = True,                                         │
│    authority = "KX108_ONLY",                                     │
│    emits_act = False                                             │
│  )                                                               │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 4 — PRECHECK FAIL-CLOSED AVANT X108                       │
│                                                                   │
│  IF irreversibility_level is None → HOLD (fail_closed)          │
│  IF authority != KX108_ONLY → REJECT                            │
│  IF external_signals.anti_replay = FAIL → flag + pénalité       │
│  IF source_status = UNKNOWN → flag + pénalité                   │
│  IF schema invalide → REJECT                                     │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 5 — SOUMISSION AU GATEWAY X108 (DRY-RUN)                 │
│                                                                   │
│  x108_gateway.evaluate(intent_envelope)                          │
│  ↓                                                               │
│  Évalue les 28 invariants Lean-proven applicables               │
│  Évalue tau_status pour actions irréversibles                    │
│  Évalue consensus (aggregate4_fail_closed)                       │
│  Évalue tous les ContextPackets et signaux                       │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 6 — PRODUCTION DU DECISIONTICKET (DRY-RUN)               │
│                                                                   │
│  DecisionTicket(                                                  │
│    decision = ALLOW | HOLD | BLOCK,  ← X108 seul décide         │
│    priority = "BLOCK > HOLD > ALLOW",                            │
│    input_hash = sha256(action_candidate),                        │
│    output_hash = sha256(envelope),                               │
│    trace_hash = sha256({input+output+packet}),                   │
│    merkle_root = sha256([ih, oh, th]),                           │
│    replay_status = "NOT_RUN",                                    │
│    tau_status = TAU_ELAPSED | TAU_PENDING | TAU_NOT_APPLICABLE  │
│  )                                                               │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 7 — ATTACHEMENT OS3EVIDENCETICKET                         │
│                                                                   │
│  OS3EvidenceTicket(                                              │
│    linked_decision_ticket = decision_ticket.id,                  │
│    hash = sha256(decision_ticket),                               │
│    merkle_status = VALID,                                        │
│    replay_status = NOT_RUN,                                      │
│    verification_status = VERIFIED | UNVERIFIED                   │
│  )                                                               │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  PHASE 8 — NO WORLD EXECUTION (DRY-RUN ONLY)                    │
│                                                                   │
│  Si decision = ALLOW (dry-run) :                                 │
│    → NE PAS exécuter l'action réelle                             │
│    → Logger le résultat du dry-run                               │
│    → Retourner (decision_ticket, os3_evidence_ticket) pour audit │
│                                                                   │
│  Si decision = HOLD → Logger HOLD + reason_codes                 │
│  Si decision = BLOCK → Logger BLOCK + reason_codes               │
│                                                                   │
│  AUCUNE ACTION MONDE RÉEL EN DRY-RUN                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Invariants Lean-proven actifs dans la chaîne

| Phase | Invariant | Théorème |
|-------|-----------|---------|
| 4 | Fail-closed | `aggregate4_fail_closed` |
| 4 | No ACT sous seuil | `E2_no_act_below_threshold` |
| 5 | Gate temporelle | `X108_no_act_before_tau` |
| 5 | Kernel jamais BLOCK | `X108_kernel_never_blocks` |
| 5 | Déterminisme | `D1_determinism` |
| 6 | Hash chain | `merkleRoot_change_if_leaf_change`, `P13_Immutability` |
| 6 | Consensus | `aggregate4_unanimous` |
| 6 | Audit growth | `P17_AuditGrowth` |

---

## Prérequis Phase P3

1. schemas JSON validés (P1)
2. Boundaries spécifiques créées (P1) — incluant COGNITIVE, ATLAS, RSSI, RGPD
3. Tests unitaires de base (P1)
4. X108 Gateway Dry-Run Harness (P3) — futur code dry-run
