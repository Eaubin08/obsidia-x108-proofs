from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

OJ_SOURCE = Path(
    os.environ.get("OBSIDIA_OPENJARVIS_SOURCE", "")
).resolve(strict=False)

OJ_EXPECTED = os.environ.get(
    "OBSIDIA_OPENJARVIS_COMMIT",
    "",
).strip().lower()

HUMAN_TOKEN = (
    "HUMAN_APPROVED_"
    + "BUILD_SESSION="
)


def _git(repo: Path, *args: str):
    proc = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        timeout=30,
    )
    return proc.returncode, proc.stdout or ""


def _die(message: str):
    sys.stderr.write(message + "\n")
    raise SystemExit(2)


if not OJ_SOURCE.is_dir():
    _die("OPENJARVIS_SOURCE_REQUIRED")

rc, actual = _git(
    OJ_SOURCE,
    "rev-parse",
    "HEAD",
)

if (
    rc != 0
    or actual.strip().lower()
    != OJ_EXPECTED
):
    _die(
        "OPENJARVIS_SOURCE_IDENTITY_MISMATCH"
    )

rc, dirty = _git(
    OJ_SOURCE,
    "status",
    "--porcelain=v1",
)

if rc != 0 or dirty.strip():
    _die(
        "OPENJARVIS_SOURCE_NOT_CLEAN"
    )


sys.path.insert(
    0,
    str(OJ_SOURCE / "src"),
)

# Repo root is required for canonical package imports such as:
#     scripts.providers.obsidia_native_tooling_session_v1
#
# The direct scripts path remains present for legacy top-level imports
# such as obsidia_relay_v0.
sys.path.insert(
    0,
    str(ROOT),
)

sys.path.insert(
    0,
    str(SCRIPTS),
)


from openjarvis.core.types import ToolResult
from openjarvis.mcp.protocol import (
    MCPRequest,
    MCPResponse,
    PARSE_ERROR,
)
from openjarvis.mcp.server import MCPServer
from openjarvis.tools._stubs import (
    BaseTool,
    ToolSpec,
)

import obsidia_relay_v0 as RELAY


def _bound_repo():
    raw = os.environ.get(
        "OBSIDIA_CLI_REPO_ROOT",
        "",
    ).strip()

    expected = os.environ.get(
        "OBSIDIA_CLI_EXPECTED_HEAD",
        "",
    ).strip().lower()

    if not raw or not expected:
        raise RuntimeError(
            "OBSIDIA_CLI_REPO_BINDING_REQUIRED"
        )

    repo = Path(
        raw
    ).resolve(strict=False)

    if not repo.is_dir():
        raise RuntimeError(
            "OBSIDIA_CLI_REPO_NOT_FOUND"
        )

    rc, head = _git(
        repo,
        "rev-parse",
        "HEAD",
    )

    if (
        rc != 0
        or head.strip().lower()
        != expected
    ):
        raise RuntimeError(
            "OBSIDIA_CLI_REPO_HEAD_MISMATCH"
        )

    rc, status = _git(
        repo,
        "status",
        "--porcelain=v1",
    )

    if rc != 0 or status.strip():
        raise RuntimeError(
            "OBSIDIA_CLI_REPO_MUST_BE_CLEAN"
        )

    return repo, expected


def _bound_target(
    value: str,
    repo: Path,
):
    raw = str(
        value or ""
    ).strip().replace("\\", "/")

    if not raw:
        raise RuntimeError(
            "TARGET_REQUIRED"
        )

    path = PurePosixPath(raw)

    if (
        path.is_absolute()
        or ".." in path.parts
    ):
        raise RuntimeError(
            "TARGET_SCOPE_INVALID"
        )

    canonical = path.as_posix()

    rc, _ = _git(
        repo,
        "ls-files",
        "--error-unmatch",
        "--",
        canonical,
    )

    if rc != 0:
        raise RuntimeError(
            "TARGET_MUST_BE_TRACKED"
        )

    return canonical


class ObsidiaSelfBuildPhase1MCPTool(
    BaseTool
):
    tool_id = (
        "obsidia_self_build_phase1"
    )

    @property
    def spec(self):
        return ToolSpec(
            name=self.tool_id,
            description=(
                "Ask canonical Obsidia to "
                "prepare one bounded "
                "Brody-to-Obsidure engineering "
                "candidate. Phase1 only. "
                "No apply, commit, push or merge."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                    },
                    "target_path": {
                        "type": "string",
                    },
                },
                "required": [
                    "objective",
                    "target_path",
                ],
                "additionalProperties": False,
            },
            category="obsidia-governed",
            timeout_seconds=600.0,
            required_capabilities=[],
            metadata={
                "authority": "NONE",
                "decision_authority": (
                    "KX108_ONLY"
                ),
                "phase2": False,
                "repo_root_bound": True,
            },
        )

    def execute(
        self,
        **params,
    ):
        allowed = {
            "objective",
            "target_path",
        }

        if set(params) - allowed:
            return ToolResult(
                tool_name=self.tool_id,
                content=(
                    "PARAMETER_SCOPE_DENIED"
                ),
                success=False,
            )

        objective = str(
            params.get("objective")
            or ""
        ).strip()

        if (
            not objective
            or len(objective) > 20000
            or HUMAN_TOKEN in objective
        ):
            return ToolResult(
                tool_name=self.tool_id,
                content="OBJECTIVE_INVALID",
                success=False,
            )

        try:
            repo, expected = _bound_repo()

            target = _bound_target(
                params.get(
                    "target_path"
                ),
                repo,
            )

        except Exception as exc:
            return ToolResult(
                tool_name=self.tool_id,
                content=str(exc),
                success=False,
            )

        _, before_head = _git(
            repo,
            "rev-parse",
            "HEAD",
        )

        _, before_status = _git(
            repo,
            "status",
            "--porcelain=v1",
        )

        digest = hashlib.sha256(
            (
                expected
                + "\n"
                + target
                + "\n"
                + objective
            ).encode("utf-8")
        ).hexdigest()[:24]

        local = os.environ.get(
            "LOCALAPPDATA",
            "",
        ).strip()

        base = (
            Path(local)
            if local
            else Path.home()
        )

        store = (
            base
            / "Obsidia"
            / "openjarvis_mcp_relay_v0"
            / digest
        )

        nested = RELAY.relay_submit_mission(
            requested_outcome=objective,
            mission_kind=(
                RELAY
                .KIND_OBSIDIA_NATIVE_SELF_BUILD_PHASE1
            ),
            target=target,
            repo_root=repo,
            store_dir=store,
        )

        evidence = dict(
            nested.get(
                "native_evidence"
            )
            or {}
        )

        plan = dict(
            evidence.get(
                "plan_summary"
            )
            or {}
        )

        _, after_head = _git(
            repo,
            "rev-parse",
            "HEAD",
        )

        _, after_status = _git(
            repo,
            "status",
            "--porcelain=v1",
        )

        mutated = (
            before_head != after_head
            or before_status != after_status
        )

        summary = {
            "mission_state": (
                nested.get(
                    "mission_state"
                )
            ),
            "relay_mission_id": (
                nested.get(
                    "relay_mission_id"
                )
            ),
            "phase1_status": (
                evidence.get(
                    "phase1_status"
                )
            ),
            "target_path": target,
            "producer_id": evidence.get(
                "producer_id"
            ),
            "model_id": evidence.get(
                "model_id"
            ),
            "candidate_patch_hash": (
                evidence.get(
                    "candidate_patch_hash"
                )
            ),
            "domain": plan.get(
                "domain"
            ),
            "risk": plan.get(
                "risk"
            ),
            "scope_mode": plan.get(
                "scope_mode"
            ),
            "candidate_files": plan.get(
                "candidate_files"
            ),
            "human_approval_required": True,
            "phase2_executed": False,
            "repo_mutation": mutated,
            "authority": "NONE",
            "decision_authority": (
                evidence.get(
                    "decision_authority"
                )
            ),
        }

        encoded = json.dumps(
            summary,
            sort_keys=True,
        )

        if HUMAN_TOKEN in encoded:
            return ToolResult(
                tool_name=self.tool_id,
                content=(
                    "HUMAN_TOKEN_LEAK_BLOCKED"
                ),
                success=False,
            )

        ok = (
            nested.get(
                "mission_state"
            )
            == "MISSION_COMPLETE"
            and evidence.get(
                "ok"
            )
            is True
            and evidence.get(
                "phase2_executed"
            )
            is False
            and evidence.get(
                "repo_mutation"
            )
            is False
            and not mutated
        )

        return ToolResult(
            tool_name=self.tool_id,
            content=encoded,
            success=ok,
            metadata={
                "authority": "NONE",
                "phase2": False,
            },
        )


def serve():
    server = MCPServer(
        tools=[
            ObsidiaSelfBuildPhase1MCPTool()
        ],
        agent_id=(
            "obsidia-mcp-bridge"
        ),
    )

    for raw in sys.stdin:
        raw = raw.strip()

        if not raw:
            continue

        parsed = None

        try:
            parsed = json.loads(raw)

            # Notification:
            # MCP requires no response.
            if "id" not in parsed:
                continue

            request = MCPRequest.from_json(
                raw
            )

            response = server.handle(
                request
            )

        except Exception as exc:
            request_id = 0

            if isinstance(
                parsed,
                dict,
            ):
                request_id = parsed.get(
                    "id",
                    0,
                )

            response = (
                MCPResponse.error_response(
                    request_id,
                    PARSE_ERROR,
                    type(exc).__name__,
                )
            )

        sys.stdout.write(
            response.to_json()
            + "\n"
        )

        sys.stdout.flush()


if __name__ == "__main__":
    serve()
