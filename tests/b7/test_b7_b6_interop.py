"""B7 / B6 interop: only typed validated context is trusted (spec §21; T17, T18).

Targets the future B7 admission API, not the current Brody seam (B6-10 stays FROZEN_DEFERRED and is
not turned into a false current regression here).
"""
from __future__ import annotations

import pytest

from app.harness.state_explicit.context_assembly import assemble_context
from app.harness.state_explicit.registry import WorkingStateRegistry

_M = {"categories": ["PURE_RESPONSE"], "matrix": {"PURE_RESPONSE": {"brody_may": ["repondre"]}}}


@pytest.mark.parametrize("mapping", [
    {"emits_act": True},
    {"decision_authority": "SELF", "memory_write": True, "kernel_mutation": True},
    {"schema": "B6_STATE_EXPLICIT_CONTEXT_PACKET_V1", "packet_id": "b6ctx_0000000000000000", "state": []},
    {"verdict": "ACCEPT_AS_STRUCTURED_CONTEXT", "derived_state": {"state_id": "x"}},
])
def test_t17_arbitrary_dict_is_never_trusted(b7, mapping):
    with pytest.raises(ValueError):
        b7.admit_trusted_context(mapping)


def test_t18_typed_packet_and_accepted_result_are_admitted(b7, coref_entry, raw_candidate_factory, providers):
    reg = WorkingStateRegistry()
    reg.register(coref_entry)
    packet = assemble_context("Lance-le.", reg, capability_matrix=_M)
    # requalified by B7-U (TYPED OBJECT != TRUSTED OBJECT): B7 cannot prove issuance of a raw B6 packet,
    # so its admission surface now fails closed; only an ACCEPT result issued by the B7 gate is admitted
    with pytest.raises(ValueError):
        b7.admit_trusted_context(packet)
    (req,) = b7.detect_unresolved(coref_entry)
    res = b7.validate_candidate(req, b7.translate(raw_candidate_factory(req), req), origin=coref_entry,
                                provider_roles=providers)
    assert b7.admit_trusted_context(res) == res.derived_state


def test_t18_rejected_or_unresolved_results_are_not_admitted(b7, coref_entry, raw_candidate_factory, providers):
    (req,) = b7.detect_unresolved(coref_entry)
    rejected = b7.validate_candidate(req, b7.translate(raw_candidate_factory(req, remaining_unknowns=[]), req),
                                     origin=coref_entry, provider_roles=providers)
    with pytest.raises(ValueError):
        b7.admit_trusted_context(rejected)
