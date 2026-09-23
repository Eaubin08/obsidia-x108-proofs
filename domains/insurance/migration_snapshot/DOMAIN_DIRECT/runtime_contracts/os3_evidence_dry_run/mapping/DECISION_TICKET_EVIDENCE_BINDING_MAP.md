# DECISION_TICKET_EVIDENCE_BINDING_MAP
# runtime_contracts/os3_evidence_dry_run/mapping/
# Plan 3 P5 — Binding documentaire DecisionTicket ↔ OS3EvidenceTicket
# Date: 2026-06-02
# Status: OS3_EVIDENCE_SPEC_ONLY

---

## Règle de binding

```
DecisionTicket (X108 → produit) → annote → OS3EvidenceTicket
OS3EvidenceTicket ↛ produit → DecisionTicket
OS3EvidenceTicket ↛ remplace → DecisionTicket

Direction obligatoire :
  X108 produit DecisionTicket d'abord
  OS3EvidenceTicket s'attache ensuite
  Aucun sens inverse admis
```

---

## Table de binding

| Decision field | Evidence binding | Required status | Failure if missing | Claim-scope |
|---------------|-----------------|----------------|-------------------|-------------|
| DecisionTicket.ticket_id | OS3EvidenceTicket.linked_decision_ticket | REQUIRED pour CRITICAL | fail_closed → HOLD (TB-38) | THEORETICAL_ONLY en P5 |
| DecisionTicket.decision (ALLOW/HOLD/BLOCK) | OS3EvidenceTicket.evidence_type=DECISION_TRACE | REQUIRED post-décision | fail_closed → evidence manquante | KX108_ONLY — X108 seul |
| DecisionTicket.reason_codes | OS3EvidenceTicket.reason_codes_trace | RECOMMENDED | advisory seulement | DOCUMENTARY |
| DecisionTicket.x108_gate_status | OS3EvidenceTicket.gate_trace | REQUIRED | fail_closed → HOLD | THEORETICAL_ONLY |
| DecisionTicket.tau_status | OS3EvidenceTicket.temporal_tau_trace | REQUIRED si irréversible | fail_closed → HOLD | THEORETICAL_ONLY |
| DecisionTicket.evidence_ticket_refs[] | ← pointeur vers OS3EvidenceTicket | REQUIRED pour CRITICAL | fail_closed → HOLD | KX108_ONLY |
| DecisionTicket.intent_envelope_ref | OS3EvidenceTicket.intent_ref | REQUIRED | evidence incomplète | THEORETICAL_ONLY |
| DecisionTicket.irreversibility_status | OS3EvidenceTicket.irreversibility_trace | REQUIRED si IRREVERSIBLE | fail_closed → BLOCK | THEORETICAL_ONLY |

---

## Binding détaillé — structure YAML

```yaml
# Binding théorique — documentaire uniquement en P5
decision_ticket_evidence_binding:

  decision_ticket:
    ticket_id: "<ticket_id>-THEORETICAL"
    decision: "ALLOW | HOLD | BLOCK"        # X108 seul
    evidence_ticket_refs: ["EV-<uuid>"]     # référence vers OS3Evidence
    reason_codes: ["<code1>", "<code2>"]
    x108_gate_status: "PASS | FAIL | PENDING"
    tau_status: "CHECKED | NOT_REQUIRED"
    irreversibility_status: "REVERSIBLE | IRREVERSIBLE_GUARDED"
    dry_run: true

  os3_evidence_ticket:
    evidence_id: "EV-<uuid>-THEORETICAL"
    linked_decision_ticket: "<ticket_id>-THEORETICAL"  # ← pointe vers le ticket ci-dessus
    evidence_type: "HASH_CHAIN"
    source: "temporal_receipt_C466"
    hash: "sha256(PLACEHOLDER...)"
    hash_status: "PLACEHOLDER_ONLY"
    replay_status: "NOT_AVAILABLE_IN_P5"
    seal_status: "PLACEHOLDER_ONLY"
    merkle_status: "PLACEHOLDER_ONLY"
    verification_status: "NOT_VERIFIED_IN_P5"
    claim_scope: "THEORETICAL_ONLY"
    dry_run: true
    can_decide: false
    can_emit_act: false

  binding_direction: "OS3Evidence → attaches_to → DecisionTicket"
  binding_condition: "only_after_X108_decides"
  binding_status: "THEORETICAL_ONLY_IN_P5"
```

---

## Cas d'evidence manquante — failure modes

| Scenario | Evidence status | Failure mode | Outcome |
|----------|----------------|-------------|---------|
| CRITICAL intent sans evidence_ticket_refs | MISSING | evidence_missing_for_critical_intent (FM-3) | fail_closed → HOLD |
| DecisionTicket sans linked_decision_ticket | ORPHAN | linked_decision_ticket_missing (FM-5) | fail_closed → HOLD |
| Temporal receipt absent pour irréversible | MISSING | temporal_receipt_missing (FM-11) | fail_closed → HOLD |
| OS3Evidence prétend à décision | INVALID | evidence_ticket_claims_decision (FM-1) | fail_closed → BLOCK |
| OS3Evidence tente d'override X108 | INVALID | evidence_overrides_x108 (FM-19) | fail_closed → BLOCK absolu |
| Evidence manquante → fail_open accepté | INVALID | fail_open_on_missing_evidence (FM-20) | fail_closed → BLOCK |

---

## Evidence non admissibles comme DecisionTicket

```
∀ e ∈ OS3EvidenceTickets : e ↛ ALLOW | HOLD | BLOCK
∀ e ∈ OS3EvidenceTickets : e ↛ ACT
∀ e ∈ OS3EvidenceTickets : e ↛ remplace DecisionTicket
∀ e ∈ OS3EvidenceTickets : e ↛ produit DecisionTicket

Même si :
  e.hash = VERIFIED (futur)
  e.seal = SEALED (futur)
  e.merkle = VERIFIED (futur)
  e.replay = COMPLETED (futur)

→ OS3EvidenceTicket reste une attestation, jamais une décision
→ X108 reste le seul producteur de DecisionTicket
```
