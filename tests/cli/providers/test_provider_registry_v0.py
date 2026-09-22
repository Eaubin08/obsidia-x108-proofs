from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_registry_v0 as R


def test_registry_load():

    registry = R.load_registry()

    assert R.verify_registry(
        registry
    ) == (True, None)


def test_brody_declared():

    out = R.resolve_provider(
        "brody"
    )

    assert out["status"] == "REGISTRY_READY"
    assert out["adapter_id"] == "BRODY_ADAPTER_V0"


def test_unknown_provider():

    out = R.resolve_provider(
        "unknown"
    )

    assert out["status"] == "REGISTRY_REJECTED"


def test_provider_disabled_by_default():

    out = R.resolve_provider(
        "claude"
    )

    assert out["enabled"] is False
    assert out["status"] == "REGISTRY_READY"
