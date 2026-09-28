"""Single canonical authority for internal resolution statuses.

One enum, one source of truth, used across the whole official path so no
two files invent competing string constants. Never serialized into
/output/results.json — audit-only.
"""
from __future__ import annotations

from enum import Enum


class ResolutionStatus(str, Enum):
    LOCAL_VALID = "LOCAL_VALID"
    LOCAL_INVALID = "LOCAL_INVALID"
    LOCAL_UNAVAILABLE = "LOCAL_UNAVAILABLE"
    LOCAL_EXCEPTION = "LOCAL_EXCEPTION"
    REMOTE_REQUIRED = "REMOTE_REQUIRED"
    REMOTE_ATTEMPTED = "REMOTE_ATTEMPTED"
    REMOTE_REPAIRABLE = "REMOTE_REPAIRABLE"
    REMOTE_REPAIRED = "REMOTE_REPAIRED"
    REMOTE_VALID = "REMOTE_VALID"
    REMOTE_INVALID = "REMOTE_INVALID"
    GOVERNED_WORLD_ACTION = "GOVERNED_WORLD_ACTION"
    FINAL_FAILURE = "FINAL_FAILURE"


# Statuses allowed to back a "successful" official projection for an
# answerable task. Anything else backing a projected answer is a bug.
SAFE_TO_PROJECT = frozenset({
    ResolutionStatus.LOCAL_VALID,
    ResolutionStatus.REMOTE_VALID,
    ResolutionStatus.REMOTE_REPAIRED,
    ResolutionStatus.GOVERNED_WORLD_ACTION,
})
