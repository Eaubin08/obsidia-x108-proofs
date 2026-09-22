from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"

for p in (str(_SCRIPTS), str(_REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

import obsidia_cognitive_provider_binder_v0 as B


def test_provider_registry_disabled_by_default():
    assert B.BINDER_ACTIVE is True
    assert B.PROVIDER_CALL_ALLOWED is False

    for name in ("BRODY", "CLAUDE", "OBSIDURE"):
        p = B.get_provider(name)
        assert p is not None
        assert p["enabled"] is False


def test_unknown_provider_rejected():
    ok, why = B.verify_provider_available("UNKNOWN")
    assert ok is False
    assert why == "PROVIDER_UNKNOWN"


def test_disabled_provider_rejected():
    ok, why = B.verify_provider_available("BRODY")
    assert ok is False
    assert why == "PROVIDER_DISABLED"


def test_valid_result_has_no_authority():
    result = B.build_capability_result(
        provider="BRODY",
        result_kind=B.RESULT_PROPOSAL,
        content="proposal",
    )

    assert result["is_execution_authority"] is False
    assert result["is_kx_authority"] is False
    assert result["is_sovereign"] is False

    assert B.verify_capability_result(result) == (True, None)


def test_execution_authority_result_rejected():
    result = B.build_capability_result(
        provider="CLAUDE",
        result_kind=B.RESULT_PROPOSAL,
        content="x",
    )
    result["is_execution_authority"] = True

    ok, why = B.verify_capability_result(result)

    assert ok is False
    assert why == "EXECUTION_AUTHORITY_FORBIDDEN"


def test_kx_authority_result_rejected():
    result = B.build_capability_result(
        provider="OBSIDURE",
        result_kind=B.RESULT_EVIDENCE,
        content="x",
    )
    result["is_kx_authority"] = True

    ok, why = B.verify_capability_result(result)

    assert ok is False
    assert why == "KX_AUTHORITY_FORBIDDEN"


def test_invalid_result_kind_rejected():
    result = B.build_capability_result(
        provider="CLAUDE",
        result_kind="DECISION",
        content="x",
    )

    ok, why = B.verify_capability_result(result)

    assert ok is False
    assert why == "RESULT_KIND_INVALID"
