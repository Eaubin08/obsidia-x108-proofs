# X108_GATEWAY_REQUIRED
# runtime_contracts/boundaries/X108_GATEWAY_REQUIRED.md
# Status: CONTRACT_SKELETON_ONLY

---

## 1. Boundary Statement

```
∀ intention critique I : I → IntentEnvelope → X108_GATEWAY → DecisionTicket
∀ action irréversible A : A ne s'exécute pas sans DecisionTicket(ALLOW) + tau_status(TAU_ELAPSED)
∀ module m : bypass(X108) ↛ admissible
X108 = seul droit de passage pour ACT / ALLOW / HOLD / BLOCK
```

---

## 2. Applies To

Toute intention impliquant :
- une écriture mémoire (Graphiti write, Brody write, Neo4j write)
- une action monde réel (GPS actuator, aviation, bank transaction)
- une émission de valeur (Gencoin mint)
- une modification d'état irréversible
- un appel d'outil (tool_call) avec effet de bord

---

## 3. Allowed

- IntentEnvelope → X108 → DecisionTicket → action (si ALLOW)
- Modules périphériques → ContextPacket → X108 (information seulement)
- Dry-run de la chaîne complète sans action réelle

---

## 4. Forbidden

```
❌ Action critique sans IntentEnvelope
❌ Action sans DecisionTicket ALLOW
❌ Action irréversible sans tau_status = TAU_ELAPSED
❌ Bypass X108 par LLM, NPL, Brody, Graphiti, External Signals, Atlas, Cognitive
❌ Modification d'état machine sans gate
❌ Écriture mémoire sans gate humain + X108
```

---

## 5. Failure Mode

| Situation | Comportement |
|-----------|-------------|
| Intention sans IntentEnvelope | Reject → fail_closed |
| Action critique sans DecisionTicket | `no_act` → fail_closed |
| IRREVERSIBLE sans tau_status | `X108_no_act_before_tau` → HOLD |
| Bypass détecté | BLOCK + audit flag |

---

## 6. Required Contract Fields

- `requires_x108: true` dans IntentEnvelope (obligatoire)
- `x108_gate_status` dans DecisionTicket (obligatoire)
- `tau_status` dans DecisionTicket pour irréversible

---

## 7. Required Future Tests

- `test_no_actuator_without_decisionticket` (existant — étendre)
- `test_intent_envelope_requires_x108`
- `test_bypass_x108_detected_block`

---

## 8. Proof Expectation

- `X108_no_act_before_tau` : Lean-proven dans `TemporalKernel.lean`
- `X108_kernel_never_blocks` : Lean-proven
- `aggregate4_fail_closed` : Lean-proven

---

## 9. Claim-Scope

**Autorisé :** "X-108 est le seul point de passage pour toute décision d'action"
**Interdit :** "X-108 peut être bypassed dans des cas exceptionnels" — INTERDIT ABSOLU

---

## 10. Example Violation

```python
# VIOLATION
def execute_gps_trajectory(coords):
    if confidence > 0.9:
        actuate(coords)  # ← BYPASS X108 → VIOLATION
```

---

## 11. Correct Handling

```python
# CORRECT
def propose_gps_trajectory(coords, context_packets):
    intent = IntentEnvelope(
        action_candidate_type="EXECUTE",
        target_domain="gps",
        irreversibility_level="IRREVERSIBLE",
        requires_x108=True,
        context_packet_refs=[cp.id for cp in context_packets]
    )
    ticket = x108_gateway.evaluate(intent)
    if ticket.decision == "ALLOW" and ticket.tau_status == "TAU_ELAPSED":
        actuate(coords, evidence=ticket.evidence_ticket_refs)
```
