from __future__ import annotations

from .domains.bank_agents import build_bank_agents
from .domains.ecom_agents import build_ecom_agents
from .domains.meta_agents import build_meta_agents
from .domains.trading_agents import build_trading_agents


def build_agent_registry() -> dict[str, list]:
    return {
        "trading": build_trading_agents(),
        "bank": build_bank_agents(),
        "ecom": build_ecom_agents(),
        "meta": build_meta_agents(),
    }
