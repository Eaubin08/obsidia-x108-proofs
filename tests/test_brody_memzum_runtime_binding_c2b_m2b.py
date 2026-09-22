"""
C2B-M2B ? MEMZUM runtime binding contract.

The Brody runtime must consume MEMZUM.memory_required instead of reading
point_cloud.memory_packet_required directly.

Graphiti remains temporarily present only as a provider/gate concern.
"""

from pathlib import Path


ROUTE = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "obsidia_api"
    / "routes"
    / "brody.py"
)


def _source() -> str:
    return ROUTE.read_text(encoding="utf-8")


def test_brody_route_imports_memzum_runtime():
    src = _source()

    assert "brody_memzum_activation_adapter" in src
    assert "evaluate_memzum_activation" in src


def test_brody_route_no_longer_consumes_raw_memory_packet_required():
    src = _source()

    assert (
        '_fp_has_mem = bool(_fp_pc.get("memory_packet_required", False))'
        not in src
    )

    assert (
        '_has_explicit_mem = bool(_pc.get("memory_packet_required", False))'
        not in src
    )


def test_context_budget_memory_signal_comes_from_memzum():
    src = _source()

    assert (
        '_fp_has_mem = bool(_fp_memzum.get("memory_required", False))'
        in src
    )

    assert (
        '_has_explicit_mem = bool(_memzum.get("memory_required", False))'
        in src
    )


def test_memzum_is_exposed_in_v3_packets():
    src = _source()

    assert '"memzum": _fp_memzum' in src
    assert src.count('"memzum": _memzum') == 2


def test_graphiti_remains_separate_temporarily():
    src = _source()
    # The old M2B temporary Graphiti admission boundary was retired by M4.
    assert "evaluate_graphiti_guard" not in src
    assert "graphiti_guard" not in src
    assert "build_native_memory_response" in src
    assert "KX108_ONLY" in src
