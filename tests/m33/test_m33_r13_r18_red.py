"""M33 RED — R13..R18 (spec §36), bounds (§10, §22), cycles, contributions, layer boundaries."""
from __future__ import annotations

import inspect

import pytest

from tests.m33 import _harness as H


def _req(m, **kw):
    return H.request(m, [H.material(m)], **kw)


# R13 — bounded execution / bounds.
@pytest.mark.parametrize("field", ["max_items", "max_relations", "max_supports_per_unit", "max_derivation_depth"])
@pytest.mark.parametrize("bad", [0, -1, 2 ** 53, "3", 1.0])
def test_r13_bounds_invalid_values(m, field, bad):
    H.raises_code(m, "INVALID_RECONSTRUCTION_REQUEST", H.bounds, m, **{field: bad})


@pytest.mark.parametrize("field", ["max_items", "max_relations", "max_supports_per_unit", "max_derivation_depth"])
def test_r13_bounds_valid_extremes(m, field):
    H.bounds(m, **{field: 1})
    H.bounds(m, **{field: 2 ** 53 - 1})


def test_r13_max_items_exceeded(m):
    req = _req(m, b=H.bounds(m, max_items=1))
    m.reconstruct(request=req, contributions=(H.contribution(m, items=[H.item(m, "A")]),))
    H.raises_code(m, "RECONSTRUCTION_BOUND_EXCEEDED", m.reconstruct, request=req,
                  contributions=(H.contribution(m, items=[H.item(m, "A"), H.item(m, "B")]),))


def test_r13_max_relations_and_supports_exceeded(m):
    a, b = H.item(m, "A"), H.item(m, "B")
    req = _req(m, b=H.bounds(m, max_relations=1, max_supports_per_unit=1))
    rels = [H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id)),
            H.relation(m, ("ITEM", b.item_id), ("ITEM", a.item_id))]
    H.raises_code(m, "RECONSTRUCTION_BOUND_EXCEEDED", m.reconstruct, request=req,
                  contributions=(H.contribution(m, items=[a, b], relations=rels),))
    two = H.item(m, "A", supports=[H.evidence(m), H.support(m, "EVIDENCE", [("SOURCE", "src:a")])])
    H.raises_code(m, "RECONSTRUCTION_BOUND_EXCEEDED", m.reconstruct, request=req,
                  contributions=(H.contribution(m, items=[two]),))


def _chain(m, n):
    items = [H.item(m, "n0")]
    for i in range(1, n + 1):
        items.append(H.item(m, f"n{i}", supports=[H.support(m, "INFERENCE", [("ITEM", items[-1].item_id)])]))
    return items


def test_r13_derivation_depth(m):
    req = _req(m, b=H.bounds(m, max_derivation_depth=2))
    m.reconstruct(request=req, contributions=(H.contribution(m, items=_chain(m, 2)),))
    H.raises_code(m, "RECONSTRUCTION_BOUND_EXCEEDED", m.reconstruct, request=req,
                  contributions=(H.contribution(m, items=_chain(m, 3)),))


def test_derivation_cycle_rejected(m):
    a_id, b_id = H.item(m, "A").item_id, H.item(m, "B").item_id
    a = H.item(m, "A", supports=[H.support(m, "INFERENCE", [("ITEM", b_id)])])
    b = H.item(m, "B", supports=[H.support(m, "INFERENCE", [("ITEM", a_id)])])
    H.raises_code(m, "DERIVATION_CYCLE", m.reconstruct, request=_req(m), contributions=(H.contribution(m, items=[a, b]),))


def test_no_scheduler_surface(m):
    assert list(inspect.signature(m.reconstruct).parameters) == ["request", "contributions"]
    for n in [x for x in dir(H.rt()) if not x.startswith("_")]:
        low = n.lower()
        for bad in ("schedul", "spawn", "select_", "router", "retry", "fast_path", "registry", "utility"):
            assert bad not in low, n


# R14 — only explicit contributions participate.
def test_r14_only_supplied_items_appear(m):
    a = H.item(m, "A")
    res = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[a]),))
    assert [i.item_id for i in res.items] == [a.item_id]
    empty = m.reconstruct(request=_req(m), contributions=())
    assert len(empty.items) == 0
    assert empty.status.name == "INSUFFICIENT_MATERIAL"


def test_r14_duplicate_contribution_ids_rejected(m):
    H.raises_code(m, "INVALID_CONTRIBUTION", m.reconstruct, request=_req(m),
                  contributions=(H.contribution(m, "dup"), H.contribution(m, "dup")))


# R15–R18 — static boundaries on the runtime package (require it to exist).
def test_r15_r17_no_forbidden_imports():
    H.require_runtime_dir()
    assert H.forbidden_imports(H.M33_RUNTIME_DIR) == set()


def test_r16_r18_r24_no_competing_public_names():
    H.require_runtime_dir()
    defined = H.defined_names(H.M33_RUNTIME_DIR)
    for layer, path in H.SEALED_LAYERS.items():
        clash = defined & H.M32H.public_names(path)
        assert clash == set(), f"{layer}: {sorted(clash)}"
    assert H.candidate_names(defined) == set()
    for n in ("CognitivePath", "FailedPath", "PathHistory", "CognitiveRoleSpec", "ContextPacket",
              "PrimitiveResult", "PrimitiveTypeSpec", "TypedCognitiveDatum"):
        assert n not in defined


def test_r16_role_ref_is_provenance_only(m):
    w = H.contributor(m, role_ref="b7.role.UNDERSTANDER")
    res = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m)], who=w),))
    plain = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m)]),))
    assert res.reconstruction_id == plain.reconstruction_id
    assert any(getattr(c, "role_ref", None) == "b7.role.UNDERSTANDER" for c in res.provenance.contributors)


def test_r18_relation_is_not_cognitive_path(m):
    a, b = H.item(m, "A"), H.item(m, "B")
    rel = H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id))
    assert type(rel).__name__ == "ReconstructionRelation"
    for f in ("steps", "path_id", "history"):
        assert not hasattr(rel, f)
