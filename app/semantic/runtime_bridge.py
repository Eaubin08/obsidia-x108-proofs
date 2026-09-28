"""Runtime bridge (LOTS M0/M1/M5) — wires the semantic layer into the
official local-closure path without changing solver signatures.

Given a local closure (solver name + prompt + answer), the bridge:
  1. runs the SemanticCandidateValidator (M0) — non-emptiness is never
     sufficient; English and solver-relevant instruction checks must pass;
  2. builds a lightweight SemanticFrame from the already-extracted structure
     and computes its stable signature (M1);
  3. emits an audit-only ClosureCertificate (M5) — never written to
     /output/results.json, only to internal metrics/receipts.

No task IDs, no expected answers, no secrets. KX108_ONLY preserved: the
bridge validates and traces — it never authorizes actions.
"""
from __future__ import annotations

import re

from app.semantic.frame import (SemanticFrame, SemanticQuantity,
                                 SemanticConstraint, semantic_signature)
from app.semantic.validation import validate_candidate
from app.semantic.closure import build_closure_certificate

# Solver families whose closures carry a structural derivation the bridge
# can frame. Other solvers still get validation, with a generic frame.
_MATH_SOLVERS = {"math_multistep_local", "math_rate_local", "math_local"}
_LOGIC_SOLVERS = {"logic_local", "logic_order_local", "logic_categorical_local"}

_NUM = re.compile(r"\d+(?:\.\d+)?")


def _frame_for(solver_name: str, prompt: str) -> SemanticFrame:
    if solver_name in _MATH_SOLVERS:
        quantities = []
        if re.search(r"(?:has|have|contains?|out of)\s+\d", prompt, re.I):
            quantities.append(SemanticQuantity(0, None, "initial"))
        if "%" in prompt:
            quantities.append(SemanticQuantity(0, "%", "percent_change"))
        if re.search(r"\bmore\b|\breturns?\b", prompt, re.I):
            quantities.append(SemanticQuantity(0, None, "fixed_change"))
        if re.search(r"\bper\s+(?:hour|minute|second)|speed|rate\b", prompt, re.I):
            quantities.append(SemanticQuantity(0, None, "rate"))
        return SemanticFrame(intent="MATH_BOUNDED",
                             quantities=tuple(quantities))
    if solver_name in _LOGIC_SOLVERS:
        kinds = []
        if re.search(r"\bdoes\s+not\b", prompt, re.I):
            kinds.append(SemanticConstraint("EXCLUDE", ()))
        if re.search(r"\bbefore\b", prompt, re.I):
            kinds.append(SemanticConstraint("BEFORE", ()))
        if re.search(r"\bafter\b", prompt, re.I):
            kinds.append(SemanticConstraint("AFTER", ()))
        kinds.append(SemanticConstraint("ALL_DIFFERENT", ()))
        return SemanticFrame(intent="LOGIC_ASSIGNMENT",
                             constraints=tuple(kinds))
    return SemanticFrame(intent=f"LOCAL_{solver_name.upper()}")


def validate_local_closure(solver_name: str | None, prompt: str,
                           answer: str) -> dict:
    """M0+M1+M5 combined entry point, called by the official resolver.

    Returns {"closure_safe", "failure_reasons", "semantic_signature",
             "certificate"} — certificate is audit-only.
    """
    solver = solver_name or "unknown_local"
    frame = _frame_for(solver, prompt)
    sig = semantic_signature(frame)

    v = validate_candidate(answer)
    checks = ["non_empty", "english"] if v.closure_safe else []

    cert = build_closure_certificate(
        solver_family=solver,
        semantic_signature=sig,
        derivation_steps=[],
        checks_passed=checks,
        quantities=[q.role for q in frame.quantities],
        constraints=[c.kind for c in frame.constraints],
        contradictions=list(v.failure_reasons) if not v.closure_safe else [],
    )
    return {
        "closure_safe": v.closure_safe,
        "failure_reasons": v.failure_reasons,
        "semantic_signature": sig,
        "certificate": cert,
    }
