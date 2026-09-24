"""
OpenJarvis <-> Obsidia governed HTTP transport.

This route owns NO execution authority.

The workspace is NEVER selected by the browser.

The server must already have a trusted Jarvis workspace binding
created by obsidia_jarvis_workspace_launcher_v0.py.  The route
accepts the resulting OBSIDIA_JARVIS_SESSION_ID and resolves that
binding through GovernedJarvisChatSession.

Authority remains:

    human exact EAH -> J9 -> J7 -> J5 -> KX108

This module never imports or calls Relay, J5, Binder, content apply,
HumanApproval storage or KX108 directly.
"""

from __future__ import annotations

import os
import re
from threading import RLock
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import (
    BaseModel,
    ConfigDict,
)

from scripts.obsidia_jarvis_governed_chat_v0 import (
    GovernedJarvisChatSession,
)


router = APIRouter(
    prefix="/api/jarvis",
    tags=["jarvis-governed"],
)


SCHEMA_VERSION = (
    "OBSIDIA_OPENJARVIS_"
    "GOVERNED_HTTP_V0"
)

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

_SESSION_PATTERN = re.compile(
    r"^jws-[0-9a-f]{20}$"
)

_LOCK = RLock()

_SESSION: GovernedJarvisChatSession | None = None


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


class JarvisTurnRequest(_StrictModel):
    text: str


class JarvisPrepareRequest(_StrictModel):
    candidate_patch_path: str


class JarvisAuthorizeRequest(_StrictModel):
    execution_authority_hash: str


def _required_environment(
    name: str,
) -> str:
    value = str(
        os.environ.get(
            name,
            "",
        )
    ).strip()

    if not value:
        raise HTTPException(
            status_code=503,
            detail={
                "error":
                    "JARVIS_TRUSTED_RUNTIME_ENV_REQUIRED",
                "missing":
                    name,
                "authority":
                    AUTHORITY,
                "decision_authority":
                    DECISION_AUTHORITY,
            },
        )

    return value


def _ensure_session() -> GovernedJarvisChatSession:
    global _SESSION

    with _LOCK:
        if _SESSION is not None:
            return _SESSION

        session_id = _required_environment(
            "OBSIDIA_JARVIS_SESSION_ID"
        )

        if not _SESSION_PATTERN.fullmatch(
            session_id
        ):
            raise HTTPException(
                status_code=503,
                detail={
                    "error":
                        "TRUSTED_JARVIS_SESSION_ID_INVALID",
                    "authority":
                        AUTHORITY,
                    "decision_authority":
                        DECISION_AUTHORITY,
                },
            )

        source = _required_environment(
            "OBSIDIA_OPENJARVIS_SOURCE"
        )

        commit = _required_environment(
            "OBSIDIA_OPENJARVIS_COMMIT"
        )

        state_path = str(
            os.environ.get(
                "OBSIDIA_JARVIS_STATE",
                "",
            )
        ).strip()

        kwargs: dict[str, Any] = {
            "openjarvis_source":
                source,
            "openjarvis_commit":
                commit,
        }

        if state_path:
            kwargs[
                "state_path"
            ] = state_path

        try:
            _SESSION = (
                GovernedJarvisChatSession(
                    session_id,
                    **kwargs,
                )
            )
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail={
                    "error":
                        "TRUSTED_JARVIS_SESSION_INIT_FAILED",
                    "reason":
                        f"{type(exc).__name__}:{exc}",
                    "authority":
                        AUTHORITY,
                    "decision_authority":
                        DECISION_AUTHORITY,
                },
            ) from exc

        return _SESSION


def _full_sha256(
    value: object,
) -> bool:
    return (
        isinstance(
            value,
            str,
        )
        and len(value) == 64
        and all(
            ch in (
                "0123456789"
                "abcdefABCDEF"
            )
            for ch in value
        )
    )


def _pending_snapshot(
    session: GovernedJarvisChatSession,
    fallback: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    current = getattr(
        session,
        "pending_governed_mission",
        None,
    )

    source = (
        current
        if isinstance(
            current,
            dict,
        )
        else fallback
    )

    if not isinstance(
        source,
        dict,
    ):
        return None

    allowed = (
        "relay_mission_id",
        "execution_authority_hash",
        "target",
        "execution_worktree_path",
        "branch_name",
        "candidate_patch_sha256",
        "source_git_commit",
    )

    return {
        key: source.get(key)
        for key in allowed
        if key in source
    }


def _project_turn(
    session: GovernedJarvisChatSession,
    turn: dict[str, Any] | None,
    *,
    pending_fallback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = (
        turn
        if isinstance(
            turn,
            dict,
        )
        else {}
    )

    relay = payload.get(
        "relay_result"
    )

    if not isinstance(
        relay,
        dict,
    ):
        relay = {}

    workspace = getattr(
        session,
        "workspace",
        None,
    )

    return {
        "schema_version":
            SCHEMA_VERSION,

        "status":
            str(
                payload.get(
                    "status",
                    "OK",
                )
            ),

        "surface_text":
            str(
                payload.get(
                    "surface_text",
                    "",
                )
            ),

        "real_execution":
            bool(
                payload.get(
                    "real_execution",
                    False,
                )
            ),

        "mission_state":
            relay.get(
                "mission_state"
            ),

        "hold_reason":
            relay.get(
                "hold_reason"
            ),

        "relay_mission_id":
            relay.get(
                "relay_mission_id"
            ),

        "execution_authority_hash":
            relay.get(
                "execution_authority_hash"
            ),

        "pending_governed_mission":
            _pending_snapshot(
                session,
                pending_fallback,
            ),

        "session_id":
            session.session_id,

        "session_label":
            session.session_label,

        "workspace":
            (
                str(workspace)
                if workspace is not None
                else None
            ),

        "authority":
            AUTHORITY,

        "decision_authority":
            DECISION_AUTHORITY,

        "http_transport_is_authority":
            False,

        "browser_selects_workspace":
            False,

        "native_openjarvis_approval_is_authority":
            False,
    }


@router.post("/session")
def ensure_jarvis_session():
    session = _ensure_session()

    return _project_turn(
        session,
        None,
    )


@router.get("/status")
def jarvis_status():
    session = _ensure_session()

    pending = _pending_snapshot(
        session
    )

    if pending is None:
        return {
            **_project_turn(
                session,
                None,
            ),
            "status":
                "JARVIS_GOVERNED_IDLE",
        }

    turn = session.ask(
        "/governed-status"
    )

    return _project_turn(
        session,
        turn,
        pending_fallback=pending,
    )


@router.post("/turn")
def jarvis_turn(
    request: JarvisTurnRequest,
):
    text = str(
        request.text or ""
    ).strip()

    if not text:
        raise HTTPException(
            status_code=422,
            detail="JARVIS_TEXT_REQUIRED",
        )

    lower = text.lower()

    if (
        lower.startswith(
            "/governed-authorize"
        )
        or lower.startswith(
            "/governed-prepare"
        )
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "error":
                    "GOVERNED_COMMAND_REQUIRES_DEDICATED_ENDPOINT",
                "authority":
                    AUTHORITY,
                "decision_authority":
                    DECISION_AUTHORITY,
            },
        )

    session = _ensure_session()

    turn = session.ask(
        text
    )

    return _project_turn(
        session,
        turn,
    )


@router.post("/prepare")
def jarvis_prepare(
    request: JarvisPrepareRequest,
):
    raw = str(
        request.candidate_patch_path
        or ""
    ).strip()

    if not raw:
        raise HTTPException(
            status_code=422,
            detail="CANDIDATE_PATCH_PATH_REQUIRED",
        )

    if (
        "\n" in raw
        or "\r" in raw
        or '"' in raw
    ):
        raise HTTPException(
            status_code=422,
            detail="CANDIDATE_PATCH_PATH_INVALID",
        )

    session = _ensure_session()

    turn = session.ask(
        (
            '/governed-prepare-candidate "'
            + raw
            + '"'
        )
    )

    return _project_turn(
        session,
        turn,
    )


@router.post("/authorize")
def jarvis_authorize(
    request: JarvisAuthorizeRequest,
):
    eah = str(
        request.execution_authority_hash
        or ""
    ).strip()

    if not _full_sha256(
        eah
    ):
        raise HTTPException(
            status_code=422,
            detail="EXACT_64_HEX_EAH_REQUIRED",
        )

    session = _ensure_session()

    pending = _pending_snapshot(
        session
    )

    if not isinstance(
        pending,
        dict,
    ):
        raise HTTPException(
            status_code=409,
            detail="NO_PENDING_GOVERNED_MISSION",
        )

    expected = pending.get(
        "execution_authority_hash"
    )

    if eah != expected:
        raise HTTPException(
            status_code=409,
            detail={
                "error":
                    "EAH_MISMATCH",
                "authority":
                    AUTHORITY,
                "decision_authority":
                    DECISION_AUTHORITY,
            },
        )

    turn = session.ask(
        (
            "/governed-authorize "
            + eah
        )
    )

    return _project_turn(
        session,
        turn,
        pending_fallback=pending,
    )
