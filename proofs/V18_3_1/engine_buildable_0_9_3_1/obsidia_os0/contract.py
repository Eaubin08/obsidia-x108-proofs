from __future__ import annotations
from typing import Any, List, Tuple
from . import ir

# ===== L2.5 Contract rules R1-R10 (validator) =====
# Note: Règles sont appliquées structurellement au programme IR.
# Le runner applique aussi des sanctions runtime (rollback/blockage etc) via exceptions.

Violation = Tuple[str, str]  # (Rule, message)

class ContractViolationError(Exception):
    """Levée si le programme viole au moins une règle R1-R10."""
    def __init__(self, violations: List[Violation]):
        self.violations = violations
        msgs = "; ".join(f"[{r}] {m}" for r, m in violations)
        super().__init__(f"Contract violations ({len(violations)}): {msgs}")


def validate(program: Any) -> List[Violation]:
    """Vérifie les règles R1-R10.

    Retourne la liste des violations si le programme est valide (liste vide).
    Lève ContractViolationError si au moins une règle est violée.
    """
    v: List[Violation] = []
    _walk(program, v)
    if v:
        raise ContractViolationError(v)
    return v

def _walk(node: Any, v: List[Violation]):
    # Accept list as top-level
    if isinstance(node, list):
        for n in node:
            _walk(n, v)
        return

    # R10: hors alphabet = inexistant (ici: hors classes IR connues)
    allowed = (
        ir.VALUE, ir.STATE, ir.READ, ir.WRITE, ir.FLOW, ir.COND, ir.LOOP,
        ir.CALL, ir.RETURN, ir.EVENT, ir.TIME
    )
    if not isinstance(node, allowed):
        v.append(("R10", f"Hors-alphabet: {type(node).__name__}"))
        return

    # R1: Toute info/action opère sur STATE (structurel: READ/WRITE exigent STATE)
    if isinstance(node, ir.READ) and not isinstance(node.state, ir.STATE):
        v.append(("R1", "READ doit viser un STATE"))
    if isinstance(node, ir.WRITE) and not isinstance(node.state, ir.STATE):
        v.append(("R1", "WRITE doit viser un STATE"))

    # R2: READ -> VALUE (structurel: READ node ok; runtime checks in runner)
    # R3: WRITE modifie un STATE (runtime: no side effects outside env)
    # R4: CALL -> RETURN ou ERROR (runtime)
    # R5: toute bifurcation via COND (structurel: LOOP has COND; if user wants IF, represent as COND+FLOW)
    if isinstance(node, ir.LOOP) and not isinstance(node.cond, ir.COND):
        v.append(("R5", "LOOP doit utiliser COND"))
    # R6: LOOP doit avoir une sortie : enforce via max_iters
    if isinstance(node, ir.LOOP) and (node.max_iters is None or node.max_iters <= 0):
        v.append(("R6", "LOOP doit avoir max_iters > 0"))
    # R7: EVENT externe et horodaté: encourage t not None
    if isinstance(node, ir.EVENT) and node.t is None:
        v.append(("R7", f"EVENT '{node.name}' sans timestamp"))
    # R8: TIME impose l'ordre (runtime)
    # R9: ERROR traçable et bloquante (runtime)

    # Recurse
    if isinstance(node, ir.FLOW):
        for s in node.steps:
            _walk(s, v)
    elif isinstance(node, ir.LOOP):
        _walk(node.cond, v)
        for s in node.body:
            _walk(s, v)
    elif isinstance(node, ir.CALL):
        for a in node.args:
            _walk(a, v) if isinstance(a, (allowed, list)) else None
    elif isinstance(node, ir.WRITE):
        _walk(node.value, v) if isinstance(node.value, allowed) else None
    elif isinstance(node, ir.COND):
        # expr may be callable or tuple; can't validate deeper safely
        pass
