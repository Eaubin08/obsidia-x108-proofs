"""Bounded ConstraintGraph — deterministic finite-domain assignment solver.

Supports the bounded constraint kinds needed by the public router's logic
family. Search is strictly bounded (MAX_ENTITIES/MAX_DOMAIN, so at most
6! = 720 permutations) and deterministic (entities and domain values keep
insertion order). Local closure requires a unique solution; zero or several
solutions mean abstention; a contradictory graph means abstention.

This module is the solver. Regex or frame extraction feeds it — it never
matches surface text itself.
"""
from __future__ import annotations

from itertools import permutations

SUPPORTED_KINDS = frozenset({
    "EQUAL", "NOT_EQUAL", "ASSIGN", "EXCLUDE", "ALL_DIFFERENT",
    "BEFORE", "AFTER", "IMPLIES", "REQUIRES",
})

MAX_ENTITIES = 6
MAX_DOMAIN = 6


class ContradictionError(ValueError):
    """The constraint set is unsatisfiable by construction."""


class ConstraintGraph:
    def __init__(self) -> None:
        self._entities: list[str] = []
        self._domain: list[str] = []
        self._constraints: list[tuple[str, tuple[str, ...]]] = []
        self._derivation: list[str] = []

    # ── construction ────────────────────────────────────────────────────────
    def add_entity(self, name: str) -> None:
        key = name.lower()
        if key not in self._entities:
            if len(self._entities) >= MAX_ENTITIES:
                raise ValueError(f"entity bound exceeded ({MAX_ENTITIES})")
            self._entities.append(key)

    def add_domain(self, value: str) -> None:
        key = value.lower()
        if key not in self._domain:
            if len(self._domain) >= MAX_DOMAIN:
                raise ValueError(f"domain bound exceeded ({MAX_DOMAIN})")
            self._domain.append(key)

    def add_constraint(self, kind: str, *operands: str) -> None:
        if kind not in SUPPORTED_KINDS:
            raise ValueError(f"unsupported constraint kind: {kind}")
        ops = tuple(o.lower() for o in operands)
        self._constraints.append((kind, ops))
        self._derivation.append(f"constraint {kind}{ops}")

    # ── validation ──────────────────────────────────────────────────────────
    def validate(self) -> None:
        """Fail fast on structurally contradictory constraint pairs."""
        assigns: dict[str, str] = {}
        for kind, ops in self._constraints:
            if kind == "ASSIGN":
                ent, val = ops
                if assigns.get(ent, val) != val:
                    raise ContradictionError(
                        f"{ent} assigned to both {assigns[ent]} and {val}")
                assigns[ent] = val
            if kind == "EXCLUDE" and ops in {("ASSIGN", o) for o in ()}:
                pass
        for kind, ops in self._constraints:
            if kind == "EXCLUDE" and assigns.get(ops[0]) == ops[1]:
                raise ContradictionError(
                    f"{ops[0]} both assigned to and excluded from {ops[1]}")

    def _satisfied(self, assign: dict[str, str]) -> bool:
        order = {v: i for i, v in enumerate(self._domain)}
        for kind, ops in self._constraints:
            if kind == "ASSIGN" and assign.get(ops[0]) != ops[1]:
                return False
            if kind == "EXCLUDE" and assign.get(ops[0]) == ops[1]:
                return False
            if kind == "EQUAL" and assign.get(ops[0]) != assign.get(ops[1]):
                return False
            if kind == "NOT_EQUAL" and assign.get(ops[0]) == assign.get(ops[1]):
                return False
            if kind == "BEFORE" and not (
                    order.get(assign.get(ops[0], ""), 99)
                    < order.get(assign.get(ops[1], ""), -1)):
                return False
            if kind == "AFTER" and not (
                    order.get(assign.get(ops[0], ""), -1)
                    > order.get(assign.get(ops[1], ""), 99)):
                return False
            if kind == "IMPLIES":
                # IMPLIES(e1, v1, e2, v2): if e1=v1 then e2=v2
                e1, v1, e2, v2 = ops
                if assign.get(e1) == v1 and assign.get(e2) != v2:
                    return False
            if kind == "REQUIRES":
                e1, v1 = ops
                if assign.get(e1) != v1:
                    return False
        return True

    # ── resolution ──────────────────────────────────────────────────────────
    def solve_unique(self) -> dict[str, str] | None:
        """Return THE unique bijective assignment, or None (abstain).

        None covers: contradictory graph, no solution, several solutions,
        or mismatched entity/domain sizes for the ALL_DIFFERENT bijection.
        """
        try:
            self.validate()
        except ContradictionError:
            self._derivation.append("contradiction detected -> abstain")
            return None
        if not self._entities or len(self._entities) != len(self._domain):
            return None
        solutions = []
        for perm in permutations(self._domain):
            assign = dict(zip(self._entities, perm))
            if self._satisfied(assign):
                solutions.append(assign)
                if len(solutions) > 1:
                    self._derivation.append("multiple solutions -> abstain")
                    return None
        if len(solutions) != 1:
            self._derivation.append("no solution -> abstain")
            return None
        self._derivation.append(f"unique solution {solutions[0]}")
        return solutions[0]

    @property
    def derivation(self) -> list[str]:
        return list(self._derivation)
