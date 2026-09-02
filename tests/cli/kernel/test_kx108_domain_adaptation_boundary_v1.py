from scripts.kernel.kx108_domain_adaptation_boundary_v1 import (
    KX108DomainAdaptationBoundary,
)


def domain_state():

    return {
        "domain": "GPS",
        "confidence": 0.95,
    }


def test_domain_acceptance():

    result = (
        KX108DomainAdaptationBoundary()
        .accept_domain_state(
            domain_state()
        )
    )

    assert (
        result["domain_status"]
        == "ACCEPTED"
    )


def test_evaluation_allowed():

    result = (
        KX108DomainAdaptationBoundary()
        .accept_domain_state(
            domain_state()
        )
    )

    assert (
        result["evaluation_allowed"]
        is True
    )


def test_domain_translation():

    result = (
        KX108DomainAdaptationBoundary()
        .translate_domain(
            domain_state()
        )
    )

    assert (
        result["translation_status"]
        == "COMPLETED"
    )


def test_kernel_protection():

    result = (
        KX108DomainAdaptationBoundary()
        .translate_domain(
            domain_state()
        )
    )

    assert (
        result["kernel_mutation"]
        is False
    )


def test_final_integrity():

    status = (
        KX108DomainAdaptationBoundary()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
