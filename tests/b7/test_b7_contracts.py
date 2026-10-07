"""B7 closed vocabularies (determinism contract §1-§3; T34-T36)."""
from __future__ import annotations

import pytest

_UNRESOLVED = ["COREFERENCE", "SOURCE_SCOPE", "CONDITIONAL_ATTACHMENT", "TEMPORAL_REFERENCE", "DEIXIS",
               "ENTITY_IDENTITY", "CONTRADICTION", "UNKNOWN_TERM_OR_PREDICATE", "DOMAIN_SPECIFIC_AMBIGUITY",
               "WORLD_OR_PHYSICAL_REFERENCE", "OTHER_EXPLICIT_UNRESOLVED"]
_KIND = {"COREFERENCE": "REFERENCE_BINDING", "SOURCE_SCOPE": "SOURCE_SCOPE_INTERPRETATION",
         "CONDITIONAL_ATTACHMENT": "CONDITIONAL_ATTACHMENT_INTERPRETATION",
         "TEMPORAL_REFERENCE": "TEMPORAL_REFERENCE_INTERPRETATION", "DEIXIS": "DEICTIC_BINDING",
         "ENTITY_IDENTITY": "ENTITY_BINDING", "CONTRADICTION": "CONTRADICTION_ANALYSIS",
         "UNKNOWN_TERM_OR_PREDICATE": "TERM_OR_PREDICATE_INTERPRETATION",
         "DOMAIN_SPECIFIC_AMBIGUITY": "DOMAIN_INTERPRETATION",
         "WORLD_OR_PHYSICAL_REFERENCE": "WORLD_REFERENCE_HYPOTHESIS",
         "OTHER_EXPLICIT_UNRESOLVED": "CHARACTERIZATION_ONLY"}
_OPS = {"DECIDE", "ACT", "SELF_AUTHORIZE", "WRITE_DURABLE_MEMORY", "WRITE_WORKING_STATE", "MUTATE_KERNEL",
        "MUTATE_ORIGIN_STATE", "PROMOTE_TO_KNOWLEDGE", "BYPASS_VALIDATION", "SELECT_WINNER", "PROPOSE_RESOLUTION",
        "ESTABLISH_WORLD_FACT", "ESTABLISH_PHYSICAL_CHRONOLOGY"}
_DEFAULT = {"DECIDE", "ACT", "SELF_AUTHORIZE", "WRITE_DURABLE_MEMORY", "WRITE_WORKING_STATE", "MUTATE_KERNEL",
            "MUTATE_ORIGIN_STATE", "PROMOTE_TO_KNOWLEDGE", "BYPASS_VALIDATION"}
_AUTHORITY_WORDS = ["ALLOW", "HOLD", "BLOCK", "ACT", "EXECUTE", "DECIDE", "AUTHORIZED", "APPROVED", "ACCEPTED",
                    "VALID", "TRUE"]


def _values(enum):
    return {m.value for m in enum}


def test_candidate_status_is_closed_lifecycle(b7):
    assert _values(b7.CandidateStatus) == {"PROPOSED", "READY_FOR_VALIDATION"}


@pytest.mark.parametrize("word", _AUTHORITY_WORDS + ["UNKNOWN_STATUS"])
def test_t36_candidate_status_rejects_unknown_and_authority_values(b7, word):
    with pytest.raises(ValueError):
        b7.CandidateStatus(word)


def test_validation_verdict_is_separate_from_candidate_status(b7):
    assert _values(b7.CognitiveValidationVerdict) == {"ACCEPT_AS_STRUCTURED_CONTEXT", "REJECT", "STILL_UNRESOLVED"}
    assert not (_values(b7.CognitiveValidationVerdict) & _values(b7.CandidateStatus))
    assert not ({"ALLOW", "HOLD", "BLOCK", "ACT", "EXECUTE", "DECIDE"} & _values(b7.CognitiveValidationVerdict))


def test_unresolved_kind_vocabulary(b7):
    assert _values(b7.UnresolvedKind) == set(_UNRESOLVED)


def test_required_candidate_kind_is_one_to_one(b7):
    assert _values(b7.RequiredCandidateKind) == set(_KIND.values())
    for kind, required in _KIND.items():
        assert b7.required_candidate_kind_for(b7.UnresolvedKind(kind)).value == required


@pytest.mark.parametrize("bad", ["FREE_TEXT_KIND", "reference_binding", ""])
def test_t36_unknown_required_kind_rejected(b7, bad):
    with pytest.raises(ValueError):
        b7.RequiredCandidateKind(bad)


def test_forbidden_operations_vocabulary_and_default(b7):
    assert _values(b7.ForbiddenOperation) == _OPS
    assert {o.value for o in b7.DEFAULT_FORBIDDEN_OPERATIONS} == _DEFAULT
    assert not ({"ALLOW", "HOLD", "BLOCK"} & _OPS)


@pytest.mark.parametrize("kind,added", [
    ("CONTRADICTION", {"SELECT_WINNER"}),
    ("TEMPORAL_REFERENCE", {"ESTABLISH_PHYSICAL_CHRONOLOGY"}),
    ("WORLD_OR_PHYSICAL_REFERENCE", {"ESTABLISH_WORLD_FACT", "ESTABLISH_PHYSICAL_CHRONOLOGY"}),
    ("OTHER_EXPLICIT_UNRESOLVED", {"PROPOSE_RESOLUTION"}),
    ("COREFERENCE", set()),
])
def test_forbidden_operations_by_kind(b7, kind, added):
    ops = {o.value for o in b7.forbidden_operations_for(b7.UnresolvedKind(kind))}
    assert ops == _DEFAULT | added


def test_confidence_class_vocabulary(b7):
    assert _values(b7.ConfidenceClass) == {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}


def test_role_vocabulary_excludes_the_gate(b7):
    assert _values(b7.CognitiveRole) == {"UNDERSTANDER", "INVESTIGATOR", "RESOLVER", "CRITIC", "TRANSLATOR",
                                         "COMPARATOR", "BUILDER_PROPOSER"}
