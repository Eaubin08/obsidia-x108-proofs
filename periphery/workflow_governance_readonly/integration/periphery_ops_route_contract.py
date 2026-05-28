from __future__ import annotations

from typing import Any

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS
from ..repo_aware.obsidia_x108_repo_map import REAL_REPO_PATHS, PROPOSED_INSTALL_PATHS


def build_periphery_ops_route_contract() -> dict[str, Any]:
    """Describe the future FastAPI route without modifying apps/obsidia_api/routes/periphery_ops.py."""
    return {
        "contract_id": "WORKFLOW_GOVERNANCE_PERIPHERY_OPS_ROUTE_CONTRACT_V5",
        "target_file": REAL_REPO_PATHS["periphery_api_route"],
        "proposed_import": "from periphery.workflow_governance_readonly.obsidia_workflow_governance.integration.brody_workflow_governance_snapshot_adapter import build_brody_workflow_governance_snapshot",
        "proposed_route": {
            "method": "POST",
            "path": "/api/periphery/workflow-governance/packet",
            "mode": "READONLY_PACKET_BUILD",
            "body_fields": ["sop_text", "title", "session_id", "request_type"],
        },
        "must_return_boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
        "must_not": [
            "call X108 runtime",
            "write Graphiti",
            "write Neo4j",
            "modify kernel",
            "emit ACT/ALLOW/BLOCK decision",
            "auto execute workflow",
        ],
        "install_root": PROPOSED_INSTALL_PATHS["module_root"],
    }
