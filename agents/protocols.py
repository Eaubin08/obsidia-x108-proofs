"""agents.protocols — compatibility shim for sigma.protocols.

Re-exports pipeline entry-points from sigma.protocols so that imports of the form
`from agents.protocols import run_trading_pipeline` continue to work.

No IO. No network. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from sigma.protocols import (  # noqa: F401
    build_agent_registry,
    run_bank_pipeline,
    run_ecom_pipeline,
    run_gps_defense_aviation_pipeline,
    run_trading_pipeline,
)
