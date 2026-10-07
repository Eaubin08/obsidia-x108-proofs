"""B7-H regression: SUBSTRING_COINCIDENCE != SEMANTIC_ADMISSIBILITY (D-B7-1) and
STRING_CONTAINMENT != RESOLUTION_IDENTITY (D-B7-2). Probes reproduced by the B7-G adversarial audit."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.sens_adapter import sens_state_entries
from conftest import PROVIDERS, make_entry, raw_candidate


def _verdict(b7, entry, request, **overrides):
    cand = b7.translate(raw_candidate(request, **overrides), request)
    return b7.validate_candidate(request, cand, origin=entry, provider_roles=PROVIDERS)


def _coref(raw, uncertainty=(), marker="u2:le", structured=None):
    e = make_entry(raw, unresolved_references=(marker,), units=("u1", "u2"), uncertainty=uncertainty,
                   unit_objects=structured)
    return e


# ── D-B7-1: no acceptance from character coincidence ────────────────────────
@pytest.mark.parametrize("raw,extra", [
    ("Marie va à Paris. Le script est prêt. Lance-le.", {"sources": ["ari"]}),            # inside "Paris"
    ("Paul parle. Le script est prêt. Lance-le.", {"participants": ["e"]}),              # single character
    ("Paul parle. Le script est prêt. Lance-le.", {"participants": ["al"]}),             # inside "Paul"
    ("Le script est prêt demain. Lance-le.", {"times": ["mai"]}),                        # inside "demain"
    ("Le script est prêt. Lance-le.", {"antecedent": "script est"}),                     # not a referent
    ("Le script est prêt. Lance-le.", {"antecedent": "cript"}),                          # prefix overlap
    ("Le script est prêt. Lance-le.", {"antecedent": "le scrip"}),                       # suffix overlap
    ("Le script est prêt. Lance-le.", {"antecedent": "prêt. lance"}),                    # across punctuation
    ("Le script est prêt. Lance-le.", {"sources": ["rêt"]}),                             # inside accented word
])
def test_d_b7_1_substring_coincidence_is_rejected(b7, raw, extra):
    e = _coref(raw)
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le", "antecedent": "le script", **extra}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict == \
        b7.CognitiveValidationVerdict.REJECT


# requalified 2026-10-07 (human doctrine option A, STRUCTURED_REFERENT_ONLY): formerly ACCEPT from raw text
@pytest.mark.parametrize("antecedent", ["le script", "Le Script", "LE SCRIPT"])
def test_option_a_unstructured_exact_referent_not_accepted(b7, antecedent):
    e = _coref("Le script est prêt. Lance-le.")
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le", "antecedent": antecedent}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict != \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


@pytest.mark.parametrize("antecedent", ["le script", "Le Script", "LE SCRIPT"])
def test_option_a_structured_referent_accepted(b7, antecedent):
    e = _coref("Le script est prêt. Lance-le.", structured={"u1": ["le script"]})
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le", "antecedent": antecedent}
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict == \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


@pytest.mark.parametrize("raw,field,value", [("Le test est prêt. Lance-le.", "antecedent", "le test"),
                                             ("Le script de Paul est prêt. Lance-le.", "participants", ["Paul"]),
                                             ("Marie dit que le script est prêt. Lance-le.", "sources", ["Marie"]),
                                             ("Paul le mange. Lance-le.", "antecedent", "le mange")])
def test_option_a_raw_text_never_establishes_a_referent(b7, raw, field, value):
    e = _coref(raw)
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": "u2:le"} if field == "antecedent" else {"mention": "u2:le", "antecedent": "le script"}
    proposal[field] = value
    assert _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal).verdict != \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


def test_option_a_lexicon_is_irrelevant_to_structured_referents(b7):
    e = _coref("Paul prend la lance. Lance-le.", structured={"u1": ["la lance"]})
    (req,) = b7.detect_unresolved(e)
    assert _verdict(b7, e, req, remaining_unknowns=[],
                    proposed_resolution={"mention": "u2:le", "antecedent": "la lance"}).verdict == \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


def test_d_b7_1_structured_referent_first(b7):
    # SENS-shaped units (as in "Paul lance le script et Nadia teste P"): structured subjects / objects
    frame = {"raw": "Paul lance le script et Nadia teste P. Lance-le.", "oblique_arguments": [],
             "units": [{"id": "u1", "subject": "paul", "objects": [{"text": "le script"}]},
                       {"id": "u2", "subject": "nadia", "objects": [{"text": "p"}]}, {"id": "u3", "objects": []}]}
    e = make_entry("Paul lance le script et Nadia teste P. Lance-le.", unresolved_references=("u3:le",),
                   units=("u1", "u2", "u3"), uncertainty=(), extra={"semantic_frame": frame})
    (req,) = b7.detect_unresolved(e)
    for antecedent in ("le script", "nadia", "p"):                      # structured referents
        ok = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u3:le", "antecedent": antecedent})
        assert ok.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT, antecedent
    for antecedent in ("script et", "lance", "teste p"):                # contiguous text, not a referent
        bad = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u3:le", "antecedent": antecedent})
        assert bad.verdict == b7.CognitiveValidationVerdict.REJECT, antecedent


# ── D-B7-2: only the exact canonical unresolved item may be removed ─────────
def test_d_b7_2_unrelated_uncertainties_sharing_the_marker_are_kept(b7):
    unc = ("unresolved_reference:u2:le", "ambiguous_antecedent:u2:le:other_problem", "subject_unresolved:u2:le_x")
    e = _coref("Le script est prêt. Lance-le.", uncertainty=unc, structured={"u1": ["le script"]})
    (req,) = b7.detect_unresolved(e)
    assert _verdict(b7, e, req, remaining_unknowns=[]).verdict == b7.CognitiveValidationVerdict.REJECT
    res = _verdict(b7, e, req, remaining_unknowns=list(unc[1:]))
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert set(unc[1:]) <= set(res.derived_state.uncertainty)


@pytest.mark.parametrize("marker,other", [("u2:l", "unresolved_reference:u2:la"), ("u2:l", "u2:la"),
                                          ("u2:le", "unresolved_reference:u2:les"), ("u2:le", "xu2:le")])
def test_d_b7_2_prefix_suffix_collisions_are_kept(b7, marker, other):
    e = _coref("Le script est prêt. Lance-le.", uncertainty=(f"unresolved_reference:{marker}", other), marker=marker,
               structured={"u1": ["le script"]})
    (req,) = b7.detect_unresolved(e)
    proposal = {"mention": marker, "antecedent": "le script"}
    res = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution=proposal)
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT and res.reasons == ("unresolved_content_lost",)


def test_d_b7_2_exact_real_sens_forms_are_removable(b7):
    (e,) = sens_state_entries("Le script est prêt. Lance-le.")
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    mention = req.problem_refs[0].split(":", 1)[1]
    keep = [u for u in e.uncertainty if u not in (mention, f"frame:unresolved_reference:{mention}")]
    before = (e.content_digest, e.uncertainty)
    res = _verdict(b7, e, req, remaining_unknowns=keep, proposed_resolution={"mention": mention, "antecedent": "le script"})
    # requalified (structured-referent-only): real SENS structures no referent here, so the candidate is
    # rejected on the referent rule — the exact uncertainty forms already passed the conservation check
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT and res.reasons == ("unsupported_content_invented",)
    assert (e.content_digest, e.uncertainty) == before                                  # origin never mutated


def test_d_b7_2_sibling_markers_survive_one_resolution(b7):
    e = make_entry("Le script est prêt. Lance-le.", unresolved_references=("u2:le",), units=("u1", "u2"),
                   ambiguities=("bare_ne:u1", "subject_unresolved:u2"), unit_objects={"u1": ["le script"]})
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    assert _verdict(b7, e, req, remaining_unknowns=[]).verdict == b7.CognitiveValidationVerdict.REJECT
    res = _verdict(b7, e, req, remaining_unknowns=["bare_ne:u1", "subject_unresolved:u2"])
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


# ── B7-J: D-B7-1a (verb-headed determiner fallback) and D-B7-1b (closed structured set) ───────────
@pytest.mark.parametrize("raw,antecedent", [("Nadia le teste. Lance-le.", "le teste"),
                                            ("Paul la lance. Lance-le.", "la lance"),
                                            ("Il un parle. Lance-le.", "un parle"),
                                            ("Paul veut le tester. Lance-le.", "le tester"),
                                            ("Il la parle. Lance-le.", "la parle"),
                                            ("Il un lance. Lance-le.", "un lance")])
def test_d_b7_1a_verb_headed_fallback_rejected(b7, raw, antecedent):
    e = _coref(raw)
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u2:le", "antecedent": antecedent})
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT


# requalified 2026-10-07 (option A): the former "legitimate fallback" ACCEPT came from raw text only
@pytest.mark.parametrize("raw,antecedent", [("Le script est prêt. Lance-le.", "le script"),
                                            ("Le test est prêt. Lance-le.", "le test")])
def test_option_a_former_fallback_controls_not_accepted(b7, raw, antecedent):
    e = _coref(raw)
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={"mention": "u2:le", "antecedent": antecedent})
    assert res.verdict != b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


def test_d_b7_1b_structured_set_is_closed(b7):
    raw = "Paul lance le script et Nadia le teste avec le mot. Lance-le."
    frame = {"raw": raw, "oblique_arguments": [],
             "units": [{"id": "u1", "subject": "paul", "objects": [{"text": "le script"}]},
                       {"id": "u2", "subject": "nadia", "objects": [{"text": "le"}]},
                       {"id": "u3", "objects": [{"text": "le"}]}]}
    e = make_entry(raw, unresolved_references=("u3:le",), units=("u1", "u2", "u3"), uncertainty=(),
                   extra={"semantic_frame": frame})
    (req,) = b7.detect_unresolved(e)

    def v(antecedent):
        return _verdict(b7, e, req, remaining_unknowns=[],
                        proposed_resolution={"mention": "u3:le", "antecedent": antecedent}).verdict
    assert v("le teste") == b7.CognitiveValidationVerdict.REJECT          # exact raw text, not a structured referent
    assert v("le mot") == b7.CognitiveValidationVerdict.REJECT            # noun-like raw phrase outside the closed set
    assert v("le script") == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert v("Paul") == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


# ── B7-L: closed proposed_resolution schema (unvalidated claim keys never enter accepted context) ─
@pytest.mark.parametrize("extra", [{"agent": "Nadia"}, {"participant": "Nadia"}, {"subject": "Nadia"},
                                   {"referent": "le build"}, {"time": "2030-01-01"}, {"source": "Marie"},
                                   {"cause": "Nadia a cassé le build"}, {"Antecedent": "le build"}])
def test_unvalidated_proposal_keys_are_rejected(b7, extra):
    e = _coref("Le script est prêt. Lance-le.", structured={"u1": ["le script"]})
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", **extra})
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT


def test_descriptive_quoted_text_remains_allowed(b7):
    e = _coref("Le script est prêt. Lance-le.", structured={"u1": ["le script"]})
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", "quoted_text": "ALLOW"})
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


# ── B7-L: relations are admissible only as existing structured relations ───────────────────────
def _rel_entry():
    frame = {"raw": "Paul lance P parce que Nadia a lancé Q. Lance-le.", "oblique_arguments": [],
             "units": [{"id": "u1", "subject": "paul", "objects": [{"text": "p"}]},
                       {"id": "u2", "subject": "nadia", "objects": [{"text": "q"}]}, {"id": "u3", "objects": []}],
             "relations": [{"kind": "CAUSES", "source": "u2", "target": "u1", "evidence": "parce que"}]}
    return make_entry(frame["raw"], unresolved_references=("u3:le",), units=("u1", "u2", "u3"), uncertainty=(),
                      extra={"semantic_frame": frame})


@pytest.mark.parametrize("rel", [{"kind": "CAUSES", "source": "u1", "target": "u2"},             # reversed
                                 {"kind": "PREVENTS", "source": "u2", "target": "u1"},           # other kind
                                 {"source": "u2", "target": "u1"},                                # kind missing
                                 {"kind": "CAUSES", "source": "u2", "target": "u1", "note": "x"},  # extra key
                                 {"kind": "CAUSES", "source": "u1", "target": "u3"}])            # invented
def test_invented_relation_between_existing_units_rejected(b7, rel):
    e = _rel_entry()
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u3:le", "antecedent": "p", "relations": [rel]})
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT


def test_existing_structured_relation_is_admissible(b7):
    e = _rel_entry()
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={
        "mention": "u3:le", "antecedent": "p", "relations": [{"kind": "CAUSES", "source": "u2", "target": "u1"}]})
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


# ── B7-M: structured temporal refs, string-only descriptives, separated derived payload ─────────
def _tm(deixis=(), raw="Le script est prêt demain. Lance-le."):
    return make_entry(raw, unresolved_references=("u2:le",), units=("u1", "u2"), uncertainty=(),
                      unit_objects={"u1": ["le script"]}, deixis=deixis)


@pytest.mark.parametrize("extra", [{"times": ["script"]}, {"times": ["prêt"]}, {"times": ["lance"]},
                                   {"times": ["mai"]}, {"times": ["2035-01-01"]}, {"times": ["demain"]},
                                   {"anchor": "le script est"}, {"anchor": "script"}, {"anchor": "demain"},
                                   {"anchor": "u1"}])
def test_m1_raw_text_temporal_claims_rejected(b7, extra):
    e = _tm()                                                              # no structured deixis
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", **extra})
    assert res.verdict != b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


@pytest.mark.parametrize("extra", [{"times": ["demain"]}, {"anchor": "demain"}, {"times": ["Demain"]}])
def test_m1_structured_deixis_is_admissible(b7, extra):
    e = _tm(deixis=("demain",))
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", **extra})
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    assert res.derived_state.payload["physical_chronology_established"] is False


@pytest.mark.parametrize("extra", [{"times": ["script"]}, {"anchor": "le script est"}])
def test_m1_structured_deixis_set_is_closed(b7, extra):
    e = _tm(deixis=("demain",))
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", **extra})
    assert res.verdict != b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT


@pytest.mark.parametrize("extra", [{"quoted_text": {"decision_authority": "SELF"}},
                                   {"characterization": {"participants": ["Nadia"]}},
                                   {"hypothesis": {"world_fact": "bridge collapsed"}},
                                   {"quoted_text": ["HOLD"]}, {"characterization": 3}, {"hypothesis": True}])
def test_m2_descriptive_values_are_strings_only(b7, extra):
    e = _tm()
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[],
                   proposed_resolution={"mention": "u2:le", "antecedent": "le script", **extra})
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT


def test_m3_derived_payload_separates_validated_from_unverified(b7):
    e = _tm(deixis=("demain",))
    (req,) = b7.detect_unresolved(e)
    res = _verdict(b7, e, req, remaining_unknowns=[], proposed_resolution={
        "mention": "u2:le", "antecedent": "le script", "times": ["demain"], "quoted_text": "ALLOW",
        "characterization": "Nadia is participant", "hypothesis": "world fact is certain"},
        evidence_refs=["proof:verified_by_kx108"], context_refs=["memory:durable_fact_42"],
        assumptions=["this is definitely true"])
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    p = res.derived_state.payload
    assert p["validated"] == {"mention": "u2:le", "antecedent": "le script", "times": ["demain"]}
    u = p["unverified_descriptive"]
    assert u["quoted_text"] == "ALLOW" and u["characterization"] == "Nadia is participant"
    assert u["hypothesis"] == "world fact is certain"
    assert u["evidence_refs"] == ["proof:verified_by_kx108"] and u["context_refs"] == ["memory:durable_fact_42"]
    assert u["assumptions"] == ["this is definitely true"]
    assert (u["is_truth"], u["is_authority"], u["is_durable_knowledge"]) == (False, False, False)
    for leaked in ("proposed_resolution", "evidence_refs", "context_refs", "assumptions", "quoted_text"):
        assert leaked not in p


# ── B7-O: candidate contradictions / provenance never become structural ────────────────────────
def _o_entry():
    return make_entry("Le script est prêt. Lance-le.", unresolved_references=("u2:le",), units=("u1", "u2"),
                      uncertainty=(), unit_objects={"u1": ["le script"]}, contradictions=("conflict:origin",))


def _o_accept(b7, **overrides):
    e = _o_entry()
    req = next(r for r in b7.detect_unresolved(e) if r.unresolved_kind == b7.UnresolvedKind.COREFERENCE)
    res = _verdict(b7, e, req, remaining_unknowns=[], **overrides)
    assert res.verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    return e, req, res.derived_state


@pytest.mark.parametrize("extra", ["EXECUTE(x):requested_and_forbidden:u1/u9", "verified:false", "kx108:block",
                                   "memory:fact", "world_fact:true", "ALLOW", "origin contradiction resolved"])
def test_o_candidate_extra_contradictions_never_root(b7, extra):
    e, _, d = _o_accept(b7, contradictions=["conflict:origin", extra])
    assert d.payload["contradictions"] == ["conflict:origin"]
    assert d.payload["unverified_descriptive"]["candidate_contradictions"] == [extra]
    assert e.payload["contradictions"] == ["conflict:origin"]


@pytest.mark.parametrize("extra", ["kx108:verified_decision", "memory:durable_fact_42", "world:true",
                                   "kx108:allow", "authority:self", "verified:true"])
def test_o_candidate_provenance_never_structural(b7, extra):
    e, req, d = _o_accept(b7, contradictions=["conflict:origin"],
                          provenance_refs=[*e_prov(), extra])
    assert d.provenance == (*req.provenance_refs, "app.cognition.b7.validation")
    assert extra not in d.provenance
    assert d.payload["unverified_descriptive"]["provenance_refs"] == [extra]
    assert e.provenance == req.provenance_refs


def e_prov():
    return list(_o_entry().provenance)


# ── B7-Q: candidate identity is bound to the canonical typed content ───────────────────────────
import dataclasses as _dc
import json as _json


def _q():
    e = make_entry("Le script et le test sont prêts demain. Lance-le.", unresolved_references=("u2:le",),
                   units=("u1", "u2"), uncertainty=(), unit_objects={"u1": ["le script", "le test"]}, deixis=("demain",))
    (req,) = __import__("app.cognition.b7", fromlist=["x"]).detect_unresolved(e)
    return e, req


def _q_verdict(b7, e, req, cand):
    return b7.validate_candidate(req, cand, origin=e, provider_roles=PROVIDERS)


_MUTATIONS = {
    "proposed_resolution_json": _json.dumps({"mention": "u2:le", "antecedent": "le test"}),
    "evidence_refs": ("other:evidence",), "context_refs": ("other:context",),
    "provenance_refs": ("app.semantic.lattice.french_grammar.parse_utterance", "app.semantic.lattice.semantic_closure",
                        "x"),
    "remaining_unknowns": ("added",), "contradictions": ("added",), "assumptions": ("added",),
    "provider_ref": "provider:other", "resolves": ("unresolved_references:u2:le",),
}


@pytest.mark.parametrize("field", sorted(_MUTATIONS) + ["confidence_class", "proposer_role", "candidate_kind"])
def test_q_mutated_content_with_old_identity_rejected(b7, field):
    e, req = _q()
    cand = b7.translate(raw_candidate(req, remaining_unknowns=[]), req)
    assert _q_verdict(b7, e, req, cand).verdict == b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    value = {"confidence_class": b7.ConfidenceClass.HIGH, "proposer_role": b7.CognitiveRole.CRITIC,
             "candidate_kind": b7.RequiredCandidateKind.REFERENCE_BINDING}.get(field, _MUTATIONS.get(field))
    if field == "resolves":
        value = ("unresolved_references:u2:le", "x")
    if field == "candidate_kind":
        value = b7.RequiredCandidateKind.ENTITY_BINDING
    mutated = _dc.replace(cand, **{field: value})
    res = _q_verdict(b7, e, req, mutated)
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT and res.derived_state is None


@pytest.mark.parametrize("change", [{"candidate_id": "b7cand_victim000000"}, {"candidate_digest": "b7dig_0123456789abcdef"},
                                    {"candidate_id": "b7cand_victim000000", "candidate_digest": "b7dig_victim000000"}])
def test_q_forged_identity_rejected(b7, change):
    e, req = _q()
    cand = b7.translate(raw_candidate(req, remaining_unknowns=[]), req)
    res = _q_verdict(b7, e, req, _dc.replace(cand, **change))
    assert res.verdict == b7.CognitiveValidationVerdict.REJECT and res.reasons == ("candidate_identity_mismatch",)


def test_q_identity_is_deterministic_and_content_sensitive(b7):
    e, req = _q()
    a = b7.translate(raw_candidate(req, remaining_unknowns=[]), req)
    b = b7.translate(raw_candidate(req, remaining_unknowns=[]), req)
    c = b7.translate(raw_candidate(req, remaining_unknowns=[],
                                   proposed_resolution={"mention": "u2:le", "antecedent": "le test"}), req)
    assert (a.candidate_id, a.candidate_digest) == (b.candidate_id, b.candidate_digest)
    assert a.candidate_digest != c.candidate_digest and a.candidate_id != c.candidate_id
    res = _q_verdict(b7, e, req, a)
    assert res.derived_state.payload["resolution_candidate_id"] == a.candidate_id


# ── B7-R: full-width (256-bit) SHA-256 B7 identities ───────────────────────────────────────────
import hashlib as _hashlib

from app.harness.state_explicit.contracts import canonical_json as _canonical_json


def _r():
    e, req = _q()
    import app.cognition.b7 as m
    return m, e, req, m.translate(raw_candidate(req, remaining_unknowns=[]), req)


def _hex(value, prefix):
    assert value.startswith(prefix)
    body = value[len(prefix):]
    assert all(c in "0123456789abcdef" for c in body)
    return body


def test_r_candidate_identity_is_full_width_and_independently_recomputable():
    m, e, req, cand = _r()
    assert len(_hex(cand.candidate_digest, "b7dig_")) == 64
    assert len(_hex(cand.candidate_id, "b7cand_")) == 64
    payload = {k: v for k, v in cand.to_dict().items() if k not in ("candidate_id", "candidate_digest", "candidate_status")}
    expected = _hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    assert cand.candidate_digest == "b7dig_" + expected and cand.candidate_id == "b7cand_" + expected


def test_r_request_identity_is_full_width_and_independently_recomputable():
    m, e, req, _ = _q_full()  # noqa: F841
    field, marker = req.problem_refs[0].split(":", 1)
    # requalified by B7-S: request identity material = (origin_state_id, full origin digest, field, marker)
    full_origin = "b7orig_" + _hashlib.sha256(_canonical_json(e.to_dict()).encode("utf-8")).hexdigest()
    expected = _hashlib.sha256(_canonical_json([req.origin_state_id, full_origin, field, marker]).encode("utf-8")).hexdigest()
    assert req.request_id == "b7req_" + expected and len(_hex(req.request_id, "b7req_")) == 64


def _q_full():
    import app.cognition.b7 as m
    e, req = _q()
    return m, e, req, None


def test_r_request_identity_replay_and_sensitivity():
    import app.cognition.b7 as m
    a = m.detect_unresolved(make_entry("x", unresolved_references=("u1:le",)))[0].request_id
    b = m.detect_unresolved(make_entry("x", unresolved_references=("u1:le",)))[0].request_id
    c = m.detect_unresolved(make_entry("x", unresolved_references=("u1:la",)))[0].request_id
    assert a == b and a != c


@pytest.mark.parametrize("tail", ["1" * 48, "2" * 48])
def test_r_same_64bit_prefix_is_not_the_same_identity(tail):
    m, e, req, cand = _r()
    prefix16 = cand.candidate_digest[len("b7dig_"):][:16]
    forged = "b7dig_" + prefix16 + tail
    assert forged != cand.candidate_digest
    res = m.validate_candidate(req, _dc.replace(cand, candidate_digest=forged, candidate_id="b7cand_" + prefix16 + tail),
                               origin=e, provider_roles=PROVIDERS)
    assert res.verdict == m.CognitiveValidationVerdict.REJECT and res.reasons == ("candidate_identity_mismatch",)


def test_r_legacy_64bit_identity_rejected():
    m, e, req, cand = _r()
    short = cand.candidate_digest[len("b7dig_"):][:16]
    for change in ({"candidate_id": "b7cand_" + short}, {"candidate_digest": "b7dig_" + short},
                   {"candidate_id": "b7cand_" + short, "candidate_digest": "b7dig_" + short}):
        res = m.validate_candidate(req, _dc.replace(cand, **change), origin=e, provider_roles=PROVIDERS)
        assert res.verdict == m.CognitiveValidationVerdict.REJECT



# ── B7-S: requests are bound to the full-width origin content digest ───────────────────────────
from app.harness.state_explicit.contracts import StateEntry as _StateEntry


def _origin(raw):
    return make_entry(raw, unresolved_references=("u1:le",), units=("u1",), uncertainty=(),
                      unit_objects={"u1": []})


def _full(entry):
    return "b7orig_" + _hashlib.sha256(_canonical_json(entry.to_dict()).encode("utf-8")).hexdigest()


def test_s_full_origin_digest_extends_the_b6_digest():
    import app.cognition.b7 as m
    a = _origin("Lance-le.")
    (req,) = m.detect_unresolved(a)
    assert req.origin_full_digest == _full(a) and len(_hex(req.origin_full_digest, "b7orig_")) == 64
    assert req.origin_full_digest[len("b7orig_"):][:16] == a.content_digest


def test_s_same_state_id_distinct_origins_have_distinct_requests():
    import app.cognition.b7 as m
    a, b = _origin("Lance-le."), _origin("Exécute-le.")
    assert a.state_id == b.state_id
    ra, rb = m.detect_unresolved(a)[0], m.detect_unresolved(b)[0]
    assert ra.problem_refs == rb.problem_refs
    assert ra.origin_full_digest != rb.origin_full_digest and ra.request_id != rb.request_id


def _accept_raw(req, structured_text):
    return raw_candidate(req, remaining_unknowns=[], proposed_resolution={"mention": "u1:le", "antecedent": structured_text})


def test_s_simulated_b6_collision_cannot_replay(monkeypatch):
    import app.cognition.b7 as m
    a = make_entry("Le script. Lance-le.", unresolved_references=("u1:le",), units=("u1", "u0"), uncertainty=(),
                   unit_objects={"u0": ["le script"]})
    b = make_entry("Le test. Lance-le.", unresolved_references=("u1:le",), units=("u1", "u0"), uncertainty=(),
                   unit_objects={"u0": ["le script"]})
    monkeypatch.setattr(_StateEntry, "content_digest", property(lambda self: "deadbeefdeadbeef"))  # simulated 64-bit collision
    assert a.state_id == b.state_id and a.content_digest == b.content_digest and a.to_dict() != b.to_dict()
    ra, rb = m.detect_unresolved(a)[0], m.detect_unresolved(b)[0]
    assert ra.origin_full_digest != rb.origin_full_digest and ra.request_id != rb.request_id
    cand_a = m.translate(_accept_raw(ra, "le script"), ra)
    assert m.validate_candidate(ra, cand_a, origin=a, provider_roles=PROVIDERS).verdict ==         m.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT                               # positive control
    for request, origin in ((rb, b), (ra, b)):                                                 # foreign / stale origin
        res = m.validate_candidate(request, cand_a, origin=origin, provider_roles=PROVIDERS)
        assert res.verdict == m.CognitiveValidationVerdict.REJECT and res.derived_state is None


@pytest.mark.parametrize("change", ["origin_full_digest", "request_id"])
def test_s_forged_origin_or_request_identity_rejected(change):
    import app.cognition.b7 as m
    a = make_entry("Le script. Lance-le.", unresolved_references=("u1:le",), units=("u1", "u0"), uncertainty=(),
                   unit_objects={"u0": ["le script"]})
    (req,) = m.detect_unresolved(a)
    forged_value = ("b7orig_" if change == "origin_full_digest" else "b7req_") + "0" * 64
    forged = _dc.replace(req, **{change: forged_value})
    cand = m.translate(_accept_raw(forged, "le script"), forged)
    res = m.validate_candidate(forged, cand, origin=a, provider_roles=PROVIDERS)
    assert res.verdict == m.CognitiveValidationVerdict.REJECT and res.reasons == ("origin_identity_mismatch",)
