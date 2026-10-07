"""RED tranche 1 — closed canonical enums and verdict / state / reason separation (spec §2, §4, §8,
§9.1, §9.5)."""
from __future__ import annotations

import re

SPEC_REASON_CODES = (
    "attestation_inadmissible", "attestation_missing", "backdated_record", "containment_not_satisfied",
    "contradiction_inadmissible", "contradiction_unresolved", "evidence_inadmissible", "forbidden_transition",
    "malformed_object", "malformed_slot", "multiple_predecessors_unsupported", "no_eligible_predecessor",
    "no_temporal_overlap", "open_contradiction", "oversize_object", "partition_not_partial",
    "predecessor_mismatch", "reason_missing", "ref_binding_mismatch", "referenced_claim_not_promoted",
    "resolution_relation_invalid", "slot_mismatch", "slot_occupied", "stale_request",
    "staleness_trigger_inadmissible", "successor_gap_not_open", "temporal_relation_indeterminate",
    "verification_not_satisfied", "verifier_inadmissible",
)
SPEC_CLAIM_STATES = ("CANDIDATE", "HELD", "REJECTED", "SUPPORTED", "VERIFIED", "PROMOTED", "CONTESTED",
                     "SUPERSEDED", "INVALIDATED", "STALE")
SPEC_GAP_STATES = ("OPEN", "RESOLVED", "SUPERSEDED")
SPEC_VERDICTS = ("APPLIED", "REJECTED", "NO_OP_DUPLICATE")
SPEC_CLAIM_CLASSES = ("FORMAL_CLAIM", "CODE_BUILD_CLAIM", "PHYSICAL_CLAIM", "DOCUMENTARY_CLAIM", "DOMAIN_CLAIM",
                      "HUMAN_DECLARATION", "ORGANIZATIONAL_POLICY")


def test_expected_vocabularies_match_the_closed_spec(spec_text):
    sec = spec_text[spec_text.index("### 9.5 ReasonCode"):spec_text.index("## 10. Point-in-time contract")]
    assert tuple(re.findall(r"^\| `([a-z0-9_]+)` \|", sec, re.M)) == SPEC_REASON_CODES
    states = spec_text[spec_text.index("## 8. States"):spec_text.index("### 8.1")]
    assert tuple(re.findall(r"^\| ([A-Z]+) \|", states, re.M)) == SPEC_CLAIM_STATES
    assert "TRANSITION_VERDICT_ENUM = APPLIED | REJECTED | NO_OP_DUPLICATE" in spec_text
    assert "state OPEN / RESOLVED / SUPERSEDED" in spec_text


def test_transition_verdict_is_exactly_the_closed_enum(b8):
    assert tuple(v.value for v in b8.TransitionVerdict) == SPEC_VERDICTS
    assert not hasattr(b8.TransitionVerdict, "HELD")


def test_claim_state_and_gap_state_are_exact(b8):
    assert tuple(s.value for s in b8.ClaimState) == SPEC_CLAIM_STATES
    assert tuple(s.value for s in b8.GapState) == SPEC_GAP_STATES
    assert tuple(c.value for c in b8.ClaimClass) == SPEC_CLAIM_CLASSES


def test_reason_code_is_a_closed_lowercase_enum_of_29(b8):
    values = [r.value for r in b8.ReasonCode]
    assert len(b8.ReasonCode) == 29 and len(set(values)) == 29
    assert tuple(sorted(values)) == SPEC_REASON_CODES
    assert all(re.fullmatch(r"[a-z]+(_[a-z]+)*", v) for v in values)
    for v in values:
        assert b8.ReasonCode(v).value == v
    for alias in ("STALE_REQUEST", "Stale_Request", "staleRequest", "MULTIPLE_PREDECESSORS_UNSUPPORTED"):
        try:
            b8.ReasonCode(alias)
        except ValueError:
            continue
        raise AssertionError(f"alias accepted: {alias}")


def test_verdict_state_reason_are_distinct_dimensions(b8):
    assert b8.TransitionVerdict.REJECTED is not b8.ClaimState.REJECTED
    assert type(b8.TransitionVerdict.REJECTED) is not type(b8.ClaimState.REJECTED)
    assert b8.TransitionVerdict.REJECTED != b8.ClaimState.REJECTED
    assert "HELD" in {s.value for s in b8.ClaimState}
    assert "HELD" not in {v.value for v in b8.TransitionVerdict}
    assert {r.value for r in b8.ReasonCode}.isdisjoint({s.value for s in b8.ClaimState})
    assert {r.value for r in b8.ReasonCode}.isdisjoint({v.value for v in b8.TransitionVerdict})
