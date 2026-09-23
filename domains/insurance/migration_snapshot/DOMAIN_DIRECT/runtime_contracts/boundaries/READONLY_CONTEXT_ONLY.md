# READONLY_CONTEXT_ONLY
# runtime_contracts/boundaries/READONLY_CONTEXT_ONLY.md
# Status: CONTRACT_SKELETON_ONLY

---

## 1. Boundary Statement

```
Graphiti → readonly uniquement
Brody    → readonly uniquement
NPL      → readonly uniquement
Atlas    → readonly uniquement (future F06)
Cognitive → readonly uniquement (future F07)
∀ module contextuel m : can_write_memory(m) = false
∀ module contextuel m : can_write_graph(m) = false
∀ module contextuel m : can_call_tools(m) = false
∀ module contextuel m : emits_verdict(m) = false
```

---

## 2. Applies To

Graphiti (PYTHON_TESTED), Brody (PYTHON_TESTED), NPL (SPEC_FUTURE), Atlas (COPIED_READONLY — future F06), Cognitive (COPIED_READONLY — future F07), Sigma (PYTHON_TESTED), agents 52 (SOURCE_CANON).

---

## 3. Allowed

- Lire le graphe Graphiti pour enrichir un ContextPacket
- Requêter Brody pour du contexte mémoriel
- Produire NarrativeProvenancePacket NPL advisory
- Fournir des signaux Atlas (F06) ou Cognitive (F07) en ContextPacket
- Fournir du contexte pour enrichir X-108

---

## 4. Forbidden

```
❌ Graphiti write sans gate humain + DecisionTicket ALLOW
❌ Brody write sans gate humain + DecisionTicket ALLOW
❌ Neo4j write sans gate
❌ Appeler un outil externe depuis un module contextuel
❌ Émettre un verdict final depuis contexte
❌ Atlas write (F06) — readonly uniquement
❌ Cognitive write (F07) — readonly uniquement
```

---

## 5. Failure Mode

- `can_write_graph = true` sans gate → reject + fail_closed
- `emits_verdict = true` depuis module contextuel → PLAN3_BACKUP_GUARD_VIOLATION

---

## 6. Required Contract Fields

- `readonly: true` dans ContextPacket
- `can_write_memory: false` dans BoundaryContract
- `can_write_graph: false` dans BoundaryContract

---

## 7. Required Future Tests

- `test_graphiti_write_requires_gate` (existant — graphiti_write=False 650+ tests)
- `test_brody_memory_readonly`
- `test_atlas_readonly_future` (F06)
- `test_cognitive_readonly_future` (F07)

---

## 8. Proof Expectation

- Python tests : graphiti_write=False (195+ tests existants dans tests/api/)
- `P17_AuditGrowth` : audit ne peut que croître — Lean-proven

---

## 9. Claim-Scope

**Autorisé :** "Graphiti, Brody, NPL, Atlas, Cognitive = contexte readonly — X-108 seul modifie"
**Interdit :** "Graphiti peut écrire directement" — INTERDIT sans gate humain + DecisionTicket

---

## 10. Example Violation

```python
graphiti.write_entity(claim)  # ← VIOLATION — sans gate X108
```

---

## 11. Correct Handling

```python
context = graphiti.read_entity(entity_id)  # CORRECT — readonly
packet = ContextPacket(source_layer="graphiti", readonly=True, context_payload=context)
intent = IntentEnvelope(target_domain="graphiti", action_candidate_type="WRITE", ...)
ticket = x108.evaluate(intent)
if ticket.decision == "ALLOW":
    graphiti.write_entity(claim, evidence=ticket.id)  # CORRECT — avec gate
```
