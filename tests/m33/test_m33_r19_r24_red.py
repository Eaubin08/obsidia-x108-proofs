"""M33 RED — R19..R24 (spec §36): effects, validation/errors, status table incl. B1, authority."""
from __future__ import annotations

import inspect

import pytest

from tests.m33 import _harness as H


def _req(m, **kw):
    return H.request(m, [H.material(m)], **kw)


def _failed(m, cid="cf"):
    return H.contribution(m, cid, status="FAILED_RUNTIME", diagnostics=("RuntimeError",))


# R19 / R23 — effects contract.
def test_r19_r23_effects_all_false(m):
    eff = m.RECONSTRUCTION_EFFECTS
    for f in H.EFFECT_FIELDS:
        assert getattr(eff, f) is False, f


@pytest.mark.parametrize("field", H.EFFECT_FIELDS)
def test_r23_effects_true_rejected(m, field):
    H.raises_code(m, "INVALID_EFFECTS_CONTRACT", m.ReconstructionEffectsContract, **{field: True})


def test_r23_result_carries_false_effects(m):
    res = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m)]),))
    for f in H.EFFECT_FIELDS:
        assert getattr(res.effects, f) is False


def test_r23_reconstruct_takes_no_handles(m):
    assert list(inspect.signature(m.reconstruct).parameters) == ["request", "contributions"]


# R20 — no world-model / calibration / selection fields.
def test_r20_no_confidence_or_utility_fields(m):
    it, res = H.item(m), m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m)]),))
    for obj in (it, res, res.provenance):
        for f in ("confidence", "utility", "score", "competence", "calibration", "world_model", "threshold"):
            assert not hasattr(obj, f), f


# R21 — every error code at its origin.
def test_r21_construction_error_origins(m):
    H.raises_code(m, "INVALID_RECONSTRUCTION_REQUEST", m.ReconstructionRequest, schema_version="m33.request.v0",
                  reconstruction_kind="arm.reconstruction", materials=(), bounds=H.bounds(m))
    H.raises_code(m, "INVALID_RECONSTRUCTION_ITEM", m.ReconstructionItem, item_kind="Bad", content=H.datum("v"),
                  supports=(H.evidence(m),), integration_status=H.enum(m, "IntegrationStatus", "UNDETERMINED"))
    H.raises_code(m, "INVALID_RECONSTRUCTION_ITEM", m.ReconstructionItem, item_kind="arm.concept",
                  content=H.datum("v"), supports=(),
                  integration_status=H.enum(m, "IntegrationStatus", "UNDETERMINED"))
    H.raises_code(m, "INVALID_RECONSTRUCTION_ISSUE", m.ReconstructionIssue, issue_kind="NOT_A_KIND", subject_ids=())
    H.raises_code(m, "INVALID_CONTRIBUTION", m.ReconstructionContribution, contribution_id="",
                  contributor=H.contributor(m), status=H.enum(m, "ContributionStatus", "COMPLETED"),
                  items=(), relations=(), issues=(), diagnostics=())
    H.raises_code(m, "INVALID_CONTRIBUTION", m.ReconstructionContributor)


def test_r21_lifecycle_error_origins(m):
    H.raises_code(m, "INVALID_SUPPORT_REFERENCE", m.reconstruct, request=_req(m),
                  contributions=(H.contribution(m, items=[H.item(m, supports=[H.evidence(m, "mat-unknown")])]),))
    H.raises_code(m, "INVALID_SUPPORT_REFERENCE", m.reconstruct, request=_req(m),  # X6
                  contributions=(H.contribution(m, items=[H.item(m, supports=[
                      H.support(m, "EVIDENCE", [("SOURCE", "src:unknown")])])]),))
    H.raises_code(m, "INVALID_SUPPORT_REFERENCE", m.reconstruct, request=_req(m),
                  contributions=(H.contribution(m, items=[H.item(m, supports=[
                      H.support(m, "INFERENCE", [("ITEM", "e" * 64)])])]),))
    H.raises_code(m, "INVALID_RECONSTRUCTION_REQUEST", m.reconstruct, request="not a request", contributions=())
    H.raises_code(m, "INVALID_CONTRIBUTION", m.reconstruct, request=_req(m), contributions=("not a contribution",))


def test_r21_invalid_result_on_direct_construction(m):
    res = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[H.item(m)]),))
    kw = {f: getattr(res, f) for f in ("schema_version", "request_id", "status", "items", "relations", "issues",
                                        "provenance", "effects")}
    kw["status"] = H.enum(m, "ReconstructionStatus", "FAILED_RUNTIME")  # §24 rule 1: FAILED_RUNTIME ⇒ empty items
    with pytest.raises(m.ReconstructionValidationError) as ei:
        m.ReconstructionResult(**kw)
    assert ei.value.code == "INVALID_RECONSTRUCTION_RESULT"


def test_r21_error_codes_are_not_statuses(m):
    statuses = {s.name for s in m.ReconstructionStatus}
    assert statuses.isdisjoint(H.ERROR_CODES)


# R22 — status decision table and B1 precedence.
def test_r22_status_table(m):
    it = H.item(m)
    ok = m.reconstruct(request=_req(m), contributions=(H.contribution(m, items=[it]),))
    assert ok.status.name == "RECONSTRUCTED"
    amb = m.reconstruct(request=_req(m), contributions=(H.contribution(
        m, items=[it], issues=[H.issue(m, "AMBIGUOUS_RECONSTRUCTION", [it.item_id])]),))
    assert amb.status.name == "PARTIAL"
    empty = m.reconstruct(request=H.request(m, []), contributions=())
    assert empty.status.name == "INSUFFICIENT_MATERIAL"
    all_failed = m.reconstruct(request=_req(m), contributions=(_failed(m, "f1"), _failed(m, "f2")))
    assert all_failed.status.name == "FAILED_RUNTIME" and len(all_failed.items) == 0


def test_r22_b1_4_mixed_failure_discards_items(m):  # X3
    res = m.reconstruct(request=_req(m), contributions=(_failed(m), H.contribution(m, "ok", items=[H.item(m)])))
    assert res.status.name == "FAILED_RUNTIME"
    assert len(res.items) == 0 and len(res.relations) == 0 and len(res.issues) == 0


def test_r22_b1_1_validation_beats_failed_runtime_dangling(m):  # M_B1_1
    bad = H.contribution(m, "bad", items=[H.item(m, supports=[H.support(m, "INFERENCE", [("ITEM", "d" * 64)])])])
    for order in ((_failed(m), bad), (bad, _failed(m))):
        H.raises_code(m, "INVALID_SUPPORT_REFERENCE", m.reconstruct, request=_req(m), contributions=order)


def test_r22_b1_2_validation_beats_failed_runtime_cycle(m):  # M_B1_3
    a_id, b_id = H.item(m, "A").item_id, H.item(m, "B").item_id
    cyc = H.contribution(m, "cyc", items=[H.item(m, "A", supports=[H.support(m, "INFERENCE", [("ITEM", b_id)])]),
                                          H.item(m, "B", supports=[H.support(m, "INFERENCE", [("ITEM", a_id)])])])
    H.raises_code(m, "DERIVATION_CYCLE", m.reconstruct, request=_req(m), contributions=(_failed(m), cyc))


def test_r22_b1_3_validation_beats_failed_runtime_bound(m):
    req = _req(m, b=H.bounds(m, max_items=1))
    big = H.contribution(m, "big", items=[H.item(m, "A"), H.item(m, "B")])
    H.raises_code(m, "RECONSTRUCTION_BOUND_EXCEEDED", m.reconstruct, request=req, contributions=(_failed(m), big))


def test_r22_b1_5_failed_contribution_payload_rejected(m):  # X12, M_B1_2
    H.raises_code(m, "INVALID_CONTRIBUTION", H.contribution, m, "cf", items=[H.item(m)], status="FAILED_RUNTIME")
    a, b = H.item(m, "A"), H.item(m, "B")
    H.raises_code(m, "INVALID_CONTRIBUTION", H.contribution, m, "cf", status="FAILED_RUNTIME",
                  relations=[H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id))])


def test_r22_insufficient_material_never_raises(m):
    res = m.reconstruct(request=H.request(m, []), contributions=(H.contribution(m),))
    assert res.status.name == "INSUFFICIENT_MATERIAL"


# R24 — public surface present and isolated (static part in r13_r18 file).
def test_r24_certified_public_surface_present(m):
    for n in H.PUBLIC_SURFACE:
        assert hasattr(H.rt(), n), n
