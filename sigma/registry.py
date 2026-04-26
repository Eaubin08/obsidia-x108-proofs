from .domains.bank_agents import build_bank_agents
try:
    from .domains.aviation_agents import build_aviation_agents
except ImportError:
    def build_aviation_agents(): return []

def build_agent_registry():
    return {
        "bank": build_bank_agents(),
        "gps_defense_aviation": build_aviation_agents(), # On a changé "aviation" par le nom complet
        "trading": [],
        "ecom": []
    }

REGISTRY = build_agent_registry()
