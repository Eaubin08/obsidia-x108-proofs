from scripts.kernel.kx108_proof_security_boundary_v1 import (
    KX108ProofSecurityBoundary,
)


def test_api_key_is_redacted():

    raw = "API_KEY=abc123SECRET"

    result = KX108ProofSecurityBoundary().sanitize(
        raw
    )

    assert result["security_boundary_status"] == "SANITIZED"
    assert result["secret_detected"] is True
    assert "abc123SECRET" not in result["sanitized"]
    assert "[REDACTED_SECRET]" in result["sanitized"]


def test_nested_secret_is_redacted():

    payload = {
        "context": {
            "credential":
                "PASSWORD=supersecret"
        }
    }

    result = KX108ProofSecurityBoundary().sanitize(
        payload
    )

    assert result["security_boundary_status"] == "SANITIZED"

    assert (
        "supersecret"
        not in result[
            "sanitized"
        ]["context"]["credential"]
    )


def test_clean_payload_is_preserved():

    payload = {
        "query": "readonly context",
        "risk": False,
    }

    result = KX108ProofSecurityBoundary().sanitize(
        payload
    )

    assert result["security_boundary_status"] == "CLEAN"
    assert result["secret_detected"] is False
    assert result["sanitized"] == payload


def test_private_key_surface_is_sanitized():

    raw = (
        "secret material "
        "-----BEGIN PRIVATE KEY----- test"
    )

    result = KX108ProofSecurityBoundary().sanitize(
        raw
    )

    assert result["security_boundary_status"] == "SANITIZED"
    assert result["redaction_present"] is True


def test_security_boundary_has_no_authority():

    status = KX108ProofSecurityBoundary().status()

    assert status["decision_authority"] == "KX108_ONLY"
    assert status["execution_authority"] is False
    assert status["memory_write"] is False
    assert status["kernel_mutation"] is False
    assert status["emits_act"] is False
