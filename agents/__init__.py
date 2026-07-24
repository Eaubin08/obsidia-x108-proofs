"""agents — compatibility namespace re-exporting sigma.contracts public types.

The canonical runtime package is `sigma`. This shim allows test files that were
written with `from agents import TradingState` to keep working without touching
the test source or duplicating sigma code.

No IO. No network. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
from sigma.contracts import BankState, EcomState, TradingState  # noqa: F401
