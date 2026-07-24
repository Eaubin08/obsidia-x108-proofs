"""agents.run_pipeline — compatibility shim for sigma.run_pipeline / sigma.protocols.

Re-exports the public pipeline functions so that imports of the form
`from agents.run_pipeline import run_trading_pipeline` continue to work.

run_trading_pipeline and friends live in sigma.protocols; sigma.run_pipeline
imports them and exposes the CLI entry-point.

No IO. No network. No ACT. DECISION_AUTHORITY=KX108_ONLY.
"""
import sys
from pathlib import Path

# Support direct execution: `python agents/run_pipeline.py`.
# In that mode, Python exposes agents/ but not the repository root,
# so the canonical sibling package sigma/ must be made importable.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)

from sigma.protocols import (  # noqa: F401
    run_bank_pipeline,
    run_ecom_pipeline,
    run_gps_defense_aviation_pipeline,
    run_trading_pipeline,
)

if __name__ == "__main__":
    # Compatibility entry-point: preserve direct execution of
    # `python agents/run_pipeline.py ...` while keeping sigma canonical.
    import runpy

    runpy.run_module("sigma.run_pipeline", run_name="__main__")
