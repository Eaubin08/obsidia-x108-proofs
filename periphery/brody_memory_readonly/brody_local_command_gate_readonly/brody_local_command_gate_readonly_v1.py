from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any
import re


@dataclass(frozen=True)
class BrodyLocalCommandGateRequest:
    command: str
    claimed_purpose: str = ""
    target_repo: str = "obsidia-x108-proofs"
    human_operator_present: bool = False


@dataclass(frozen=True)
class BrodyLocalCommandGateResponse:
    status: str
    classification: str
    reason: str
    command_echo: str
    target_repo: str
    brody_execute_allowed: bool
    executed: bool
    requires_human_operator: bool
    readonly_analysis_only: bool
    network_executed: bool
    filesystem_mutation_executed: bool
    git_mutation_executed: bool
    secrets_printed: bool
    graphiti_write: bool
    memory_intake: bool
    memory_decision: bool
    allowed_to_decide: bool
    emits_act: bool
    emits_verdict: bool
    decision_authority: str
    kernel_mutation: bool
    x108_runtime_binding: bool
    x108_merge: bool
    created_at: str


class BrodyLocalCommandGateReadonlyV1:
    """
    Readonly command gate for Brody / LLM Obsidien.

    It classifies local terminal commands.
    It never executes them.
    It never authorizes Brody to decide, ACT, mutate X108, write Graphiti,
    ingest memory, call network, or print secrets.
    """

    decision_authority = "KX108_ONLY"

    destructive_patterns = [
        r"\brm\s+-rf\b",
        r"\bRemove-Item\b.*\b-Recurse\b.*\b-Force\b",
        r"\bdel\b.*\/s",
        r"\bformat\b",
        r"\bmkfs\b",
        r"\bdrop\s+database\b",
    ]

    external_patterns = [
        r"\bInvoke-WebRequest\b",
        r"\bInvoke-RestMethod\b",
        r"\bcurl\b",
        r"\bwget\b",
        r"\bgit\s+clone\b",
        r"\bgit\s+fetch\b",
        r"\bgit\s+pull\b",
    ]

    git_mutation_patterns = [
        r"\bgit\s+add\b",
        r"\bgit\s+commit\b",
        r"\bgit\s+push\b",
        r"\bgit\s+reset\b",
        r"\bgit\s+rebase\b",
        r"\bgit\s+merge\b",
        r"\bgit\s+tag\b",
    ]

    fs_mutation_patterns = [
        r"\bSet-Content\b",
        r"\bAdd-Content\b",
        r"\bNew-Item\b",
        r"\bCopy-Item\b",
        r"\bMove-Item\b",
        r"\bRemove-Item\b",
        r">\s*",
        r">>\s*",
    ]

    readonly_patterns = [
        r"\bgit\b.*\bstatus\b",
        r"\bgit\b.*\bdiff\b",
        r"\bgit\b.*\blog\b",
        r"\bgit\b.*\brev-parse\b",
        r"\bGet-Content\b",
        r"\bTest-Path\b",
        r"\bGet-ChildItem\b",
        r"\bSelect-String\b",
    ]

    local_validation_patterns = [
        r"\bverify_all\.py\b",
        r"\bpy_compile\b",
        r"\bpytest\b",
        r"\bsmoke_.*\.py\b",
        r"\brun_.*\.ps1\b",
    ]

    secret_patterns = [
        r"API_KEY",
        r"SECRET",
        r"TOKEN",
        r"PASSWORD",
        r"\.env",
    ]

    decision_pressure_patterns = [
        r"\bALLOW\b",
        r"\bHOLD\b",
        r"\bBLOCK\b",
        r"\bACT\b",
        r"\bverdict\b",
        r"\bdécision\b",
        r"\bdecision\b",
        r"\btrigger\s+X108\b",
        r"\bdéclenche\b",
    ]

    def evaluate(self, request: BrodyLocalCommandGateRequest) -> BrodyLocalCommandGateResponse:
        command = request.command or ""

        classification = "UNKNOWN_COMMAND_REVIEW_REQUIRED"
        reason = "COMMAND_NOT_RECOGNIZED_BY_READONLY_GATE"

        if self._matches(command, self.destructive_patterns):
            classification = "DESTRUCTIVE_COMMAND_BLOCKED"
            reason = "DESTRUCTIVE_PATTERN_DETECTED"
        elif self._matches(command, self.external_patterns):
            classification = "EXTERNAL_ACCESS_COMMAND_REVIEW_REQUIRED"
            reason = "NETWORK_OR_REMOTE_ACCESS_PATTERN_DETECTED"
        elif self._matches(command, self.git_mutation_patterns):
            classification = "GIT_MUTATION_COMMAND_HUMAN_ONLY"
            reason = "GIT_MUTATION_PATTERN_DETECTED"
        elif self._matches(command, self.fs_mutation_patterns):
            classification = "FILESYSTEM_MUTATION_COMMAND_HUMAN_ONLY"
            reason = "FILESYSTEM_MUTATION_PATTERN_DETECTED"
        elif self._matches(command, self.decision_pressure_patterns):
            classification = "DECISION_OR_ACT_PRESSURE_BLOCKED"
            reason = "DECISION_OR_ACT_PATTERN_DETECTED"
        elif self._matches(command, self.local_validation_patterns):
            classification = "LOCAL_VALIDATION_COMMAND_HUMAN_ONLY"
            reason = "LOCAL_VALIDATION_PATTERN_DETECTED"
        elif self._matches(command, self.readonly_patterns):
            classification = "READONLY_INSPECTION_COMMAND_HUMAN_ONLY"
            reason = "READONLY_INSPECTION_PATTERN_DETECTED"

        if self._matches(command, self.secret_patterns):
            classification = "SECRET_SURFACE_REVIEW_REQUIRED"
            reason = "SECRET_OR_ENV_PATTERN_DETECTED"

        return BrodyLocalCommandGateResponse(
            status="BRODY_LOCAL_COMMAND_GATE_READONLY_V1_CLASSIFIED",
            classification=classification,
            reason=reason,
            command_echo=command,
            target_repo=request.target_repo,
            brody_execute_allowed=False,
            executed=False,
            requires_human_operator=True,
            readonly_analysis_only=True,
            network_executed=False,
            filesystem_mutation_executed=False,
            git_mutation_executed=False,
            secrets_printed=False,
            graphiti_write=False,
            memory_intake=False,
            memory_decision=False,
            allowed_to_decide=False,
            emits_act=False,
            emits_verdict=False,
            decision_authority=self.decision_authority,
            kernel_mutation=False,
            x108_runtime_binding=False,
            x108_merge=False,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def _matches(self, command: str, patterns: list[str]) -> bool:
        return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern in patterns)


def evaluate_command(payload: Dict[str, Any]) -> Dict[str, Any]:
    req = BrodyLocalCommandGateRequest(
        command=str(payload.get("command", "")),
        claimed_purpose=str(payload.get("claimed_purpose", "")),
        target_repo=str(payload.get("target_repo", "obsidia-x108-proofs")),
        human_operator_present=bool(payload.get("human_operator_present", False)),
    )
    return asdict(BrodyLocalCommandGateReadonlyV1().evaluate(req))


if __name__ == "__main__":
    import json
    sample = {
        "command": "git -C obsidia-x108-proofs status --short",
        "claimed_purpose": "inspect repo state",
    }
    print(json.dumps(evaluate_command(sample), indent=2, ensure_ascii=False))
