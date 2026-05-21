import pytest
from periphery.memory.memory_source_registry import register_source, get_source, list_sources, MemorySourceEntry
from periphery.memory.memory_source_types import MemorySourceType


def test_default_sources_exist():
    sources = list_sources()
    assert len(sources) >= 4


def test_get_brody_runtime_source():
    src = get_source("brody_runtime")
    assert src is not None
    assert src.write_allowed is False


def test_all_default_sources_readonly():
    for src in list_sources():
        assert src.write_allowed is False


def test_register_write_allowed_raises():
    bad = MemorySourceEntry("bad_src", MemorySourceType.UNKNOWN, write_allowed=True)
    with pytest.raises(ValueError, match="WRITE_FORBIDDEN"):
        register_source(bad)


def test_register_readonly_source_ok():
    entry = MemorySourceEntry("test_op", MemorySourceType.OPERATOR_SESSION,
                              readonly=True, write_allowed=False)
    register_source(entry)
    src = get_source("test_op")
    assert src.write_allowed is False
