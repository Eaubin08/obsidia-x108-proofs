import pytest
from periphery.gencoin_distribution import compute_distribution, DistributionCandidate


def test_human_share_largest():
    dist = compute_distribution("act_001", 100.0)
    assert dist.human_share >= dist.agent_share
    assert dist.human_share >= dist.audit_share
    assert dist.human_share >= dist.maintenance_share


def test_agent_share_capped():
    dist = compute_distribution("act_001", 1000.0)
    assert dist.agent_share <= 100.0


def test_zero_gencoin_zero_all():
    dist = compute_distribution("act_zero", 0.0)
    assert dist.human_share == 0.0
    assert dist.agent_share == 0.0
    assert dist.mint_allowed is False


def test_no_mint_allowed():
    dist = compute_distribution("act_001", 100.0)
    assert dist.mint_allowed is False


def test_human_priority_assertion():
    dist = DistributionCandidate(
        action_id="x",
        gencoin_candidate=100.0,
        human_share=5.0,
        audit_share=10.0,
        maintenance_share=10.0,
        agent_share=50.0,
        reserve_share=5.0,
        burn_or_zero_share=2.0,
    )
    with pytest.raises(AssertionError, match="DISTRIBUTION_HUMAN_NOT_PRIORITY"):
        dist.assert_human_priority()
