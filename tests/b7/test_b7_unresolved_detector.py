"""B7 mechanical unresolved detector (contract §4-§6; T1, T2, T12, T30-T32, T37-T39)."""
from __future__ import annotations

import pytest

from app.harness.state_explicit.contracts import StateStatus
from app.harness.state_explicit.sens_adapter import sens_state_entries


@pytest.mark.parametrize("field,marker,kind", [
    ("unresolved_references", "u1:le", "COREFERENCE"),                                              # M1
    ("ambiguities", "ambiguous_antecedent:u2:qui:", "COREFERENCE"),                                 # M2
    ("semantic_closure.reasons", "event_reference:AMBIGUOUS:x:u1", "COREFERENCE"),                  # M3
    ("missing", "unanalyzed_predicative_content:0-11:detached_source_of=u2", "SOURCE_SCOPE"),       # M4
    ("ambiguities", "condition_scope_ambiguous:c1", "CONDITIONAL_ATTACHMENT"),                      # M5
    ("ambiguities", "exception_condition_open:u1", "CONDITIONAL_ATTACHMENT"),                       # M5
    ("ambiguities", "temporal_scope_ambiguous:u2:host=u1", "TEMPORAL_REFERENCE"),                   # M6
    ("ambiguities", "temporal_subordinate_open:u1", "TEMPORAL_REFERENCE"),                          # M6
    ("contradictions", "EXECUTE(p):requested_and_forbidden:u1/u2", "CONTRADICTION"),                # M7
    ("ambiguities", "occurrence_conflict_open:u1:u2", "CONTRADICTION"),                             # M8
    ("ambiguities", "infinitive_under_unrecognized_governor:u1", "UNKNOWN_TERM_OR_PREDICATE"),      # M9
    ("ambiguities", "complement_under_unresolved_governor:u1", "UNKNOWN_TERM_OR_PREDICATE"),        # M9
    ("ambiguities", "unresolved_complement_governance:u1", "UNKNOWN_TERM_OR_PREDICATE"),            # M9
    ("ambiguities", "subject_unresolved:u1", "OTHER_EXPLICIT_UNRESOLVED"),                          # M10
    ("ambiguities", "coordination_attachment_ambiguous:u2", "OTHER_EXPLICIT_UNRESOLVED"),           # M10
    ("ambiguities", "bare_ne:u1", "OTHER_EXPLICIT_UNRESOLVED"),                                     # M10
    ("missing", "unanalyzed_predicative_content:26-35:root", "OTHER_EXPLICIT_UNRESOLVED"),          # M10
    ("missing", "unanalyzed_predicative_content:25-31:conditional_protasis", "OTHER_EXPLICIT_UNRESOLVED"),
    ("semantic_closure.reasons", "meta_target:UNRESOLVED:x:u1", "OTHER_EXPLICIT_UNRESOLVED"),
    ("semantic_closure.reasons", "no_predicate_unit", "OTHER_EXPLICIT_UNRESOLVED"),
    ("ambiguities", "future_prefix_never_seen:u9", "OTHER_EXPLICIT_UNRESOLVED"),                    # T31
])
def test_t30_marker_table_m1_to_m10(b7, field, marker, kind):
    assert b7.classify_marker(field, marker) == b7.UnresolvedKind(kind)


def test_t30_classification_is_deterministic(b7):
    a = [b7.classify_marker("ambiguities", "subject_unresolved:u1") for _ in range(5)]
    assert len(set(a)) == 1


@pytest.mark.parametrize("word", ["coreference", "unknown", "conditional", "yesterday", "world", "physical",
                                  "error", "contradiction", "hier", "selon Marie"])
def test_no_free_text_routing(b7, entry_factory, word):
    assert b7.detect_unresolved(entry_factory(f"Paul dit {word}.", status=StateStatus.KNOWN)) == ()
    reqs = b7.detect_unresolved(entry_factory(f"Paul dit {word}.", ambiguities=("bare_ne:u1",)))
    assert [r.unresolved_kind for r in reqs] == [b7.UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED]


def test_current_coreference_reality(b7):
    (d3,) = sens_state_entries("Le script que Paul lance, il échoue.")
    assert {r.unresolved_kind for r in b7.detect_unresolved(d3)} == {b7.UnresolvedKind.OTHER_EXPLICIT_UNRESOLVED}
    (live,) = sens_state_entries("Lance-le.")
    reqs = b7.detect_unresolved(live)
    assert [r.unresolved_kind for r in reqs] == [b7.UnresolvedKind.COREFERENCE]
    assert reqs[0].problem_refs == ("unresolved_references:u1:le",)


def test_no_current_source_categories(b7, entry_factory):
    e = entry_factory("Lance P maintenant ici.", status=StateStatus.KNOWN, extra={
        "semantic_frame": {"raw": "x", "units": [{"id": "u1"}], "oblique_arguments": [], "deixis": ["maintenant"],
                           "constraints": ["NO_EXECUTE(p)"], "evidence_needs": ["truth_value"],
                           "presupposed_referents": ["le test"]}})
    assert b7.detect_unresolved(e) == ()                                                            # T38
    never = {b7.UnresolvedKind.DEIXIS, b7.UnresolvedKind.ENTITY_IDENTITY,
             b7.UnresolvedKind.DOMAIN_SPECIFIC_AMBIGUITY, b7.UnresolvedKind.WORLD_OR_PHYSICAL_REFERENCE}
    for text in ["Lance P maintenant ici.", "Lance-le.", "Lance P et ne lance pas P.",
                 "Si, selon Marie, le script qui teste P échoue, lance R."]:
        (s,) = sens_state_entries(text)
        assert not ({r.unresolved_kind for r in b7.detect_unresolved(s)} & never)


def test_t32_multiple_markers_conserved_in_canonical_order(b7, entry_factory):
    e = entry_factory("x", missing=("unanalyzed_predicative_content:0-1:root",),
                      ambiguities=("subject_unresolved:u1", "bare_ne:u1"), unresolved_references=("u1:le",),
                      contradictions=("EXECUTE(p):requested_and_forbidden:u1/u2",))
    reqs = b7.detect_unresolved(e)
    assert [r.problem_refs for r in reqs] == [
        ("unresolved_references:u1:le",), ("contradictions:EXECUTE(p):requested_and_forbidden:u1/u2",),
        ("ambiguities:bare_ne:u1",), ("ambiguities:subject_unresolved:u1",),
        ("missing:unanalyzed_predicative_content:0-1:root",)]
    assert len({r.request_id for r in reqs}) == 5
    assert [r.request_id for r in reqs] == [r.request_id for r in b7.detect_unresolved(e)]


def test_t39_frame_reasons_are_not_double_counted(b7, entry_factory):
    e = entry_factory("x", unresolved_references=("u1:le",), reasons=("frame:unresolved_reference:u1:le",))
    assert len(b7.detect_unresolved(e)) == 1


@pytest.mark.parametrize("status,state_type,expected", [
    (StateStatus.OPEN, "SENS_FRAME", ["OTHER_EXPLICIT_UNRESOLVED"]),
    (StateStatus.UNKNOWN, "SENS_FRAME", ["OTHER_EXPLICIT_UNRESOLVED"]),
    (StateStatus.UNKNOWN, "NATIVE_MEMORY_STATUS", ["OTHER_EXPLICIT_UNRESOLVED"]),
    (StateStatus.ERROR, "SENS_FRAME_ERROR", []),                                                    # T37
    (StateStatus.KNOWN, "SENS_FRAME", []),
])
def test_status_fallbacks(b7, entry_factory, status, state_type, expected):
    e = entry_factory("x", status=status, state_type=state_type)
    reqs = b7.detect_unresolved(e)
    assert [r.unresolved_kind.value for r in reqs] == expected
    if expected:
        assert reqs[0].problem_refs == (f"status:{status.value}",)


def test_t1_t2_t12_request_derived_mechanically(b7, coref_entry):
    before = coref_entry.content_digest
    (r,) = b7.detect_unresolved(coref_entry)
    assert coref_entry.content_digest == before                                                     # T12
    assert r.origin_state_id == coref_entry.state_id and r.origin_state_type == "SENS_FRAME"
    assert r.unresolved_kind == b7.UnresolvedKind.COREFERENCE
    assert r.problem_refs == ("unresolved_references:u2:le",)
    assert r.source_refs == (coref_entry.source_ref,)
    assert r.provenance_refs == coref_entry.provenance
    assert r.uncertainty == coref_entry.uncertainty
    assert r.original_state_digest == coref_entry.content_digest
    assert r.required_candidate_kind == b7.RequiredCandidateKind.REFERENCE_BINDING
    assert r.forbidden_operations == b7.forbidden_operations_for(b7.UnresolvedKind.COREFERENCE)
    assert r.allowed_role_ids == b7.eligible_roles(b7.UnresolvedKind.COREFERENCE)
    assert isinstance(r.context_refs, tuple) and r.why_resolution_needed
