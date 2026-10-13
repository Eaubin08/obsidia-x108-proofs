"""M33 RED — R7..R12 (spec §36), integration merge (§21), identity vectors (§19)."""
from __future__ import annotations

import itertools
import time

import pytest

from tests.m33 import _harness as H


def _req(m, **kw):
    return H.request(m, [H.material(m)], **kw)


# R7 — contradiction preserved (declarative model, §17).
def test_r7_contradiction_preserves_both_items(m):
    a, b = H.item(m, "sky is blue"), H.item(m, "sky is green")
    c = H.contribution(m, items=[a, b], relations=[H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id),
                                                               kind="arm.contradicts")])
    res = m.reconstruct(request=_req(m), contributions=(c,))
    assert {i.item_id for i in res.items} == {a.item_id, b.item_id}
    kinds = [i.issue_kind.name for i in res.issues]
    assert kinds.count("CONTRADICTORY_SUPPORT") == 1
    iss = next(i for i in res.issues if i.issue_kind.name == "CONTRADICTORY_SUPPORT")
    assert set(iss.subject_ids) == {a.item_id, b.item_id}
    assert res.status.name == "RECONSTRUCTED"  # X5: structural completion only (§24 rule 4)


# R8 — unknown/unresolved preserved.
def test_r8_unresolved_reference_yields_partial(m):
    it = H.item(m)
    c = H.contribution(m, items=[it], issues=[H.issue(m, "UNRESOLVED_REFERENCE", [it.item_id])])
    res = m.reconstruct(request=_req(m), contributions=(c,))
    assert res.status.name == "PARTIAL"
    assert [i.issue_kind.name for i in res.issues] == ["UNRESOLVED_REFERENCE"]


def test_r8_status_and_issue_enums_distinct(m):
    assert {s.name for s in m.ReconstructionStatus} == set(H.STATUS_VALUES)
    assert {k.name for k in m.ReconstructionIssueKind} == set(H.ISSUE_KINDS)
    for bad in ("FALSE", "TRUE", "VERIFIED", "UNKNOWN"):
        assert not hasattr(m.ReconstructionStatus, bad)


# Integration merge (§21) — all ordered pairs, both contribution orders.
@pytest.mark.parametrize("s1,s2", list(itertools.product(H.INTEGRATION_VALUES, repeat=2)))
def test_integration_merge_pairs_commutative(m, s1, s2):
    req = _req(m, scope_ref="scope:test")
    results = []
    for order in ((s1, s2), (s2, s1)):
        cs = (H.contribution(m, "c1", items=[H.item(m, "X", status=order[0])]),
              H.contribution(m, "c2", items=[H.item(m, "X", status=order[1])]))
        results.append(m.reconstruct(request=req, contributions=cs))
    expected, ambiguous = H.expected_merged_status([s1, s2])
    for res in results:
        assert len(res.items) == 1
        assert res.items[0].integration_status.name == expected
        assert ("AMBIGUOUS_RECONSTRUCTION" in [i.issue_kind.name for i in res.issues]) == ambiguous
    assert results[0].reconstruction_id == results[1].reconstruction_id


# R9 — immutable deterministic result; caller mutation safety.
def test_r9_same_inputs_same_reconstruction_id(m):
    a, b = H.item(m, "A"), H.item(m, "B")
    c1, c2 = H.contribution(m, "c1", items=[a]), H.contribution(m, "c2", items=[b])
    r1 = m.reconstruct(request=_req(m), contributions=(c1, c2))
    r2 = m.reconstruct(request=_req(m), contributions=(c2, c1))
    assert r1.reconstruction_id == r2.reconstruction_id
    with pytest.raises(Exception):
        r1.status = r1.status


def test_r9_nested_caller_mutation_does_not_change_identity(m):
    payload = {"k": ["a", {"n": [1, 2]}]}
    d = H.m32().TypedCognitiveDatum("v1", "arm.text", payload)
    mat = m.ReconstructionMaterial(material_id="mat-1", datum=d, source_refs=("src:a",))
    req = H.request(m, [mat])
    it = m.ReconstructionItem(item_kind="arm.concept", content=d, supports=(H.evidence(m),),
                              integration_status=H.enum(m, "IntegrationStatus", "EVOKED_NOT_LOCKED"))
    before = (req.request_id, it.item_id)
    payload["k"][1]["n"].append(3)
    payload["k"].append("mutated")
    assert (req.request_id, it.item_id) == before
    expected_payload = {"k": ["a", {"n": [1, 2]}]}
    assert it.item_id == H.ref_item_id("arm.concept", H.m32().TypedCognitiveDatum("v1", "arm.text", expected_payload))


# R10 — canonical identity vectors (independent preimages, incl. RFC 8785 floats).
@pytest.mark.parametrize("value", ["plain", {"b": 1, "a": [2, 1]}, 1e-7, 0.000001, 1e21, 123456789012345680000.0,
                                   1.5, -0.0, "é"])
def test_r10_item_id_matches_reference(m, value):
    d = H.datum(value)
    it = m.ReconstructionItem(item_kind="arm.concept", content=d, supports=(H.evidence(m),),
                              integration_status=H.enum(m, "IntegrationStatus", "UNDETERMINED"))
    assert it.item_id == H.ref_item_id("arm.concept", d)


def test_r10_request_id_matches_reference(m):
    mats = [H.material(m, "mat-2", 1e-7, ("src:b", "src:a", "src:a")), H.material(m, "mat-1", "x", ())]
    req = H.request(m, mats, scope_ref="scope:test")
    b = {"max_derivation_depth": 4, "max_items": 50, "max_relations": 50, "max_supports_per_unit": 8}
    exp = H.ref_request_id("arm.reconstruction", [("mat-2", H.datum(1e-7), ("src:b", "src:a")),
                                                  ("mat-1", H.datum("x"), ())], b, "scope:test")
    assert req.request_id == exp
    no_scope = H.request(m, mats, scope_ref=None)
    assert no_scope.request_id == H.ref_request_id("arm.reconstruction", [("mat-2", H.datum(1e-7), ("src:a", "src:b")),
                                                                          ("mat-1", H.datum("x"), ())], b, None)


def test_r10_result_id_matches_reference(m):
    a, b = H.item(m, "A"), H.item(m, "B", status="ALREADY_INTEGRATED")
    rel = H.relation(m, ("ITEM", a.item_id), ("MATERIAL", "mat-1"))
    req = _req(m)
    c = H.contribution(m, items=[a, b], relations=[rel], issues=[H.issue(m, "INSUFFICIENT_MATERIAL", [], "arm.gap")])
    res = m.reconstruct(request=req, contributions=(c,))
    ev = [H.support_obj("EVIDENCE", [("MATERIAL", "mat-1")])]
    exp = H.ref_result_id(req.request_id, "PARTIAL",
                          [(a.item_id, "EVOKED_NOT_LOCKED", ev), (b.item_id, "ALREADY_INTEGRATED", ev)],
                          [(rel.relation_id, ev)], [H.issue_obj("INSUFFICIENT_MATERIAL", [], "arm.gap")])
    assert res.status.name == "PARTIAL"
    assert res.reconstruction_id == exp


# R11 — non-semantic metadata excluded; semantic change included (positive control in-test).
def test_r11_provider_model_clock_excluded(m, monkeypatch):
    it = H.item(m)
    w1 = H.contributor(m, provider_id="prov.a", model_id="model.a", implementation_id="impl.a")
    w2 = H.contributor(m, provider_id="prov.b", model_id="model.b", implementation_id="impl.b")
    r1 = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[it], who=w1),))
    monkeypatch.setattr(time, "time", lambda: 4_102_444_800.0)
    r2 = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[it], who=w2,
                                                                      diagnostics=("host:/tmp/x", "pid:42")),))
    assert r1.reconstruction_id == r2.reconstruction_id
    r3 = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m, "other")], who=w1),))
    assert r3.reconstruction_id != r1.reconstruction_id


def test_r11_issue_change_changes_result_id(m):
    it = H.item(m)
    r1 = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[it]),))
    r2 = m.reconstruct(request=_req(m), contributions=(H.contribution(
        m, items=[it], issues=[H.issue(m, "UNRESOLVED_REFERENCE", [it.item_id])]),))
    assert r1.reconstruction_id != r2.reconstruction_id  # X8


def test_r11_bounds_change_request_id(m):
    a = H.request(m, [H.material(m)], b=H.bounds(m, max_items=10))
    b = H.request(m, [H.material(m)], b=H.bounds(m, max_items=11))
    assert a.request_id != b.request_id  # X11


# R12 — provenance normalization and derivation trace.
def test_r12_provenance_normalized(m):
    base = H.item(m, "base")
    inf = H.item(m, "derived", supports=[H.support(m, "INFERENCE", [("ITEM", base.item_id)])])
    mats = [H.material(m, "mat-2", "y", ("src:z", "src:a")), H.material(m, "mat-1", "x", ("src:a",))]
    w1, w2 = H.contributor(m, implementation_id="impl.b"), H.contributor(m, implementation_id="impl.a")
    res = m.reconstruct(request=H.request(m, mats), contributions=(
        H.contribution(m, "c2", items=[inf], who=w1), H.contribution(m, "c1", items=[base], who=w2)))
    p = res.provenance
    assert tuple(p.source_refs) == ("src:a", "src:z")
    assert tuple(p.contribution_ids) == ("c1", "c2")
    assert tuple(p.derived_from_material_ids) == ("mat-1",)
    assert tuple(p.derived_from_item_ids) == (base.item_id,)
    assert len(p.contributors) == 2  # X10: both contributors retained
    assert p.request_id == res.request_id
