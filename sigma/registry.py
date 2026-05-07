from .domains.bank_agents import build_bank_agents
from .domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents


def build_agent_registry():
    return {
        "bank": build_bank_agents(),
        "gps_defense_aviation": build_gps_defense_aviation_agents(),
        "trading": [],
        "ecom": [],
    }


REGISTRY = build_agent_registry()
