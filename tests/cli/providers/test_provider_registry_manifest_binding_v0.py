from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_registry_manifest_binding_v0 as B


def test_registry_manifest_binding_valid():

    surface = B.build_provider_capability_surface()

    assert B.verify_registry_manifest_binding(
        surface
    ) == (True, None)


def test_brody_surface():

    caps = B.get_provider_capabilities(
        "brody"
    )

    assert "ENGINEERING_REASONING" in caps
    assert "LANGUAGE_REASONING" in caps


def test_unknown_provider_has_no_surface():

    caps = B.get_provider_capabilities(
        "unknown"
    )

    assert caps == []


def test_manifest_provider_must_exist_in_registry():

    surface = B.build_provider_capability_surface()

    surface["capabilities"]["FAKE"] = [
        "ghost_provider"
    ]

    ok, why = B.verify_registry_manifest_binding(
        surface
    )

    assert ok is False
    assert why == "PROVIDER_NOT_IN_REGISTRY"
