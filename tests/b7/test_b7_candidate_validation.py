"""B7 candidate lifecycle, translator and validation gate (T5-T11, T19-T29, T33-T35, T40)."""
from __future__ import annotations

import dataclasses
import math

import pytest

from app.harness.state_explicit.registry import WorkingStateRegistry


def _ready(b7, coref_entry, raw_candidate_factory, **overrides):
    (req,) = b7.detect_unresolved(coref_entry)
    return req, b7.translate(raw_candidate_factory(req, **overrides), req)


def _verdict(b7, req, cand, origin, providers):
    return b7.validate_candidate(req, cand, origin=origin, provider_roles=providers)


# ── lifecycle ────────────────────────────────────────────────────────────────
def test_lifecycle_proposed_then_ready(b7, coref_entry, raw_candidate_factory):
    (req,) = b7.detect_unresolved(coref_entry)
    assert b7.propose(raw_candidate_factory(req), req).candidate_status == b7.CandidateStatus.PROPOSED
    assert b7.translate(raw_candidate_factory(req), req).candidate_status == b7.CandidateStatus.READY_FOR_VALIDATION


def test_t34_proposed_candidate_at_gate_is_rejected(b7, coref_entry, raw_candidate_factory, providers):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory)
    proposed = dataclasses.replace(cand, candidate_status=b7.CandidateStatus.PROPOSED)
    assert _verdict(b7, req, proposed, coref_entry, providers).verdict == b7.CognitiveValidationVerdict.REJECT


# ── happy path and derived state (T11, T12) ─────────────────────────────────
def test_t11_t12_accept_creates_new_entry_and_keeps_origin(b7, coref_entry, raw_candidate_factory, providers):
    before = coref_entry.content_digest
    req, cand = _ready(b7, coref_entry, raw_candidate_factory)
    res = _verdict(b7, req, cand, coref_entry, providers)
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    d = res.derived_state
    assert d.state_id != coref_entry.state_id and coref_entry.content_digest == before
    p = d.payload
    assert p["derived_from_state_id"] == coref_entry.state_id
    assert p["resolution_request_id"] == req.request_id and p["resolution_candidate_id"] == cand.candidate_id
    assert p["provider_ref"] == "provider:test" and p["role_ref"] == "RESOLVER"
    assert set(req.provenance_refs) <= set(d.provenance)
    assert "other_open_item" in d.uncertainty


def test_t29_duplicate_derived_state_fails_closed(b7, coref_entry, raw_candidate_factory, providers):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory)
    res = _verdict(b7, req, cand, coref_entry, providers)
    reg = WorkingStateRegistry()
    b7.register_derived(reg, res)
    with pytest.raises(ValueError):
        b7.register_derived(reg, res)
    assert len(reg.list_entries()) == 1


# ── request match (T19-T21, T35) ────────────────────────────────────────────
@pytest.mark.parametrize("field,value", [("request_id", "req:other"), ("origin_state_id", "sens:other"),
                                         ("original_state_digest", "0" * 16),
                                         ("candidate_kind", "ENTITY_BINDING")])
def test_t19_t20_t21_t35_mismatch_rejected(b7, coref_entry, raw_candidate_factory, providers, field, value):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory, **{field: value})
    assert _verdict(b7, req, cand, coref_entry, providers).verdict == b7.CognitiveValidationVerdict.REJECT


# ── role / provider eligibility (T22, T23) ──────────────────────────────────
def test_t22_ineligible_role_rejected(b7, coref_entry, raw_candidate_factory, providers):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory, proposer_role="COMPARATOR")
    assert _verdict(b7, req, cand, coref_entry, providers).verdict == b7.CognitiveValidationVerdict.REJECT


@pytest.mark.parametrize("provider", ["provider:unknown", "provider:other"])
def test_t23_ineligible_provider_rejected(b7, coref_entry, raw_candidate_factory, provider):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory, provider_ref=provider)
    roles = {"provider:other": frozenset({"CRITIC"})}               # eligibility is data, not a provider identity
    assert _verdict(b7, req, cand, coref_entry, roles).verdict == b7.CognitiveValidationVerdict.REJECT


# ── content conservation (T6-T10) ───────────────────────────────────────────
@pytest.mark.parametrize("overrides", [
    {"remaining_unknowns": []},                                                                     # T6
    {"resolves": ["unresolved_references:u9:la"]},                                                 # question changed
    {"provenance_refs": []},                                                                        # provenance dropped
    {"proposed_resolution": {"mention": "u2:le", "antecedent": "le script", "participants": ["Nadia"]}},  # T8
    {"proposed_resolution": {"mention": "u2:le", "antecedent": "le script",
                             "relations": [{"kind": "CAUSES", "source": "u2", "target": "u7"}]}},   # T9
    {"proposed_resolution": {"mention": "u2:le", "antecedent": "le script", "times": ["2026-10-06"]}},  # T10
    {"proposed_resolution": {"mention": "u2:le", "antecedent": "le script", "sources": ["Marie"]}},     # T10
    {"proposed_resolution": {"mention": "u2:le", "antecedent": "le build"}},                         # unsupported antecedent
])
def test_t6_to_t10_content_conservation(b7, coref_entry, raw_candidate_factory, providers, overrides):
    req, cand = _ready(b7, coref_entry, raw_candidate_factory, **overrides)
    assert _verdict(b7, req, cand, coref_entry, providers).verdict == b7.CognitiveValidationVerdict.REJECT


def test_t7_hidden_contradiction_rejected(b7, entry_factory, raw_candidate_factory, providers):
    e = entry_factory("Le script est prêt. Lance-le.", unresolved_references=("u2:le",), units=("u1", "u2"),
                      contradictions=("EXECUTE(p):requested_and_forbidden:u1/u2",), uncertainty=(),
                      unit_objects={"u1": ["le script"]})
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    hidden = b7.translate(raw_candidate_factory(req, remaining_unknowns=[]), req)
    kept = b7.translate(raw_candidate_factory(req, remaining_unknowns=[],
                                              contradictions=["EXECUTE(p):requested_and_forbidden:u1/u2"]), req)
    assert _verdict(b7, req, hidden, e, providers).verdict == b7.CognitiveValidationVerdict.REJECT
    assert _verdict(b7, req, kept, e, providers).verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


# ── OTHER_EXPLICIT_UNRESOLVED (T24) ─────────────────────────────────────────
def test_t24_other_explicit_never_accepts(b7, entry_factory, raw_candidate_factory, providers):
    e = entry_factory("Paul ne lance P.", ambiguities=("bare_ne:u1",), uncertainty=("ambiguity:bare_ne:u1",))
    (req,) = b7.detect_unresolved(e)
    assert req.required_candidate_kind == b7.RequiredCandidateKind.CHARACTERIZATION_ONLY
    good = b7.translate(raw_candidate_factory(req, candidate_kind="CHARACTERIZATION_ONLY", proposer_role="UNDERSTANDER",
                                              proposed_resolution={"characterization": "negation without pas"},
                                              remaining_unknowns=["ambiguity:bare_ne:u1"]), req)
    assert _verdict(b7, req, good, e, providers).verdict == b7.CognitiveValidationVerdict.STILL_UNRESOLVED
    resolver = b7.translate(raw_candidate_factory(req, candidate_kind="CHARACTERIZATION_ONLY",
                                                  proposed_resolution={"characterization": "x"},
                                                  remaining_unknowns=["ambiguity:bare_ne:u1"]), req)
    assert _verdict(b7, req, resolver, e, providers).verdict == b7.CognitiveValidationVerdict.REJECT


# ── temporal / world (T33, T40) ─────────────────────────────────────────────
def test_t33_linguistic_time_is_not_physical_chronology(b7, entry_factory, raw_candidate_factory, providers):
    # requalified 2026-10-07 (STRUCTURED_TEMPORAL_REFERENCE_ONLY): "hier" is SENS-structured deixis
    e = entry_factory("Paul a lancé P hier quand Nadia part.", ambiguities=("temporal_scope_ambiguous:u2:host=u1",),
                      units=("u1", "u2"), uncertainty=(), deixis=("hier",))
    (req,) = b7.detect_unresolved(e)
    assert b7.ForbiddenOperation.ESTABLISH_PHYSICAL_CHRONOLOGY in req.forbidden_operations
    base = dict(candidate_kind="TEMPORAL_REFERENCE_INTERPRETATION", remaining_unknowns=[])
    ok = b7.translate(raw_candidate_factory(req, proposed_resolution={"anchor": "hier", "times": ["hier"]}, **base), req)
    res = _verdict(b7, req, ok, e, providers)
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert res.derived_state.payload["physical_chronology_established"] is False
    bad = b7.translate(raw_candidate_factory(req, proposed_resolution={"anchor": "hier", "times": ["hier"],
                                                                        "physical_chronology_established": True},
                                             **base), req)
    assert _verdict(b7, req, bad, e, providers).verdict == b7.CognitiveValidationVerdict.REJECT


def test_t40_world_hypothesis_without_evidence_stays_unresolved(b7, entry_factory, raw_candidate_factory, providers):
    e = entry_factory("Le capteur est chaud.", missing=("unanalyzed_predicative_content:0-21:root",), uncertainty=())
    req = b7.make_request(e, b7.UnresolvedKind.WORLD_OR_PHYSICAL_REFERENCE, "missing",
                          "unanalyzed_predicative_content:0-21:root")
    cand = b7.translate(raw_candidate_factory(req, candidate_kind="WORLD_REFERENCE_HYPOTHESIS", proposer_role="INVESTIGATOR",
                                              proposed_resolution={"hypothesis": "le capteur"}, evidence_refs=[],
                                              remaining_unknowns=[], confidence_class="HIGH"), req)
    # requalified by B7-T (canonical request policy): no explicit marker maps to WORLD_OR_PHYSICAL_REFERENCE
    # (M1-M10), so this hand-built request is not one the detector would construct and is now REJECTed
    # (stricter than STILL_UNRESOLVED); the invariant under test -- a world hypothesis never becomes
    # structured context -- is unchanged
    res = _verdict(b7, req, cand, e, providers)
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT and res.reasons == ("request_identity_mismatch",)
    assert res.derived_state is None


# ── translator, strict JSON, bounds (T26-T28) ───────────────────────────────
@pytest.mark.parametrize("drop", ["provenance_refs", "evidence_refs", "proposer_role", "candidate_kind",
                                  "proposed_resolution", "remaining_unknowns"])
def test_t28_translator_never_invents_missing_fields(b7, coref_entry, raw_candidate_factory, drop):
    (req,) = b7.detect_unresolved(coref_entry)
    raw = raw_candidate_factory(req)
    del raw[drop]
    with pytest.raises(ValueError):
        b7.translate(raw, req)


@pytest.mark.parametrize("field,value", [("candidate_kind", "FREE_TEXT"), ("confidence_class", "CERTAIN"),
                                         ("proposer_role", "PROVIDER_BRODY")])
def test_t28_t36_translator_rejects_unknown_enums(b7, coref_entry, raw_candidate_factory, field, value):
    (req,) = b7.detect_unresolved(coref_entry)
    with pytest.raises(ValueError):
        b7.translate(raw_candidate_factory(req, **{field: value}), req)


def _loop():
    x: list = []
    x.append(x)
    return x


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, b"x", {1, 2}, object(), {1: "a"},
                                 {"a": {2: "b"}}, "LOOP"])
def test_t26_strict_json_candidate_rejected(b7, coref_entry, raw_candidate_factory, bad):
    (req,) = b7.detect_unresolved(coref_entry)
    value = _loop() if bad == "LOOP" else bad
    with pytest.raises(ValueError):
        b7.translate(raw_candidate_factory(req, proposed_resolution={"mention": "u2:le", "antecedent": "le script",
                                                                     "extra": value}), req)


def test_t27_oversized_candidate_rejected(b7, coref_entry, raw_candidate_factory):
    (req,) = b7.detect_unresolved(coref_entry)
    huge = {"mention": "u2:le", "antecedent": "le script", "note": "x" * (b7.MAX_CANDIDATE_CHARS + 1)}
    with pytest.raises(ValueError):
        b7.translate(raw_candidate_factory(req, proposed_resolution=huge), req)
