from scripts.kernel.kx108_adaptive_context_boundary_v1 import (
    KX108AdaptiveContextBoundary,
)


def test_context_acceptance():

    result = (
        KX108AdaptiveContextBoundary()
        .accept_context(
            {
                "domain": "test",
            }
        )
    )

    assert (
        result["context_status"]
        == "ACCEPTED"
    )


def test_calibration_allowed():

    result = (
        KX108AdaptiveContextBoundary()
        .accept_context(
            {
                "domain": "test",
            }
        )
    )

    assert (
        result["calibration_allowed"]
        is True
    )


def test_calibration_targets_periphery():

    result = (
        KX108AdaptiveContextBoundary()
        .calibrate(
            {
                "parameter": "context",
            }
        )
    )

    assert (
        result["target"]
        == "PERIPHERY"
    )


def test_no_kernel_mutation():

    result = (
        KX108AdaptiveContextBoundary()
        .calibrate(
            {}
        )
    )

    assert (
        result["kernel_mutation"]
        is False
    )


def test_kernel_integrity():

    status = (
        KX108AdaptiveContextBoundary()
        .status()
    )

    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
