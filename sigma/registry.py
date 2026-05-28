from .domains.bank_agents import build_bank_agents
from .domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents
from .domains.trading_agents import build_trading_agents
from .domains.ecom_agents import build_ecom_agents
from .domains.meta_agents import build_meta_agents


def build_agent_registry():
    return {
        "bank": build_bank_agents(),
        "gps_defense_aviation": build_gps_defense_aviation_agents(),
        "trading": build_trading_agents(),
        "ecom": build_ecom_agents(),
        "meta": build_meta_agents(),
    }


REGISTRY = build_agent_registry()
