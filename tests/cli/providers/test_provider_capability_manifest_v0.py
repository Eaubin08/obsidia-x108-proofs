from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from providers import provider_capability_manifest_v0 as M


def test_manifest_load():
    manifest = M.load_manifest()

    ok, why = M.verify_manifest(manifest)

    assert ok is True
    assert why is None


def test_engineering_capability_exists():
    out = M.resolve_capability(
        "ENGINEERING_REASONING"
    )

    assert out["status"] == "MANIFEST_READY"
    assert "brody" in out["providers"]


def test_unknown_capability_rejected():
    out = M.resolve_capability(
        "UNKNOWN_CAPABILITY"
    )

    assert out["status"] == "MANIFEST_REJECTED"


def test_manifest_is_declarative_only():
    manifest = M.load_manifest()

    assert "authority" not in manifest
    assert "execution" not in manifest
    assert "memory_write" not in manifest
