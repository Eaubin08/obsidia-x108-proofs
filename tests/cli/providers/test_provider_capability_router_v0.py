from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_capability_router_v0 as R


def test_engineering_routes():
    x = R.route_capability(
        requested_capability="ENGINEERING_REASONING",
        allowed_providers=["brody", "claude"],
    )

    assert x["status"] == "ROUTING_READY"
    assert x["compatible_providers"] == ["brody"]


def test_formal_only_obsidure():
    x = R.route_capability(
        requested_capability="FORMAL_VERIFICATION",
        allowed_providers=["brody", "obsidure"],
    )

    assert x["compatible_providers"] == ["obsidure"]


def test_unknown_capability_rejected():
    x = R.route_capability(
        requested_capability="UNKNOWN",
        allowed_providers=["brody"],
    )

    assert x["status"] == "ROUTING_REJECTED"


def test_route_validation():
    x = R.route_capability(
        requested_capability="LANGUAGE_REASONING",
        allowed_providers=["claude"],
    )

    assert R.verify_routing(x) == (True, None)
