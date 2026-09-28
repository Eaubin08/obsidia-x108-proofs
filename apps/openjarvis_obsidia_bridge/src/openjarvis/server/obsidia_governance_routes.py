"""
OpenJarvis-side transport proxy for Obsidia governance.

AUTHORITY=NONE.

The browser talks only to the existing OpenJarvis server.
This module forwards bounded governance requests to the local
Obsidia API. It never decides, authorizes or executes an action.

Native OpenJarvis ApprovalStore is intentionally NOT used as
Obsidia authority.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict


router = APIRouter(
    prefix="/v1/obsidia-governance",
    tags=["obsidia-governance"],
)

AUTHORITY = "NONE"
DECISION_AUTHORITY = "KX108_ONLY"

DEFAULT_OBSIDIA_URL = (
    "http://127.0.0.1:8001"
)


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )


class PrepareRequest(_StrictModel):
    candidate_patch_path: str


class AuthorizeRequest(_StrictModel):
    execution_authority_hash: str


def _base_url() -> str:
    raw = str(
        os.environ.get(
            "OBSIDIA_GOVERNANCE_URL",
            DEFAULT_OBSIDIA_URL,
        )
    ).strip().rstrip("/")

    parsed = urlparse(raw)

    if (
        parsed.scheme != "http"
        or parsed.hostname
        not in {
            "127.0.0.1",
            "localhost",
            "::1",
        }
    ):
        raise HTTPException(
            status_code=503,
            detail="OBSIDIA_GOVERNANCE_URL_MUST_BE_LOOPBACK_HTTP",
        )

    return raw


def _headers() -> dict[str, str]:
    out = {
        "Content-Type":
            "application/json",
        "Accept":
            "application/json",
    }

    key = str(
        os.environ.get(
            "OBSIDIA_GOVERNANCE_API_KEY",
            "",
        )
    ).strip()

    if key:
        out["Authorization"] = (
            "Bearer " + key
        )

    return out


def _forward_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = (
        json.dumps(payload).encode("utf-8")
        if payload is not None
        else None
    )

    request = Request(
        _base_url() + path,
        data=body,
        headers=_headers(),
        method=method,
    )

    try:
        with urlopen(
            request,
            timeout=15,
        ) as response:
            raw = response.read()

    except HTTPError as exc:
        raw = exc.read()

        try:
            detail = json.loads(
                raw.decode(
                    "utf-8",
                    errors="replace",
                )
            )
        except Exception:
            detail = raw.decode(
                "utf-8",
                errors="replace",
            )

        raise HTTPException(
            status_code=exc.code,
            detail=detail,
        ) from exc

    except URLError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error":
                    "OBSIDIA_GOVERNANCE_UNAVAILABLE",
                "reason":
                    str(exc.reason),
                "authority":
                    AUTHORITY,
                "decision_authority":
                    DECISION_AUTHORITY,
            },
        ) from exc

    try:
        data = json.loads(
            raw.decode(
                "utf-8",
                errors="strict",
            )
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="OBSIDIA_GOVERNANCE_INVALID_JSON",
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise HTTPException(
            status_code=502,
            detail="OBSIDIA_GOVERNANCE_RESPONSE_NOT_OBJECT",
        )

    return data


@router.post("/session")
async def governed_session() -> dict[str, Any]:
    return _forward_json(
        "POST",
        "/api/jarvis/session",
        {},
    )


@router.get("/status")
async def governed_status() -> dict[str, Any]:
    return _forward_json(
        "GET",
        "/api/jarvis/status",
    )


@router.post("/prepare")
async def governed_prepare(
    request: PrepareRequest,
) -> dict[str, Any]:
    return _forward_json(
        "POST",
        "/api/jarvis/prepare",
        {
            "candidate_patch_path":
                request.candidate_patch_path,
        },
    )


@router.post("/authorize")
async def governed_authorize(
    request: AuthorizeRequest,
) -> dict[str, Any]:
    return _forward_json(
        "POST",
        "/api/jarvis/authorize",
        {
            "execution_authority_hash":
                request.execution_authority_hash,
        },
    )
