from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_activation_gate_v0 as G


def test_disabled_provider_rejected():

    out = G.evaluate_provider_activation(
        "brody",
        "ENGINEERING_REASONING",
    )

    assert out["status"] == "ACTIVATION_REJECTED"
    assert out["reason"] == "PROVIDER_DISABLED"


def test_unknown_capability_rejected():

    out = G.evaluate_provider_activation(
        "brody",
        "UNKNOWN",
    )

    assert out["status"] == "ACTIVATION_REJECTED"


def test_activation_has_no_authority():

    activation = {
        "status": "ACTIVATION_READY",
        "invocable": True,
        "execution_authority": False,
        "kx_authority": False,
    }

    assert G.verify_activation(
        activation
    ) == (True, None)


def test_fake_authority_rejected():

    activation = {
        "status": "ACTIVATION_READY",
        "invocable": True,
        "execution_authority": True,
        "kx_authority": False,
    }

    ok, why = G.verify_activation(
        activation
    )

    assert ok is False
    assert why == "EXECUTION_AUTHORITY_FORBIDDEN"
