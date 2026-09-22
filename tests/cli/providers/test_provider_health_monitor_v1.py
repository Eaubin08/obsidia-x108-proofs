import pytest

from scripts.providers.provider_health_monitor_v1 import (
    ProviderHealthMonitor,
    ProviderHealthMonitorError,
)


def build_monitor():

    return ProviderHealthMonitor(
        provider_id="brody"
    )


def test_initial_state():

    monitor = build_monitor()

    assert monitor.status == "AVAILABLE"


def test_update_valid_state():

    monitor = build_monitor()

    assert monitor.update_status(
        "DEGRADED"
    ) is True

    assert monitor.status == "DEGRADED"


def test_invalid_state_blocked():

    monitor = build_monitor()

    with pytest.raises(
        ProviderHealthMonitorError
    ):

        monitor.update_status(
            "UNKNOWN"
        )


def test_authority_invariants():

    monitor = build_monitor()

    assert monitor.decision_authority is False
    assert monitor.execution_authority is False
    assert monitor.memory_write is False
    assert monitor.kernel_mutation is False
    assert monitor.emits_act is False


def test_to_dict():

    monitor = build_monitor()

    data = monitor.to_dict()

    assert data["provider_id"] == "brody"
    assert data["status"] == "AVAILABLE"
