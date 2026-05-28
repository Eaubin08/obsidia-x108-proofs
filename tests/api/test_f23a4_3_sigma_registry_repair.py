from sigma.registry import build_agent_registry


def test_f23a4_3_sigma_registry_has_trading_ecom_meta():
    registry = build_agent_registry()

    assert "trading" in registry
    assert "ecom" in registry
    assert "meta" in registry

    assert len(registry["trading"]) > 0
    assert len(registry["ecom"]) > 0
    assert len(registry["meta"]) > 0


def test_f23a4_3_sigma_registry_expected_domain_counts():
    registry = build_agent_registry()

    assert len(registry["trading"]) == 17
    assert len(registry["ecom"]) == 12
    assert len(registry["meta"]) >= 10


def test_f23a4_3_sigma_registry_no_empty_critical_domains():
    registry = build_agent_registry()

    for domain in ("bank", "gps_defense_aviation", "trading", "ecom", "meta"):
        assert domain in registry
        assert registry[domain], f"{domain} registry must not be empty"
