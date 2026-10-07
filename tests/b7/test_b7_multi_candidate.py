"""B7 multiple candidates and confidence (spec §11, §15; T13, T14)."""
from __future__ import annotations


def _setup(b7, entry_factory):
    e = entry_factory("Le script et le test sont prêts. Lance-le.", unresolved_references=("u2:le",),
                      units=("u1", "u2"), uncertainty=(), unit_objects={"u1": ["le script", "le test"]})
    (req,) = b7.detect_unresolved(e)
    return e, req


def _cand(b7, req, raw_candidate_factory, antecedent, confidence="MEDIUM", provider="provider:test"):
    return b7.translate(raw_candidate_factory(req, remaining_unknowns=[], confidence_class=confidence,
                                              provider_ref=provider,
                                              proposed_resolution={"mention": "u2:le", "antecedent": antecedent}), req)


def test_t13_two_valid_candidates_no_winner(b7, entry_factory, raw_candidate_factory, providers):
    e, req = _setup(b7, entry_factory)
    a = _cand(b7, req, raw_candidate_factory, "le script", "HIGH")
    b = _cand(b7, req, raw_candidate_factory, "le test", "LOW")
    res = b7.validate_candidates(req, (a, b), origin=e, provider_roles=providers)
    assert res.verdict == b7.CognitiveValidationVerdict.STILL_UNRESOLVED
    assert {c.candidate_id for c in res.candidates} == {a.candidate_id, b.candidate_id}
    assert res.derived_state is None


def test_t13_majority_and_provider_priority_do_not_win(b7, entry_factory, raw_candidate_factory, providers):
    e, req = _setup(b7, entry_factory)
    cands = (_cand(b7, req, raw_candidate_factory, "le script", "HIGH"),
             _cand(b7, req, raw_candidate_factory, "le script", "HIGH", provider="provider:other"),
             _cand(b7, req, raw_candidate_factory, "le test", "LOW"))
    res = b7.validate_candidates(req, cands, origin=e, provider_roles=providers)
    assert res.verdict == b7.CognitiveValidationVerdict.STILL_UNRESOLVED and len(res.candidates) == 3


def test_t14_confidence_is_not_truth(b7, entry_factory, raw_candidate_factory, providers):
    e, req = _setup(b7, entry_factory)
    invented = b7.translate(raw_candidate_factory(req, remaining_unknowns=[], confidence_class="HIGH",
                                                  proposed_resolution={"mention": "u2:le", "antecedent": "le build"}),
                            req)
    assert b7.validate_candidate(req, invented, origin=e, provider_roles=providers).verdict == \
        b7.CognitiveValidationVerdict.REJECT
    low = _cand(b7, req, raw_candidate_factory, "le script", "LOW")
    assert b7.validate_candidate(req, low, origin=e, provider_roles=providers).verdict == \
        b7.CognitiveValidationVerdict.ACCEPT_AS_STRUCTURED_CONTEXT
    unknown = _cand(b7, req, raw_candidate_factory, "le script", "UNKNOWN")
    assert unknown.confidence_class == b7.ConfidenceClass.UNKNOWN
