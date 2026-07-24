"""agents.obsidia_sigma_v130 — compatibility shim for sigma.obsidia_sigma_v130.

Re-exports ObsidiaSigmaMonitor so that `from agents.obsidia_sigma_v130 import
ObsidiaSigmaMonitor` continues to work without duplicating sigma code.

No IO. No network. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor  # noqa: F401
