#!/usr/bin/env python3
"""
OBSIDIA — verify_decision.py
Vérifie l'intégrité d'un CanonicalDecisionEnvelope produit par le moteur.

Vérifications effectuées :
  1. Présence des champs obligatoires (domain, x108_gate, decision_id, trace_id)
  2. x108_gate est dans {ALLOW, HOLD, BLOCK}
  3. decision_id et trace_id sont non-vides
  4. attestation_ref est non-vide (preuve de traçabilité)
  5. Si x108_gate == ALLOW → ticket_required == True et ticket_id non-vide

Usage:
  python3 proofs/verify_decision.py <path_to_envelope.json>

Exit code:
  0 → VALID
  1 → INVALID
"""
import json
import sys


REQUIRED_FIELDS = [
    "domain", "market_verdict", "confidence",
    "x108_gate", "reason_code", "severity",
    "decision_id", "trace_id", "attestation_ref", "source",
]

VALID_GATES = {"ALLOW", "HOLD", "BLOCK"}


def verify(file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []

    # 1. Champs obligatoires
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"missing field: {field}")

    if errors:
        print("INVALID")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    # 2. x108_gate valide
    gate = data["x108_gate"]
    if gate not in VALID_GATES:
        errors.append(f"x108_gate '{gate}' not in {VALID_GATES}")

    # 3. decision_id et trace_id non-vides
    if not data.get("decision_id"):
        errors.append("decision_id is empty")
    if not data.get("trace_id"):
        errors.append("trace_id is empty")

    # 4. attestation_ref non-vide
    if not data.get("attestation_ref"):
        errors.append("attestation_ref is empty")

    # 5. ALLOW → ticket obligatoire
    if gate == "ALLOW":
        if not data.get("ticket_required"):
            errors.append("x108_gate=ALLOW but ticket_required is False/missing")
        if not data.get("ticket_id"):
            errors.append("x108_gate=ALLOW but ticket_id is empty")

    if errors:
        print("INVALID")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    print("VALID")
    print(f"  domain      : {data['domain']}")
    print(f"  x108_gate   : {data['x108_gate']}")
    print(f"  verdict     : {data['market_verdict']}")
    print(f"  confidence  : {data['confidence']:.4f}")
    print(f"  decision_id : {data['decision_id']}")
    print(f"  trace_id    : {data['trace_id']}")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_decision.py <path_to_envelope.json>")
        sys.exit(2)
    verify(sys.argv[1])
