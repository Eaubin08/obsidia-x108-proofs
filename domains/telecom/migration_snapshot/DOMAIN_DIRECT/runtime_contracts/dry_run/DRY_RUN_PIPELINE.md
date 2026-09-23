# DRY_RUN_PIPELINE
# runtime_contracts/dry_run/DRY_RUN_PIPELINE.md
# Status: DRY_RUN_DOCUMENTAIRE / NO_RUNTIME_EXECUTION

---

## Pipeline futur documenté (8 étapes)

### Étape 1 — Receive Peripheral Context

**Input :** Signaux de toutes les couches périphériques actives.

```
Sources actives (Plan 3 P0 état) :
  ✅ Brody    → ContextPacket (PYTHON_TESTED, readonly)
  ✅ Graphiti → ContextPacket (PYTHON_TESTED, readonly)
  ✅ Sigma    → ContextPacket (PYTHON_TESTED, readonly)
  ✅ External Signals → PeripheralSignalPacket (SPEC_IMPORTED F04)
  ⬜ NPL     → NarrativeProvenancePacket (SPEC_FUTURE — P6)
  ⬜ Atlas   → ContextPacket (COPIED_READONLY — F06/P2)
  ⬜ Cognitive → ContextPacket (COPIED_READONLY — F07/P2)
  ⬜ P107 advisory → PeripheralSignalPacket (PYTHON_SPEC_NOT_LEAN_PROVEN)
  ⬜ P161 advisory → PeripheralSignalPacket (PYTHON_SPEC_NOT_LEAN_PROVEN)
  ⬜ Audio/Entropy → PeripheralSignalPacket (SOURCE_PARTIAL)
```

**Boundary :** READONLY_CONTEXT_ONLY, NO_ACT_FROM_PERIPHERY.

---

### Étape 2 — Validate Boundary

**Action :** Vérifier que chaque packet respecte sa boundary.

```
CHECK list :
  ✓ readonly = true → ContextPacket
  ✓ advisory_only = true → tous packets
  ✓ emits_act = false → tous packets
  ✓ decision_authority = KX108_ONLY → tous packets
  ✓ labels présents selon source_layer
  ✓ source_status déclaré explicitement
  ✓ confidence ≤ 0.99 si source_status ≠ LEAN_PROVEN
  
FAIL : fail_closed si champ critique manquant
```

---

### Étape 3 — Build IntentEnvelope

**Action :** Structurer l'intention avec tous les contextes validés.

```python
# FUTUR — non exécuté en P0
intent = IntentEnvelope(
    intent_id = uuid(),
    source_module = requesting_module.name,
    action_candidate_type = classify_action(request),
    target_domain = target_domain,
    irreversibility_level = assess_irreversibility(request),
    criticality_level = assess_criticality(request),
    context_packet_refs = [cp.id for cp in validated_context_packets],
    peripheral_signal_refs = [psp.id for psp in validated_signals],
    timestamp_or_tick_context = current_tick(),
    requires_x108 = True,
    authority = "KX108_ONLY",
    emits_act = False,
    source_status = requesting_module.source_status,
    claim_scope = derive_claim_scope(requesting_module.source_status)
)
```

---

### Étape 4 — Apply Fail-Closed Precheck

**Action :** Appliquer toutes les règles FAIL_CLOSED_PRIORITY avant soumission.

```
PRECHECK :
  IF intent.irreversibility_level is None → fail_closed → HOLD
  IF intent.authority != "KX108_ONLY" → reject
  IF intent.emits_act != False → violation
  IF external_signals.anti_replay == "FAIL" → flag + continue with penalty
  IF external_signals.stale_execution == "FAIL" → fail_closed
  IF intent.source_status == "UNKNOWN_SOURCE" → unknown_source_flag = true
  IF intent.schema_valid() == False → reject → fail_closed
  IF intent.criticality_level == "CRITICAL" and len(context_packet_refs) == 0 → reject
```

---

### Étape 5 — Submit to X108 Dry-Run

**Action :** Soumettre l'IntentEnvelope validé au gateway X-108 (futur dry-run harness — P3).

```
x108_gateway.evaluate_dry_run(intent)
  ↓
Applique les 28 invariants Lean-proven applicables
Évalue tau_status pour actions IRREVERSIBLE
Applique consensus (aggregate4_fail_closed)
Pondère les ContextPackets par source_status + confidence
Pondère les signaux advisory (P107/P161/NPL/External Signals)
```

---

### Étape 6 — Produce DecisionTicket

**Action :** X-108 produit le DecisionTicket avec ALLOW, HOLD, ou BLOCK.

```
ticket = DecisionTicket(
    decision = x108.decide(),  # ALLOW | HOLD | BLOCK — X108 seul
    decision_priority = "BLOCK > HOLD > ALLOW",
    input_hash = sha256(action_candidate),
    output_hash = sha256(envelope),
    trace_hash = sha256({input+output+packet}),
    merkle_root = sha256([input_hash, output_hash, trace_hash]),
    replay_status = "NOT_RUN",
    tau_status = x108.tau_status()
)
```

---

### Étape 7 — Attach OS3EvidenceTicket

**Action :** Attacher la preuve à la décision.

```
evidence = OS3EvidenceTicket(
    linked_decision_ticket = ticket.id,
    hash = sha256(ticket),
    merkle_status = "VALID",
    replay_status = "NOT_RUN",
    verification_status = "VERIFIED"
)
```

---

### Étape 8 — No World Execution (DRY-RUN BOUNDARY)

**Action :** Retourner le résultat sans exécuter d'action réelle.

```
DRY-RUN ONLY :
  IF decision == "ALLOW" → LOG + return (ticket, evidence) — NO ACTUATE
  IF decision == "HOLD"  → LOG HOLD + reason_codes
  IF decision == "BLOCK" → LOG BLOCK + reason_codes + audit

INTERDIT EN DRY-RUN :
  ❌ Écrire en mémoire
  ❌ Appeler un actuateur GPS
  ❌ Émettre du Gencoin
  ❌ Écrire Graphiti
  ❌ Modifier l'état machine
  ❌ Envoyer des transactions
```

---

## Statut par étape — Plan 3 P0

| Étape | Disponibilité | Prérequis |
|-------|--------------|-----------|
| 1. Receive context | Partiellement (Brody/Graphiti/Sigma existants) | P6 pour NPL, F06 pour Atlas |
| 2. Validate boundary | Documentaire P0 | Tests P1 |
| 3. Build IntentEnvelope | Documentaire P0 | Schema validation P1 |
| 4. Fail-closed precheck | Documentaire P0 | Code P3 |
| 5. X108 dry-run | FUTUR P3 | P3 Harness |
| 6. DecisionTicket | FUTUR P3 | P3 Harness |
| 7. OS3EvidenceTicket | FUTUR P5 | P5 dry-run |
| 8. No world execution | Documentaire P0 | Enforcement code P3 |
