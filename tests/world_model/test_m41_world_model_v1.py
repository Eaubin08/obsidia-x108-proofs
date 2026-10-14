"""M41 World Model V1 — RED contract tests.

Source of truth: docs/architecture/M41_WORLD_MODEL_SPEC_V1.md at commit 21dd4634 (independently
certified PASS_WITH_NONBLOCKING_FINDINGS). Runtime target: ``app.world_model`` (absent at RED).

Conventions:
- the runtime is imported lazily inside each test (``rt()``); a missing runtime makes each runtime test
  FAIL with "M41 runtime app/world_model is absent (certified RED)" — no collection error, no skip,
  no xfail, no fallback implementation;
- constructors are called with keyword arguments named after the spec fields; an absent optional field
  is an omitted keyword;
- identifiers are checked against an independent oracle written from spec §6/§11 and M32 §16; the
  runtime's own hashing is never used to compute an expected value;
- error codes are asserted as the ``"<CODE>: "`` prefix of a ``ValueError`` message (spec §14);
- NB9: the spec prescribes no code for an invalid ``unknowns`` element, so those tests only require a
  ``ValueError`` with an ``M41_`` code.
"""
from __future__ import annotations

import ast
import builtins
import hashlib
import io
import json
import os
import socket
import subprocess
import sys
import unicodedata
from collections.abc import Mapping
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.primitives.m32 import TypedCognitiveDatum  # sealed-substrate primitive, allowed by spec §3

STATE = "STATE_OF_PRESUMED_REFERENT"
IDENTITY = "REFERENT_IDENTITY"


# ---------------------------------------------------------------------------
# Runtime access (RED attribution)
# ---------------------------------------------------------------------------

def rt():
    try:
        import app.world_model as mod  # noqa: PLC0415
    except ModuleNotFoundError as exc:
        if exc.name in ("app.world_model",) or (exc.name or "").startswith("app.world_model"):
            pytest.fail("M41 runtime app/world_model is absent (certified RED)")
        raise
    return mod


# ---------------------------------------------------------------------------
# Builders (keyword arguments only)
# ---------------------------------------------------------------------------

def ref(kind="mmonde.world_state_v0", rid="ws-1", src=None):
    kw = {"ref_kind": kind, "ref_id": rid}
    if src is not None:
        kw["source_label"] = src
    return rt().WorldMaterialRef(**kw)


def datum(value="ball at rest", dtype="arm.text", semantic_refs=None):
    if semantic_refs is None:
        return TypedCognitiveDatum("v1", dtype, value)
    return TypedCognitiveDatum("v1", dtype, value, semantic_refs)


_UNSET = object()


def hyp(kind=STATE, referent=_UNSET, content=_UNSET, materials=_UNSET, modality="mmonde.observed",
        contradictions=_UNSET, unknowns=_UNSET, rank=_UNSET, confidence=_UNSET):
    kw = {
        "hypothesis_kind": kind,
        "presumed_referent_ref": ref("sens.entity_ref", "ball-1") if referent is _UNSET else referent,
        "material_refs": (ref(),) if materials is _UNSET else materials,
        "modality_label": modality,
    }
    if content is not _UNSET:
        kw["content"] = content
    if contradictions is not _UNSET:
        kw["contradiction_refs"] = contradictions
    if unknowns is not _UNSET:
        kw["unknowns"] = unknowns
    if rank is not _UNSET:
        kw["rank"] = rank
    if confidence is not _UNSET:
        kw["confidence"] = confidence
    return rt().WorldStateHypothesis(**kw)


def hset(members, subject=_UNSET):
    return rt().WorldHypothesisSet(
        subject_ref=ref("sens.entity_ref", "ball-1") if subject is _UNSET else subject,
        members=members,
    )


def expect_code(code, fn):
    with pytest.raises(ValueError) as info:
        fn()
    assert str(info.value).startswith(code + ": "), f"expected {code}, got: {info.value!r}"


def expect_some_m41_code(fn):
    with pytest.raises(ValueError) as info:
        fn()
    assert str(info.value).startswith("M41_"), f"expected an M41_* code, got: {info.value!r}"


# ---------------------------------------------------------------------------
# Independent identity oracle (spec §6, §11; M32 §15/§16) — never calls the runtime
# ---------------------------------------------------------------------------

def nfc(s):
    return unicodedata.normalize("NFC", s)


def canon(obj):
    """Canonical JSON for the string/int/list/dict values used by these tests.

    For such values M32 §15 (sorted keys, compact separators, NFC, UTF-8, ensure_ascii=false) coincides
    with json.dumps below; tests deliberately avoid floats inside identity preimages.
    """
    def norm(v):
        if isinstance(v, str):
            return nfc(v)
        if isinstance(v, list):
            return [norm(x) for x in v]
        if isinstance(v, dict):
            return {nfc(k): norm(x) for k, x in v.items()}
        if isinstance(v, bool) or not isinstance(v, int):
            raise AssertionError("oracle restricted to str/int/list/dict")
        return v
    return json.dumps(norm(obj), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha(obj):
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


def REF(kind, rid, src=None):
    d = {"ref_id": nfc(rid), "ref_kind": kind}
    if src is not None:
        d["source_label"] = nfc(src)
    return d


def DATUM(value, dtype="arm.text", semantic_refs=None):
    d = {"datum_type": dtype, "schema_version": "v1", "value": value}
    if semantic_refs is not None:
        d["semantic_refs"] = list(semantic_refs)
    return d


def ref_sorted(refs):
    return sorted(refs, key=canon)


def oracle_hypothesis_id(kind, referent, materials, modality, content=None, contradictions=(), unknowns=()):
    pre = {
        "schema_version": "m41.world_state_hypothesis.v1",
        "hypothesis_kind": kind,
        "presumed_referent": referent,
        "material_refs": ref_sorted(list(materials)),
        "modality_label": modality,
        "contradiction_refs": ref_sorted(list(contradictions)),
        "unknowns": sorted(nfc(u) for u in unknowns),
    }
    if content is not None:
        pre["content"] = content
    return sha(pre)


def oracle_set_id(subject, member_ids):
    return sha({"schema_version": "m41.world_hypothesis_set.v1", "subject": subject,
                "member_ids": sorted(member_ids)})


def is_hex64(s):
    return isinstance(s, str) and len(s) == 64 and all(c in "0123456789abcdef" for c in s)


# ---------------------------------------------------------------------------
# Oracle self-checks (pass at RED; they test the oracle, not the runtime)
# ---------------------------------------------------------------------------

def test_oracle_canon_is_sorted_compact_nfc():
    assert canon({"b": 1, "a": "é"}) == '{"a":"é","b":1}'


def test_oracle_hash_shape_and_sensitivity():
    a = oracle_hypothesis_id(STATE, REF("sens.entity_ref", "x"), [REF("k.a", "1")], "m.o")
    b = oracle_hypothesis_id(STATE, REF("sens.entity_ref", "x"), [REF("k.a", "1", "s")], "m.o")
    assert is_hex64(a) and is_hex64(b) and a != b


# ---------------------------------------------------------------------------
# Type A — WorldMaterialRef
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ["mmonde.world_state_v0", "sens.event_ref",
                                  "f16.real_image_observation_v0", "gps.domain_measurement", "a.b.c"])
def test_ref_valid_kinds_accepted_and_stored(kind):
    r = ref(kind, "id-1", "src")
    assert (r.ref_kind, r.ref_id, r.source_label) == (kind, "id-1", "src")


def test_ref_source_label_optional():
    r = ref("sens.event_ref", "ev-9")
    assert (r.ref_kind, r.ref_id) == ("sens.event_ref", "ev-9")


def test_ref_nfc_normalized_and_whitespace_preserved():
    r = ref("k.a", "caf" + "é", " lab" + "él ")
    assert r.ref_id == "café"
    assert r.source_label == " labél "
    assert ref("k.a", " a ").ref_id == " a "


def test_ref_equality_is_three_field_equality():
    assert ref("k.a", "1", "s") == ref("k.a", "1", "s")
    assert ref("k.a", "1") != ref("k.a", "1", "s")
    assert ref("k.a", "1", "s") != ref("k.a", "1", "t")
    assert ref("k.a", "1") != ref("k.b", "1")


@pytest.mark.parametrize("rid", ["", "   ", "\t\n", "a\x00b", b"x", 5, None])
def test_ref_invalid_ref_id(rid):
    expect_code("M41_INVALID_REF", lambda: rt().WorldMaterialRef(ref_kind="k.a", ref_id=rid))


@pytest.mark.parametrize("kind", ["nodot", "Up.x", "mmonde.", ".x", "a.b-c", "1a.b", b"a.b", None])
def test_ref_invalid_ref_kind(kind):
    expect_code("M41_INVALID_REF", lambda: rt().WorldMaterialRef(ref_kind=kind, ref_id="x"))


@pytest.mark.parametrize("src", ["", "   ", "a\x00", b"s", 3])
def test_ref_invalid_source_label(src):
    expect_code("M41_INVALID_REF",
                lambda: rt().WorldMaterialRef(ref_kind="k.a", ref_id="x", source_label=src))


REF_FORBIDDEN_NAMES = {"resolve", "dereference", "deref", "fetch", "load", "get_material", "verify",
                       "verified", "is_verified", "source_verified", "verification", "trusted",
                       "is_trusted", "exists", "is_valid_provenance"}


def test_ref_no_resolution_and_no_verification_surface():
    r = ref("k.a", "1", "src")
    names = {n for n in dir(r) if not n.startswith("_")} | {n for n in dir(type(r)) if not n.startswith("_")}
    assert not (names & REF_FORBIDDEN_NAMES), sorted(names & REF_FORBIDDEN_NAMES)


# ---------------------------------------------------------------------------
# Type B — WorldStateHypothesis
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("kind", [STATE, IDENTITY])
def test_hypothesis_kinds_accepted(kind):
    assert hyp(kind=kind).hypothesis_kind == kind


@pytest.mark.parametrize("kind", ["STATE", "state_of_presumed_referent", "", None, "REFERENT_IDENTITY "])
def test_hypothesis_invalid_kind(kind):
    expect_code("M41_INVALID_KIND", lambda: hyp(kind=kind))


@pytest.mark.parametrize("materials", [(), []])
def test_hypothesis_missing_material(materials):
    expect_code("M41_MISSING_MATERIAL", lambda: hyp(materials=materials))


@pytest.mark.parametrize("modality", ["observed", "Mmonde.observed", "", "mmonde.", None])
def test_hypothesis_invalid_modality(modality):
    expect_code("M41_INVALID_MODALITY", lambda: hyp(modality=modality))


@pytest.mark.parametrize("content", [{"value": 1}, "text", 3])
def test_hypothesis_invalid_content(content):
    expect_code("M41_INVALID_CONTENT", lambda: hyp(content=content))


def test_hypothesis_content_optional_and_typed():
    h1 = hyp()
    d = datum("ball falling", semantic_refs=["sem:1"])
    h2 = hyp(content=d)
    assert isinstance(h2.content, TypedCognitiveDatum)
    assert h2.content.value == "ball falling"
    assert h1.hypothesis_id != h2.hypothesis_id


def test_hypothesis_presumed_referent_must_be_ref():
    expect_code("M41_INVALID_REF", lambda: hyp(referent="ball-1"))


@pytest.mark.parametrize("bad", [{"a": 1}, {1, 2}])
def test_hypothesis_material_refs_non_sequence(bad):
    expect_code("M41_INVALID_COLLECTION", lambda: hyp(materials=bad))


def test_hypothesis_material_refs_plain_string_element():
    expect_code("M41_INVALID_COLLECTION", lambda: hyp(materials=(ref(), "mmonde.world_state_v0")))


def test_hypothesis_contradiction_refs_plain_string_element():
    expect_code("M41_INVALID_COLLECTION", lambda: hyp(contradictions=("c-1",)))


def test_hypothesis_unknowns_mutable_element_rejected():
    expect_code("M41_INVALID_COLLECTION", lambda: hyp(unknowns=("u1", ["nested"])))


@pytest.mark.parametrize("bad", ["", "   ", "\t"])
def test_hypothesis_unknowns_invalid_entry_rejected_nb9(bad):
    # NB9: rejection is normative (OPAQUE_STRING), the exact code is not prescribed by the spec.
    expect_some_m41_code(lambda: hyp(unknowns=("u1", bad)))


def test_hypothesis_duplicate_material_rejected():
    expect_code("M41_DUPLICATE_ENTRY", lambda: hyp(materials=(ref("k.a", "1"), ref("k.a", "1"))))


def test_hypothesis_duplicate_contradiction_rejected():
    expect_code("M41_DUPLICATE_ENTRY",
                lambda: hyp(contradictions=(ref("k.c", "1"), ref("k.c", "1"))))


def test_hypothesis_duplicate_unknown_rejected():
    expect_code("M41_DUPLICATE_ENTRY", lambda: hyp(unknowns=("u1", "u1")))


@pytest.mark.parametrize("kw", [{"rank": True}, {"rank": -1}, {"rank": 1.5}, {"rank": "1"},
                                {"confidence": 1.5}, {"confidence": -0.1}, {"confidence": float("nan")},
                                {"confidence": float("inf")}, {"confidence": True}, {"confidence": "0.5"}])
def test_hypothesis_invalid_scalars(kw):
    expect_code("M41_INVALID_SCALAR", lambda: hyp(**kw))


@pytest.mark.parametrize("kw", [{"rank": 0}, {"rank": 7}, {"confidence": 0}, {"confidence": 1},
                                {"confidence": 0.25}])
def test_hypothesis_valid_scalars_accepted(kw):
    hyp(**kw)


def test_hypothesis_collections_stored_sorted_as_tuples():
    m = (ref("k.b", "2"), ref("k.a", "9", "s"), ref("k.a", "1"))
    c = (ref("k.c", "z"), ref("k.c", "a"))
    h = hyp(materials=m, contradictions=c, unknowns=("zeta", "alpha", "é"))
    assert isinstance(h.material_refs, tuple) and isinstance(h.contradiction_refs, tuple)
    assert isinstance(h.unknowns, tuple)
    exp_m = ref_sorted([REF("k.b", "2"), REF("k.a", "9", "s"), REF("k.a", "1")])
    got_m = [REF(r.ref_kind, r.ref_id, getattr(r, "source_label", None)) for r in h.material_refs]
    assert got_m == exp_m
    assert [r.ref_id for r in h.contradiction_refs] == ["a", "z"]
    assert h.unknowns == ("alpha", "zeta", "é")


def test_hypothesis_id_matches_independent_oracle_without_content():
    h = hyp(kind=IDENTITY, referent=ref("sens.entity_ref", "ball-1"),
            materials=(ref("mmonde.world_state_v0", "ws-2", "cam-A"), ref("f16.real_image_observation_v0", "img-7")),
            modality="f16.generated", contradictions=(ref("gps.domain_measurement", "m-3"),),
            unknowns=("occluded side", "mass"))
    exp = oracle_hypothesis_id(IDENTITY, REF("sens.entity_ref", "ball-1"),
                               [REF("mmonde.world_state_v0", "ws-2", "cam-A"),
                                REF("f16.real_image_observation_v0", "img-7")],
                               "f16.generated", contradictions=[REF("gps.domain_measurement", "m-3")],
                               unknowns=["occluded side", "mass"])
    assert is_hex64(h.hypothesis_id)
    assert h.hypothesis_id == exp


def test_hypothesis_id_matches_independent_oracle_with_content_and_nfc():
    d = datum({"b": 2, "a": ["x", 1]}, dtype="brody.state_text", semantic_refs=["s:2", "s:1"])
    h = hyp(content=d, materials=(ref("k.a", "caf" + "é"),), modality="brody.predicted")
    exp = oracle_hypothesis_id(STATE, REF("sens.entity_ref", "ball-1"), [REF("k.a", "café")],
                               "brody.predicted",
                               content=DATUM({"b": 2, "a": ["x", 1]}, "brody.state_text", ["s:2", "s:1"]))
    assert h.hypothesis_id == exp


def test_hypothesis_id_excludes_rank_and_confidence():
    base = hyp(content=datum())
    assert hyp(content=datum(), rank=0).hypothesis_id == base.hypothesis_id
    assert hyp(content=datum(), rank=9, confidence=0.99).hypothesis_id == base.hypothesis_id
    assert hyp(content=datum(), confidence=0.01).hypothesis_id == base.hypothesis_id


def test_hypothesis_id_independent_of_input_order_of_collections():
    a = hyp(materials=(ref("k.a", "1"), ref("k.a", "2")), unknowns=("u2", "u1"))
    b = hyp(materials=(ref("k.a", "2"), ref("k.a", "1")), unknowns=("u1", "u2"))
    assert a.hypothesis_id == b.hypothesis_id


# Identifier cases A–D, H (spec §8, §9, §11)

def test_case_a_same_content_different_material():
    assert hyp(content=datum(), materials=(ref("k.a", "1"),)).hypothesis_id != \
        hyp(content=datum(), materials=(ref("k.a", "2"),)).hypothesis_id


def test_case_b_same_content_different_source_label():
    assert hyp(content=datum(), materials=(ref("k.a", "1", "cam-A"),)).hypothesis_id != \
        hyp(content=datum(), materials=(ref("k.a", "1", "cam-B"),)).hypothesis_id
    assert hyp(content=datum(), materials=(ref("k.a", "1"),)).hypothesis_id != \
        hyp(content=datum(), materials=(ref("k.a", "1", "cam-A"),)).hypothesis_id


def test_case_c_same_content_different_modality():
    assert hyp(content=datum(), modality="mmonde.observed").hypothesis_id != \
        hyp(content=datum(), modality="brody.predicted").hypothesis_id


def test_case_d_same_material_different_kind():
    assert hyp(kind=STATE).hypothesis_id != hyp(kind=IDENTITY).hypothesis_id


IDENTITY_DECISION_NAMES = {"decision", "decided", "is_same", "same_entity", "same_object", "resolved",
                           "identity_resolved", "resolve_identity", "verdict", "is_identical",
                           "continuity_proven", "is_continuous", "truth", "is_true"}


def test_case_h_content_identity_is_not_world_identity():
    a = hyp(content=datum(), referent=ref("sens.entity_ref", "ball-1"), materials=(ref("k.a", "1"),))
    b = hyp(content=datum(), referent=ref("sens.entity_ref", "ball-2"), materials=(ref("k.a", "2"),))
    assert a.hypothesis_id != b.hypothesis_id
    s = hset((a, b))
    assert len(s.members) == 2
    assert {m.presumed_referent_ref.ref_id for m in s.members} == {"ball-1", "ball-2"}


def test_identity_hypothesis_exposes_no_decision():
    h = hyp(kind=IDENTITY)
    names = {n for n in dir(h) if not n.startswith("_")} | {n for n in dir(type(h)) if not n.startswith("_")}
    assert not (names & IDENTITY_DECISION_NAMES), sorted(names & IDENTITY_DECISION_NAMES)


# ---------------------------------------------------------------------------
# Type C — WorldHypothesisSet
# ---------------------------------------------------------------------------

def two_members():
    return hyp(content=datum("rolling"), materials=(ref("k.a", "1"),)), \
        hyp(content=datum("at rest"), materials=(ref("k.a", "2"),))


def test_set_requires_two_members():
    a, _ = two_members()
    expect_code("M41_INSUFFICIENT_MEMBERS", lambda: hset(()))
    expect_code("M41_INSUFFICIENT_MEMBERS", lambda: hset((a,)))


def test_set_subject_must_be_ref():
    expect_code("M41_INVALID_REF", lambda: hset(two_members(), subject="ball-1"))


@pytest.mark.parametrize("bad", ["dict", "set", "string_element"])
def test_set_members_collection_type(bad):
    a, b = two_members()
    members = {"dict": {"a": a, "b": b}, "set": {"x", "y"}, "string_element": (a, "b")}[bad]
    expect_code("M41_INVALID_COLLECTION", lambda: hset(members))


def test_case_e_exact_duplicate_rejected():
    a, _ = two_members()
    a2 = hyp(content=datum("rolling"), materials=(ref("k.a", "1"),))
    expect_code("M41_DUPLICATE_MEMBER", lambda: hset((a, a2)))


def test_case_f_rank_or_confidence_only_difference_rejected():
    a = hyp(content=datum("rolling"), rank=1)
    b = hyp(content=datum("rolling"), rank=5)
    c = hyp(content=datum("rolling"), confidence=0.9)
    expect_code("M41_DUPLICATE_MEMBER", lambda: hset((a, b)))
    expect_code("M41_DUPLICATE_MEMBER", lambda: hset((a, c)))


def test_case_g_input_order_does_not_change_canonical_order_or_set_id():
    a, b = two_members()
    c = hyp(content=datum("flying"), materials=(ref("k.a", "3"),))
    s1 = hset((a, b, c))
    s2 = hset([c, a, b])
    ids1 = [m.hypothesis_id for m in s1.members]
    assert ids1 == sorted(ids1)
    assert ids1 == [m.hypothesis_id for m in s2.members]
    assert s1.set_id == s2.set_id


def test_set_id_matches_independent_oracle():
    a, b = two_members()
    s = hset((b, a), subject=ref("sens.entity_ref", "ball-1", "sens"))
    exp = oracle_set_id(REF("sens.entity_ref", "ball-1", "sens"), [a.hypothesis_id, b.hypothesis_id])
    assert is_hex64(s.set_id)
    assert s.set_id == exp


SET_FORBIDDEN_NAMES = {"add", "append", "extend", "insert", "remove", "pop", "discard", "clear", "replace",
                       "merge", "fuse", "fusion", "select", "selected", "best", "best_member", "choose", "pick",
                       "winner", "top", "collapse", "resolve", "resolve_identity", "supersede", "superseded",
                       "promote", "promoted", "truth", "is_true", "true_member", "verdict", "rank_members",
                       "sort_by_rank", "revise", "update"}


@pytest.mark.parametrize("which", ["ref", "hypothesis", "set"])
def test_r2_no_fusion_selection_or_truth_surface(which):
    a, b = two_members()
    obj = {"ref": ref(), "hypothesis": a, "set": hset((a, b))}[which]
    names = {n for n in dir(obj) if not n.startswith("_")} | {n for n in dir(type(obj)) if not n.startswith("_")}
    assert not (names & SET_FORBIDDEN_NAMES), sorted(names & SET_FORBIDDEN_NAMES)


def test_r2_members_is_an_immutable_tuple():
    a, b = two_members()
    s = hset([a, b])
    assert type(s.members) is tuple
    assert all(isinstance(m, rt().WorldStateHypothesis) for m in s.members)


# R1 — coexistence

def test_r1_identical_content_different_material_both_kept():
    a = hyp(content=datum(), materials=(ref("k.a", "1"),))
    b = hyp(content=datum(), materials=(ref("k.a", "2"),))
    assert {m.hypothesis_id for m in hset((a, b)).members} == {a.hypothesis_id, b.hypothesis_id}


def test_r1_identical_content_different_source_label_only_both_kept():
    a = hyp(content=datum(), materials=(ref("k.a", "1", "cam-A"),))
    b = hyp(content=datum(), materials=(ref("k.a", "1", "cam-B"),))
    assert len(hset((a, b)).members) == 2


def test_r1_identical_content_different_modality_only_both_kept():
    a = hyp(content=datum(), modality="mmonde.observed")
    b = hyp(content=datum(), modality="brody.predicted")
    assert len(hset((a, b)).members) == 2


def test_r1_contradictory_hypotheses_coexist():
    a = hyp(content=datum("ball moving"), materials=(ref("k.a", "1"),),
            contradictions=(ref("k.a", "2"),))
    b = hyp(content=datum("ball at rest"), materials=(ref("k.a", "2"),),
            contradictions=(ref("k.a", "1"),))
    s = hset((a, b))
    assert len(s.members) == 2
    assert {m.content.value for m in s.members} == {"ball moving", "ball at rest"}


# R3 — identity unresolved

def test_r3_divergent_referents_coexist():
    a = hyp(kind=IDENTITY, referent=ref("sens.entity_ref", "obj-1"))
    b = hyp(kind=IDENTITY, referent=ref("sens.entity_ref", "obj-2"))
    s = hset((a, b))
    assert {m.presumed_referent_ref.ref_id for m in s.members} == {"obj-1", "obj-2"}


def test_r3_equal_referent_does_not_merge_members():
    a = hyp(content=datum("x=1"), referent=ref("sens.entity_ref", "obj-1"), materials=(ref("k.a", "1"),))
    b = hyp(content=datum("x=2"), referent=ref("sens.entity_ref", "obj-1"), materials=(ref("k.a", "2"),))
    s = hset((a, b))
    assert len(s.members) == 2


def test_r3_state_and_identity_hypotheses_distinct_in_one_set():
    a = hyp(kind=STATE)
    b = hyp(kind=IDENTITY)
    assert {m.hypothesis_kind for m in hset((a, b)).members} == {STATE, IDENTITY}


# R4 — preservation and caller mutation

def test_r4_preservation_and_caller_list_mutation():
    mats = [ref("k.a", "1", "src-1"), ref("k.b", "2")]
    contr = [ref("k.c", "9")]
    unk = ["u1", "u2"]
    h = hyp(content=datum(), materials=mats, contradictions=contr, unknowns=unk,
            referent=ref("sens.entity_ref", "r-1"), modality="gps.measured")
    before = (h.material_refs, h.contradiction_refs, h.unknowns, h.hypothesis_id)
    mats.append(ref("k.z", "evil"))
    mats.pop(0)
    contr.clear()
    unk[0] = "mutated"
    after = (h.material_refs, h.contradiction_refs, h.unknowns, h.hypothesis_id)
    assert before == after
    assert {(r.ref_kind, r.ref_id, getattr(r, "source_label", None)) for r in h.material_refs} == \
        {("k.a", "1", "src-1"), ("k.b", "2", None)}
    assert [r.ref_id for r in h.contradiction_refs] == ["9"]
    assert h.unknowns == ("u1", "u2")
    assert h.presumed_referent_ref == ref("sens.entity_ref", "r-1")
    assert h.modality_label == "gps.measured"


def test_r4_set_members_survive_caller_mutation():
    a, b = two_members()
    members = [a, b]
    s = hset(members)
    sid = s.set_id
    members.clear()
    assert len(s.members) == 2 and s.set_id == sid


# R5 — modality

OBSERVATION_CONVERSION_NAMES = {"observed", "is_observed", "as_observation", "to_observation", "observed_fact",
                                "promote_to_observation", "as_fact", "realized", "is_realized", "verified",
                                "is_verified", "set_modality", "with_modality", "normalize_modality"}


@pytest.mark.parametrize("modality", ["brody.predicted", "f16.generated", "sim.simulated", "sens.inferred",
                                      "mmonde.observed"])
def test_r5_modality_preserved_byte_for_byte(modality):
    h = hyp(modality=modality)
    assert h.modality_label == modality
    other = hyp(modality="zz.other", materials=(ref("k.a", "other"),))
    s = hset((h, other))
    assert {m.modality_label for m in s.members} == {modality, "zz.other"}


def test_r5_no_observation_conversion_surface():
    a, b = two_members()
    for obj in (a, hset((a, b))):
        names = {n for n in dir(obj) if not n.startswith("_")} | \
            {n for n in dir(type(obj)) if not n.startswith("_")}
        assert not (names & OBSERVATION_CONVERSION_NAMES), sorted(names & OBSERVATION_CONVERSION_NAMES)


# R6 — effects

EXPECTED_EFFECT_KEYS = {"memory_write", "emits_act", "b8", "binder", "kernel", "kx108", "external_io",
                        "durable_state_write"}


def test_r6_effects_exact_keys_all_false_and_read_only():
    eff = rt().M41_EFFECTS
    assert isinstance(eff, Mapping)
    assert set(eff.keys()) == EXPECTED_EFFECT_KEYS
    assert all(eff[k] is False for k in EXPECTED_EFFECT_KEYS)
    with pytest.raises(TypeError):
        eff["memory_write"] = True  # type: ignore[index]
    assert all(eff[k] is False for k in EXPECTED_EFFECT_KEYS)


def test_r6_construction_performs_no_io(monkeypatch):
    mod = rt()

    def forbidden(*_a, **_k):
        raise AssertionError("M41 construction attempted a forbidden external effect")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(io, "open", forbidden)
    monkeypatch.setattr(os, "open", forbidden)
    monkeypatch.setattr(os, "remove", forbidden)
    monkeypatch.setattr(os, "rename", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    r1 = mod.WorldMaterialRef(ref_kind="k.a", ref_id="1", source_label="s")
    r2 = mod.WorldMaterialRef(ref_kind="k.a", ref_id="2")
    subj = mod.WorldMaterialRef(ref_kind="sens.entity_ref", ref_id="ball-1")
    h1 = mod.WorldStateHypothesis(hypothesis_kind=STATE, presumed_referent_ref=subj, material_refs=(r1,),
                                  modality_label="mmonde.observed", content=datum(), unknowns=("u",))
    h2 = mod.WorldStateHypothesis(hypothesis_kind=IDENTITY, presumed_referent_ref=subj, material_refs=(r2,),
                                  modality_label="brody.predicted", contradiction_refs=(r1,), rank=1,
                                  confidence=0.5)
    s = mod.WorldHypothesisSet(subject_ref=subj, members=(h1, h2))
    assert len(s.members) == 2


FORBIDDEN_IMPORT_PREFIXES = ("periphery", "app.cognition", "app.knowledge", "app.semantic", "app.reconstruction",
                             "app.harness", "app.security", "app.router", "socket", "requests", "urllib", "http",
                             "sqlite3", "subprocess", "neo4j", "graphiti", "shelve", "pickle", "asyncio",
                             "threading", "multiprocessing", "tempfile", "shutil")


def test_r6_runtime_imports_nothing_forbidden():
    mod = rt()
    pkg_dir = Path(mod.__file__).resolve().parent
    files = sorted(pkg_dir.rglob("*.py"))
    assert files, "app/world_model contains no Python source"
    offending = []
    for f in files:
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            for n in names:
                if any(n == p or n.startswith(p + ".") for p in FORBIDDEN_IMPORT_PREFIXES):
                    offending.append((f.name, n))
                if "binder" in n.lower() or "kx108" in n.lower():
                    offending.append((f.name, n))
    assert not offending, offending


# R7 — order without authority

def test_r7_order_independent_of_rank_and_confidence():
    a, b = two_members()
    c = hyp(content=datum("flying"), materials=(ref("k.a", "3"),))
    plain = hset((a, b, c))
    order = [m.hypothesis_id for m in plain.members]
    # give the highest rank/confidence to the member that sorts LAST by id
    last_id = order[-1]
    ranked = []
    for h, mats, txt in ((a, ("k.a", "1"), "rolling"), (b, ("k.a", "2"), "at rest"), (c, ("k.a", "3"), "flying")):
        if h.hypothesis_id == last_id:
            ranked.append(hyp(content=datum(txt), materials=(ref(*mats),), rank=0, confidence=1.0))
        else:
            ranked.append(hyp(content=datum(txt), materials=(ref(*mats),), rank=9, confidence=0.0))
    s = hset(tuple(reversed(ranked)))
    assert [m.hypothesis_id for m in s.members] == order
    assert s.members[-1].hypothesis_id == last_id
    assert s.set_id == plain.set_id


# ---------------------------------------------------------------------------
# Immutability
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("which,attr", [("ref", "ref_id"), ("ref", "source_label"),
                                        ("hypothesis", "modality_label"), ("hypothesis", "material_refs"),
                                        ("hypothesis", "hypothesis_id"), ("hypothesis", "unknowns"),
                                        ("set", "members"), ("set", "set_id")])
def test_immutable_assignment_and_deletion(which, attr):
    a, b = two_members()
    obj = {"ref": ref("k.a", "1", "s"), "hypothesis": a, "set": hset((a, b))}[which]
    before = getattr(obj, attr)
    with pytest.raises(Exception):
        setattr(obj, attr, "tampered")
    with pytest.raises(Exception):
        delattr(obj, attr)
    assert getattr(obj, attr) == before


def test_immutable_returned_collections_and_stable_ids():
    a, b = two_members()
    s = hset((a, b))
    h = s.members[0]
    hid, sid = h.hypothesis_id, s.set_id
    for coll in (s.members, h.material_refs, h.contradiction_refs, h.unknowns):
        assert type(coll) is tuple
    with pytest.raises(Exception):
        s.members[0].material_refs[0].ref_id = "x"  # type: ignore[misc]
    assert h.hypothesis_id == hid and s.set_id == sid
    assert isinstance(h.content, TypedCognitiveDatum)


def test_contradiction_refs_cannot_be_dropped_or_altered():
    contr = (ref("k.c", "1"), ref("k.c", "2"))
    h = hyp(contradictions=contr)
    with pytest.raises(Exception):
        h.contradiction_refs = ()  # type: ignore[misc]
    assert [r.ref_id for r in h.contradiction_refs] == ["1", "2"]


def test_ids_are_unprefixed_lowercase_hex64():
    a, b = two_members()
    s = hset((a, b))
    assert is_hex64(a.hypothesis_id) and is_hex64(s.set_id)


# ---------------------------------------------------------------------------
# NB1 hardening — float payloads inside `content` must use M32 canonical JSON (RFC 8785 numbers),
# not Python json.dumps formatting. Expected vectors are built from literal RFC 8785 number tokens
# written by hand ("1" for 1.0, "1e-7" for 1e-7, "0.5"), substituted into the independent oracle's
# canonical preimage; neither the runtime nor M32 nor json number formatting produces the expected value.
# ---------------------------------------------------------------------------

RFC8785_LITERALS = {"__F_ONE__": "1", "__F_TINY__": "1e-7", "__F_HALF__": "0.5"}


def oracle_float_hypothesis_id(placeholder_value, materials, modality="mmonde.observed"):
    """Hypothesis id whose content value contains placeholders replaced by literal RFC 8785 tokens."""
    pre = {
        "schema_version": "m41.world_state_hypothesis.v1",
        "hypothesis_kind": STATE,
        "presumed_referent": REF("sens.entity_ref", "ball-1"),
        "content": DATUM(placeholder_value, dtype="arm.measurement"),
        "material_refs": ref_sorted(list(materials)),
        "modality_label": modality,
        "contradiction_refs": [],
        "unknowns": [],
    }
    text = canon(pre)
    for placeholder, literal in RFC8785_LITERALS.items():
        text = text.replace('"' + placeholder + '"', literal)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_float_oracle_literals_differ_from_json_dumps():
    # Oracle self-check (passes at RED): the RFC 8785 literals are not what json.dumps would emit.
    assert json.dumps(1.0) == "1.0" and RFC8785_LITERALS["__F_ONE__"] == "1"
    assert json.dumps(1e-7) == "1e-07" and RFC8785_LITERALS["__F_TINY__"] == "1e-7"


def test_float_content_one_point_zero_uses_canonical_number():
    h = hyp(content=datum({"x": 1.0}, dtype="arm.measurement"), materials=(ref("k.a", "f1"),))
    assert h.hypothesis_id == oracle_float_hypothesis_id({"x": "__F_ONE__"}, [REF("k.a", "f1")])


def test_float_content_1e_minus_7_uses_canonical_number():
    h = hyp(content=datum({"y": 1e-7}, dtype="arm.measurement"), materials=(ref("k.a", "f2"),))
    assert h.hypothesis_id == oracle_float_hypothesis_id({"y": "__F_TINY__"}, [REF("k.a", "f2")])


def test_float_content_nested_list_uses_canonical_numbers():
    h = hyp(content=datum({"z": [1.0, 1e-7, 0.5]}, dtype="arm.measurement"), materials=(ref("k.a", "f3"),))
    exp = oracle_float_hypothesis_id({"z": ["__F_ONE__", "__F_TINY__", "__F_HALF__"]}, [REF("k.a", "f3")])
    assert h.hypothesis_id == exp


def test_float_content_one_point_zero_and_int_one_share_canonical_identity():
    # RFC 8785 serializes 1.0 and 1 identically; the content identity therefore coincides.
    a = hyp(content=datum({"x": 1.0}, dtype="arm.measurement"), materials=(ref("k.a", "f4"),))
    b = hyp(content=datum({"x": 1}, dtype="arm.measurement"), materials=(ref("k.a", "f4"),))
    assert a.hypothesis_id == b.hypothesis_id


def test_float_rank_confidence_still_excluded_with_float_content():
    base = hyp(content=datum({"y": 1e-7}, dtype="arm.measurement"), materials=(ref("k.a", "f5"),))
    other = hyp(content=datum({"y": 1e-7}, dtype="arm.measurement"), materials=(ref("k.a", "f5"),),
                rank=3, confidence=0.75)
    assert base.hypothesis_id == other.hypothesis_id
