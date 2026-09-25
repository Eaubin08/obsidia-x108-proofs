"""Structured-semantics checks for the frozen French grammar matrix.

Skipped until the non-sovereign semantic lattice exists, so that the matrix
can be frozen before any implementation is written.
"""
from __future__ import annotations

import pytest

from tests.semantic_grammar_matrix import PROBES

lattice = pytest.importorskip("app.semantic.lattice")


def _unit_attr(unit, key):
    if key == "object":
        return unit.object_head
    if key == "object_reference":
        return unit.object.reference if unit.object is not None else None
    return getattr(unit, key)


def _match_units(frame, specs):
    remaining = list(frame.units)
    for spec in specs:
        found = None
        for unit in remaining:
            if all(_unit_attr(unit, k) == v for k, v in spec.items()):
                found = unit
                break
        assert found is not None, (
            f"no unit matches {spec}\n"
            f"units: {[u.describe() for u in frame.units]}"
        )
        remaining.remove(found)


def _has_relation(frame, kind, src_pred, tgt_pred):
    by_id = {u.id: u for u in frame.units}
    for rel in frame.relations:
        if rel.kind != kind:
            continue
        src, tgt = by_id.get(rel.source), by_id.get(rel.target)
        if src and tgt and src.predicate == src_pred and tgt.predicate == tgt_pred:
            return True
    return False


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_matrix_probe_semantics(probe):
    frame = lattice.parse_utterance(probe["text"])

    # Raw input is always preserved verbatim.
    assert frame.raw == probe["text"]

    if "units" in probe:
        _match_units(frame, probe["units"])
    if "n_units" in probe:
        assert len(frame.units) == probe["n_units"], [u.describe() for u in frame.units]
    for kind, src, tgt in probe.get("relations", []):
        assert _has_relation(frame, kind, src, tgt), (
            f"missing {kind}({src}->{tgt}); relations: "
            f"{[r.describe() for r in frame.relations]}"
        )
    for c in probe.get("constraints", []):
        assert c in frame.constraints, frame.constraints
    for c in probe.get("absent_constraints", []):
        assert c not in frame.constraints, frame.constraints
    if "closure" in probe:
        assert frame.closure is probe["closure"], frame.closure_blockers
    if "contradiction" in probe:
        assert bool(frame.contradictions) is probe["contradiction"], frame.contradictions
    if "unresolved" in probe:
        assert len(frame.unresolved_references) == probe["unresolved"], frame.unresolved_references
    if "evidence_need" in probe:
        assert bool(frame.evidence_needs) is probe["evidence_need"]
    if "surface_act" in probe:
        assert frame.surface_act == probe["surface_act"]
    for d in probe.get("deixis", []):
        assert d in frame.deixis


def test_matrix_is_broad_enough():
    assert len(PROBES) >= 40
    assert len({p["id"] for p in PROBES}) == len(PROBES)
