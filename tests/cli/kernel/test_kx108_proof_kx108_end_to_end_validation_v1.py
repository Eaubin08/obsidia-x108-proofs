from scripts.kernel.kx108_proof_kx108_end_to_end_validation_v1 import (
    KX108ProofEndToEndValidation,
)
from scripts.kernel.kx108_runtime_link_facts_v1 import (
    MISSING_RUNTIME_LINK_ADAPTER,
    MISSING_RUNTIME_LINK_REAL_EXECUTION,
    canonical_agent_context_adapter_present,
)


def safe(status_key, status):
    return {
        status_key: status,
        "decision_authority": "KX108_ONLY",
        "execution_authority": False,
        "memory_write": False,
        "kernel_mutation": False,
        "emits_act": False,
    }


def surfaces():
    global_runtime = safe(
        "kx108_global_runtime_status",
        "PROOF_RUNTIME_SURFACES_VALIDATED",
    )

    global_runtime.update({
        "proof_runtime_surfaces_validated": True,
        "runtime_globally_validated": False,
        "runtime_end_to_end_validated": False,
        "production_ready": False,
        "release_ready": False,
        "deployment_ready": False,
        "final_freeze": False,
    })

    decision_flow = safe(
        "agent_decision_flow_status",
        "BOUNDARY_VALIDATED",
    )

    decision_flow.update({
        "agent_decision_created": False,
        "x108_submitted_here": False,
        "requires_canonical_context_adapter": True,
        # Must mirror the real repository state, not a hardcoded claim.
        "canonical_agent_context_adapter_present":
            canonical_agent_context_adapter_present(),
    })

    envelope = safe(
        "agent_canonical_envelope_status",
        "VALIDATED",
    )

    envelope.update({
        "agent_envelope_created_here": False,
    })

    receipt = safe(
        "agent_receipt_closure_status",
        "VALIDATED",
    )

    receipt.update({
        "agent_receipt_generated_here": False,
    })

    return (
        global_runtime,
        decision_flow,
        envelope,
        receipt,
    )


def test_proof_end_to_end_validated():
    result = (
        KX108ProofEndToEndValidation()
        .validate(
            *surfaces()
        )
    )

    assert (
        result[
            "kx108_end_to_end_validation_status"
        ]
        == "PROOF_E2E_VALIDATED"
    )

    assert result["proof_end_to_end_validated"] is True


def test_runtime_end_to_end_remains_false():
    result = (
        KX108ProofEndToEndValidation()
        .validate(
            *surfaces()
        )
    )

    assert result["runtime_end_to_end_validated"] is False
    assert result["runtime_globally_validated"] is False

    assert (
        result["missing_runtime_link"]
        == MISSING_RUNTIME_LINK_REAL_EXECUTION
    )

    assert (
        MISSING_RUNTIME_LINK_REAL_EXECUTION
        in result["missing_runtime_links"]
    )


def test_fake_x108_submission_claim_rejected():
    values = list(surfaces())

    values[1][
        "x108_submitted_here"
    ] = True

    result = (
        KX108ProofEndToEndValidation()
        .validate(
            *values
        )
    )

    assert (
        result[
            "kx108_end_to_end_validation_status"
        ]
        == "REJECTED"
    )


def test_false_runtime_global_claim_rejected():
    values = list(surfaces())

    values[0][
        "runtime_globally_validated"
    ] = True

    result = (
        KX108ProofEndToEndValidation()
        .validate(
            *values
        )
    )

    assert (
        result[
            "kx108_end_to_end_validation_status"
        ]
        == "REJECTED"
    )


def test_proof_e2e_is_not_release_or_authority():
    result = (
        KX108ProofEndToEndValidation()
        .validate(
            *surfaces()
        )
    )

    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False
    assert result["new_authority_created"] is False
    assert result["validation_authority"] is False
    assert result["decision_authority"] == "KX108_ONLY"
    assert result["execution_authority"] is False
    assert result["memory_write"] is False
    assert result["kernel_mutation"] is False
    assert result["emits_act"] is False


def test_canonical_adapter_presence_must_match_the_repository_fact():
    """A surface lying about the adapter — either way — is rejected."""
    values = list(surfaces())

    values[1]["canonical_agent_context_adapter_present"] = (
        not canonical_agent_context_adapter_present()
    )

    result = (
        KX108ProofEndToEndValidation()
        .validate(*values)
    )

    assert (
        result["kx108_end_to_end_validation_status"]
        == "REJECTED"
    )
    assert (
        result["checks"]["canonical_adapter_presence_is_factual"]
        is False
    )
    assert result["runtime_end_to_end_validated"] is False


def test_present_adapter_does_not_raise_any_runtime_flag():
    """The canonical adapter exists; nothing about that validates the runtime."""
    result = (
        KX108ProofEndToEndValidation()
        .validate(*surfaces())
    )

    assert result["canonical_agent_context_adapter_present"] is True
    assert MISSING_RUNTIME_LINK_ADAPTER not in result["missing_runtime_links"]

    assert result["runtime_end_to_end_validated"] is False
    assert result["runtime_globally_validated"] is False
    assert result["production_ready"] is False
    assert result["release_ready"] is False
    assert result["deployment_ready"] is False
    assert result["final_freeze"] is False
