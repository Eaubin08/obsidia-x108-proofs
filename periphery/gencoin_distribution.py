from __future__ import annotations

from dataclasses import dataclass


_HUMAN_SHARE = 0.50
_AUDIT_SHARE = 0.15
_MAINTENANCE_SHARE = 0.15
_AGENT_SHARE_MAX = 0.10
_RESERVE_SHARE = 0.08
_BURN_SHARE = 0.02


@dataclass
class DistributionCandidate:
    action_id: str
    gencoin_candidate: float
    human_share: float
    audit_share: float
    maintenance_share: float
    agent_share: float
    reserve_share: float
    burn_or_zero_share: float
    mint_allowed: bool = False

    def assert_human_priority(self) -> None:
        if self.gencoin_candidate > 0 and self.human_share < self.agent_share:
            raise AssertionError("DISTRIBUTION_HUMAN_NOT_PRIORITY")

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "gencoin_candidate": self.gencoin_candidate,
            "human_share": self.human_share,
            "audit_share": self.audit_share,
            "maintenance_share": self.maintenance_share,
            "agent_share": self.agent_share,
            "reserve_share": self.reserve_share,
            "burn_or_zero_share": self.burn_or_zero_share,
            "mint_allowed": self.mint_allowed,
        }


def compute_distribution(action_id: str, gencoin_candidate: float) -> DistributionCandidate:
    if gencoin_candidate <= 0.0:
        return DistributionCandidate(
            action_id=action_id,
            gencoin_candidate=0.0,
            human_share=0.0,
            audit_share=0.0,
            maintenance_share=0.0,
            agent_share=0.0,
            reserve_share=0.0,
            burn_or_zero_share=0.0,
            mint_allowed=False,
        )

    agent_share = min(_AGENT_SHARE_MAX, gencoin_candidate * _AGENT_SHARE_MAX)
    human_share = gencoin_candidate * _HUMAN_SHARE
    audit_share = gencoin_candidate * _AUDIT_SHARE
    maintenance_share = gencoin_candidate * _MAINTENANCE_SHARE
    reserve_share = gencoin_candidate * _RESERVE_SHARE
    burn_share = gencoin_candidate * _BURN_SHARE

    dist = DistributionCandidate(
        action_id=action_id,
        gencoin_candidate=gencoin_candidate,
        human_share=human_share,
        audit_share=audit_share,
        maintenance_share=maintenance_share,
        agent_share=agent_share,
        reserve_share=reserve_share,
        burn_or_zero_share=burn_share,
        mint_allowed=False,
    )
    dist.assert_human_priority()
    return dist
