import pytest

from scripts.providers.provider_lifecycle_manager_v0 import (
    ProviderLifecycleManager,
    ProviderLifecycleError,
    ProviderLifecycleState,
)


def build_manager():
    return ProviderLifecycleManager(
        provider_id="brody"
    )


def test_initial_state():
    manager = build_manager()

    assert manager.state == ProviderLifecycleState.INSTALLED
    assert manager.execution_authority is False
    assert manager.decision_authority is False


def test_full_lifecycle():
    manager = build_manager()

    manager.declare()
    assert manager.state == ProviderLifecycleState.DECLARED

    manager.validate()
    assert manager.state == ProviderLifecycleState.VALIDATED

    manager.enable()
    assert manager.state == ProviderLifecycleState.ENABLED

    manager.disable()
    assert manager.state == ProviderLifecycleState.DISABLED

    manager.remove()
    assert manager.state == ProviderLifecycleState.REMOVED


def test_enable_before_validation_blocked():
    manager = build_manager()

    with pytest.raises(ProviderLifecycleError):
        manager.enable()


def test_removed_provider_is_terminal():
    manager = build_manager()

    manager.declare()
    manager.validate()
    manager.enable()
    manager.disable()
    manager.remove()

    with pytest.raises(ProviderLifecycleError):
        manager.enable()


def test_only_enabled_provider_can_invoke():
    manager = build_manager()

    assert manager.can_invoke() is False

    manager.declare()
    manager.validate()
    manager.enable()

    assert manager.can_invoke() is True
