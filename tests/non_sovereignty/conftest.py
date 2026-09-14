"""
Fixture: redirect world_action_bus writes to a temporary file for all
tests in tests/non_sovereignty/ so no versioned file is modified.

The bus behaviour (append-only, dry_run_only, blocked=True) is preserved.
Only the output destination is isolated.
"""
import pytest
import periphery.world_calls.world_action_bus as _bus


@pytest.fixture(autouse=True)
def isolate_world_action_bus(tmp_path, monkeypatch):
    """Redirect _DEFAULT_BUS_PATH to a temp file for the duration of each test."""
    temp_bus = tmp_path / "world_action_bus_isolated.jsonl"
    monkeypatch.setattr(_bus, "_DEFAULT_BUS_PATH", str(temp_bus))
    yield
    # tmp_path is cleaned up by pytest automatically
