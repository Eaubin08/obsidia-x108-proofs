"""M33 RED — R1..R6 (spec §36)."""
from __future__ import annotations

import re
import unicodedata

import pytest

from tests.m33 import _harness as H


# R1 — source attribution / N1 (DOC_AUDIT; passes on the certified spec text).
def test_r1_spec_distinguishes_source_levels_a_b_c():
    text = H.SPEC_FILE.read_text(encoding="utf-8")
    sec3 = text[text.index("## 3. Source attribution"):text.index("## 4.")]
    for level in ("A — direct historical source", "B — later lineage", "C — current certified synthesis"):
        assert level in sec3
    assert "without retroactively attributing later terminology to the earliest source" in sec3
    assert "HISTORICAL_SOURCE_RETROJECTION_FORBIDDEN=YES" in sec3


def test_r1_level_a_row_carries_no_trajectory_vocabulary():
    text = H.SPEC_FILE.read_text(encoding="utf-8")
    row_a = next(l for l in text.splitlines() if l.startswith("| A — direct historical source"))
    for word in ("trajector", "path", "chemin", "décomposition", "decomposition", "recomposition"):
        assert word not in row_a.lower()


# R2 — M32-typed bounded input; no context fetch / memory lookup.
def test_r2_material_requires_m32_datum(m):
    mat = H.material(m)
    assert mat.datum.datum_type == "arm.text"
    H.raises_code(m, "INVALID_MATERIAL", m.ReconstructionMaterial, material_id="mat-x",
                  datum={"datum_type": "arm.text", "value": "raw"}, source_refs=())
    H.raises_code(m, "INVALID_MATERIAL", m.ReconstructionMaterial, material_id="", datum=H.datum("v"), source_refs=())


def test_r2_duplicate_material_ids_rejected(m):
    H.raises_code(m, "INVALID_RECONSTRUCTION_REQUEST", H.request, m, [H.material(m, "mat-1"), H.material(m, "mat-1", "other")])


def test_r2_no_context_or_memory_lookup_surface(m):
    params = set(__import__("inspect").signature(m.reconstruct).parameters)
    assert params == {"request", "contributions"}
    for n in [x for x in dir(H.rt()) if not x.startswith("_")]:
        assert not re.search(r"(?i)(fetch|retriev|lookup|memory|context_packet|graphiti)", n), n


# R3 — ReconstructionItem / N2.
def test_r3_reconstruction_item_exists_with_hex_id(m):
    it = H.item(m)
    assert H.M32H.HEX64.match(it.item_id)


def test_r3_no_candidate_names_in_public_surface(m):
    public = [n for n in dir(H.rt()) if not n.startswith("_")]
    assert H.candidate_names(public) == set()
    for n in H.PUBLIC_SURFACE:
        assert hasattr(H.rt(), n), f"missing certified public name {n}"


def test_r3_item_has_no_truth_or_promotion_fields(m):
    it = H.item(m)
    for f in ("verified", "promoted", "truth", "authority", "confidence", "claim_state"):
        assert not hasattr(it, f)


# R4 — evidence vs inference.
def test_r4_support_kind_enum_exact(m):
    assert {k.name for k in m.ReconstructionSupportKind} == set(H.SUPPORT_KINDS)
    assert not hasattr(m.ReconstructionSupportKind, "VERIFIED")


def test_r4_evidence_shape_and_inference_basis(m):
    H.support(m, "EVIDENCE", [("MATERIAL", "mat-1")])
    H.support(m, "EVIDENCE", [("SOURCE", "src:a")])
    H.support(m, "INFERENCE", [("ITEM", "a" * 64)])
    H.raises_code(m, "INVALID_DERIVATION", H.support, m, "EVIDENCE", [("ITEM", "a" * 64)])
    H.raises_code(m, "INVALID_DERIVATION", m.ReconstructionSupport,
                  kind=H.enum(m, "ReconstructionSupportKind", "INFERENCE"), refs=())


def test_r4_kinds_preserved_on_aggregation(m):
    target = H.item(m, "shared")
    req = H.request(m, [H.material(m)])
    a = H.contribution(m, "ca", items=[H.item(m, "shared", supports=[H.evidence(m)])])
    b = H.contribution(m, "cb", items=[H.item(m, "base"), H.item(m, "shared", supports=[
        H.support(m, "INFERENCE", [("ITEM", H.item(m, "base").item_id)])])])
    res = m.reconstruct(request=req, contributions=(a, b))
    got = next(i for i in res.items if i.item_id == target.item_id)
    kinds = sorted(s.kind.name for s in got.supports)
    assert kinds == ["EVIDENCE", "INFERENCE"]


# R5 — scope-bounded integration status (incl. B2).
def test_r5_integration_status_enum_exact(m):
    assert {s.name for s in m.IntegrationStatus} == set(H.INTEGRATION_VALUES)
    assert not hasattr(m.IntegrationStatus, "UNKNOWN") and not hasattr(m.IntegrationStatus, "FALSE")


def test_r5_absent_in_scope_requires_scope_ref(m):
    ok = m.reconstruct(request=H.request(m, [H.material(m)], scope_ref="scope:test"),
                       contributions=(H.contribution(m, items=[H.item(m, status="ABSENT_IN_SCOPE")]),))
    assert ok.items[0].integration_status.name == "ABSENT_IN_SCOPE"
    H.raises_code(m, "INVALID_INTEGRATION_STATUS", m.reconstruct,
                  request=H.request(m, [H.material(m)], scope_ref=None),
                  contributions=(H.contribution(m, items=[H.item(m, status="ABSENT_IN_SCOPE")]),))


def test_r5_b2_invalid_absent_not_sanitized_by_merge(m):
    req = H.request(m, [H.material(m)], scope_ref=None)
    a = H.contribution(m, "ca", items=[H.item(m, "X", status="ABSENT_IN_SCOPE")])
    b = H.contribution(m, "cb", items=[H.item(m, "X", status="EVOKED_NOT_LOCKED")])
    for order in ((a, b), (b, a)):
        H.raises_code(m, "INVALID_INTEGRATION_STATUS", m.reconstruct, request=req, contributions=order)


def test_r5_inspection_scope_is_material_set(m):
    one = H.request(m, [H.material(m, "mat-1")], scope_ref="scope:same")
    two = H.request(m, [H.material(m, "mat-1"), H.material(m, "mat-2", "more")], scope_ref="scope:same")
    assert one.request_id != two.request_id


# R6 — relations without mandatory graph.
def test_r6_relation_identity_and_endpoints(m):
    a, b = H.item(m, "A"), H.item(m, "B")
    rel = H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id))
    assert rel.relation_id == H.ref_relation_id("arm.related_to", ("ITEM", a.item_id), ("ITEM", b.item_id))
    H.raises_code(m, "INVALID_RECONSTRUCTION_RELATION", H.relation, m, ("ITEM", a.item_id), ("ITEM", a.item_id))
    H.raises_code(m, "INVALID_RECONSTRUCTION_RELATION", H.relation, m, ("ITEM", a.item_id), ("ITEM", b.item_id),
                  kind="NotNamespaced")


def test_r6_relation_cycle_allowed_unknown_endpoint_rejected(m):
    a, b = H.item(m, "A"), H.item(m, "B")
    req = H.request(m, [H.material(m)])
    cyc = H.contribution(m, items=[a, b], relations=[H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id)),
                                                     H.relation(m, ("ITEM", b.item_id), ("ITEM", a.item_id))])
    res = m.reconstruct(request=req, contributions=(cyc,))
    assert len(res.relations) == 2 and res.status.name == "RECONSTRUCTED"
    dangling = H.contribution(m, items=[a], relations=[H.relation(m, ("ITEM", a.item_id), ("ITEM", "f" * 64))])
    H.raises_code(m, "INVALID_RELATION_REFERENCE", m.reconstruct, request=req, contributions=(dangling,))


def test_r6_no_graph_types_and_no_transitive_closure(m):
    for n in ("ARMGraph", "ARMNode", "ARMEdge", "GraphScheduler"):
        assert not hasattr(H.rt(), n)
    a, b, c = H.item(m, "A"), H.item(m, "B"), H.item(m, "C")
    res = m.reconstruct(request=H.request(m, [H.material(m)]), contributions=(H.contribution(
        m, items=[a, b, c], relations=[H.relation(m, ("ITEM", a.item_id), ("ITEM", b.item_id)),
                                       H.relation(m, ("ITEM", b.item_id), ("ITEM", c.item_id))]),))
    assert len(res.relations) == 2


def test_nfc_equivalent_content_same_item_id(m):
    a = H.item(m, unicodedata.normalize("NFC", "é"))
    b = H.item(m, unicodedata.normalize("NFD", "é"))
    assert a.item_id == b.item_id
