from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from ..constants import DECISION_AUTHORITY, READONLY_FLAGS

REPO_BASELINE: dict[str, Any] = {
    "repository_full_name": "Eaubin08/obsidia-x108-proofs",
    "default_branch": "main",
    "visibility": "public",
    "repo_size_kb_observed": 47680,
    "latest_freeze_search_commit": {
        "sha": "b9c191c889724053e2d34e94474355ad2e949cd0",
        "short_sha": "b9c191c",
        "message": "audit: freeze F23A4 reflex diagnostic packet source audit",
        "created_at": "2026-05-28T08:59:34+02:00",
    },
    "indexed_blob_sha_seen_in_code_search": "75a9a516a9858748a387a95d47d982db852b5a13",
    "branching_policy": {
        "direct_main_patch": False,
        "create_feature_branch": True,
        "preferred_branch_name": "periphery/workflow-governance-readonly-v5",
        "merge_requires_human_review": True,
    },
}

REAL_REPO_PATHS: dict[str, str] = {
    "periphery_root": "periphery/",
    "periphery_common": "periphery/common.py",
    "periphery_core_registry": "periphery/core_registry.py",
    "periphery_public_index": "docs/status/PERIPHERY_PUBLIC_INDEX.md",
    "periphery_non_sovereignty_contract": "docs/architecture/PERIPHERY_NON_SOVEREIGNTY_CONTRACT_V0.md",
    "periphery_ci_doc": "docs/ci/CI_PIPELINE_X108_PERIPHERY_V1.md",
    "periphery_api_route": "apps/obsidia_api/routes/periphery_ops.py",
    "brody_automation_orchestrator": "apps/obsidia_api/brody_automation_orchestrator.py",
    "brody_runtime_context_adapter": "apps/obsidia_api/brody_runtime_context_adapter.py",
    "brody_operator_view_packet": "apps/obsidia_api/brody_operator_view_packet.py",
    "brody_operator_loop_adapter": "apps/obsidia_api/brody_operator_loop_adapter.py",
    "brody_memory_readonly_root": "periphery/brody_memory_readonly/",
    "brody_readonly_runtime_root": "periphery/brody/",
    "graphiti_periphery_root": "periphery/graphiti/",
    "graphiti_docs_root": "docs/graphiti/",
    "graphiti_api_route": "apps/obsidia_api/routes/graphiti.py",
    "workbench_app_root": "apps/obsidia-workbench/",
    "right_panel_component": "apps/obsidia-workbench/src/components/RightPanel.tsx",
    "runtime_docs_root": "docs/runtime/",
    "local_ci_runner": "scripts/run_ci_local.ps1",
}

PROPOSED_INSTALL_PATHS: dict[str, str] = {
    "module_root": "periphery/workflow_governance_readonly/",
    "python_package_root": "periphery/workflow_governance_readonly/obsidia_workflow_governance/",
    "repo_alignment_doc": "docs/runtime/OBSIDIA_WORKFLOW_GOVERNANCE_REPO_AWARE_V5_ALIGNMENT.md",
    "freeze_report_doc": "docs/runtime/OBSIDIA_WORKFLOW_GOVERNANCE_PRIMITIVE_V5_FREEZE_REPORT.md",
    "api_route_patch_plan": "patch_plans/WORKFLOW_GOVERNANCE_API_ROUTE_PATCH_PLAN_V5.md",
    "rightpanel_patch_plan": "patch_plans/WORKFLOW_GOVERNANCE_RIGHTPANEL_PATCH_PLAN_V5.md",
    "registry_patch_plan": "patch_plans/WORKFLOW_GOVERNANCE_REGISTRY_PATCH_PLAN_V5.md",
}

PROTECTED_PATHS: list[str] = [
    "sigma/",
    "proofs/lean/",
    "formal/tla/",
    "merkle_seal.json",
    "periphery/brody_memory_readonly/graphiti_import_apply_guarded_manual_only/",
    "periphery/brody_memory_readonly/graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only/",
    "scripts/brody_memory_intake_gate.py",
]

QUARANTINE_PATTERNS: list[str] = [
    "graphiti_guarded_manual_apply",
    "graphiti_import_apply",
    "graphiti_import_dry_run",
    "neo4j_brody_guide_bridge",
    "brody_memory_intake_gate.py",
    "session.write_transaction",
    "execute_write",
    "MERGE ",
    "CREATE ",
    "SET ",
    "DELETE ",
    "DETACH DELETE",
    "git commit",
    "git push",
    "os.system(",
]

@dataclass(frozen=True)
class RepoAwareInstallPlan:
    repo_root: str
    module_root: str
    proposed_branch: str
    copy_commands: list[str]
    validation_commands: list[str]
    forbidden_direct_targets: list[str]
    boundary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_repo_aware_install_plan(repo_root: str = ".") -> dict[str, Any]:
    root = Path(repo_root)
    module_root = root / PROPOSED_INSTALL_PATHS["module_root"]
    copy_commands = [
        "Copy-Item -Recurse -Force .\\src\\obsidia_workflow_governance .\\periphery\\workflow_governance_readonly\\obsidia_workflow_governance",
        "Copy-Item -Recurse -Force .\\contracts .\\periphery\\workflow_governance_readonly\\contracts",
        "Copy-Item -Recurse -Force .\\schemas .\\periphery\\workflow_governance_readonly\\schemas",
        "Copy-Item -Recurse -Force .\\tests .\\periphery\\workflow_governance_readonly\\tests",
        "Copy-Item -Recurse -Force .\\scripts .\\periphery\\workflow_governance_readonly\\scripts",
        "Copy-Item -Recurse -Force .\\docs .\\periphery\\workflow_governance_readonly\\docs",
    ]
    validation_commands = [
        "python -m compileall periphery/workflow_governance_readonly -q",
        "$env:PYTHONPATH=\"$PWD\\periphery\\workflow_governance_readonly\"; python periphery/workflow_governance_readonly/scripts/audit_v5_repo_alignment.py",
        "$env:PYTHONPATH=\"$PWD\\periphery\\workflow_governance_readonly\"; python periphery/workflow_governance_readonly/scripts/smoke_workflow_governance_v5.py",
        "$env:PYTHONPATH=\"$PWD\\periphery\\workflow_governance_readonly\"; python -m pytest periphery/workflow_governance_readonly/tests -q",
        "python scripts/check_forbidden_content.py",
        "python scripts/run_ci_local.ps1  # if executed from PowerShell, use .\\scripts\\run_ci_local.ps1 instead",
    ]
    return RepoAwareInstallPlan(
        repo_root=str(root),
        module_root=str(module_root),
        proposed_branch=REPO_BASELINE["branching_policy"]["preferred_branch_name"],
        copy_commands=copy_commands,
        validation_commands=validation_commands,
        forbidden_direct_targets=PROTECTED_PATHS,
        boundary={"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    ).to_dict()


def build_repo_alignment_matrix() -> dict[str, Any]:
    return {
        "matrix_id": "OBSIDIA_WORKFLOW_GOVERNANCE_REPO_ALIGNMENT_MATRIX_V5",
        "repo_baseline": REPO_BASELINE,
        "real_repo_paths": REAL_REPO_PATHS,
        "proposed_install_paths": PROPOSED_INSTALL_PATHS,
        "protected_paths": PROTECTED_PATHS,
        "quarantine_patterns": QUARANTINE_PATTERNS,
        "decision_authority": DECISION_AUTHORITY,
        "boundary": {"decision_authority": DECISION_AUTHORITY, **READONLY_FLAGS},
    }
