"""B6 State-Explicit Harness contracts: typed, addressable, bounded, immutable working state.

WORKING_STATE != DURABLE_MEMORY != WORLD_MODEL != TRUTH. VISIBILITY != PERMISSION.
Every object here is read-only and non-sovereign: it describes context, it never decides,
authorizes, acts, writes memory or mutates the kernel (decision authority: KX108_ONLY).
"""
from __future__ import annotations

import json
from dataclasses import InitVar, dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

BOUNDARY: Mapping[str, Any] = MappingProxyType({
    "readonly": True,
    "decision_authority": "KX108_ONLY",
    "memory_write": False,
    "emits_act": False,
    "kernel_mutation": False,
    "allowed_to_decide": False,
    "allowed_to_act": False,
})

MAX_PAYLOAD_CHARS = 65_536          # bounded payload (canonical JSON)
LONG_PREVIEW_CHARS = 2_048          # LONG exposure: bounded preview, truncation recorded


class Visibility(str, Enum):
    """Context exposure level only (never an access right or a permission)."""
    HIDE = "HIDE"
    SHORT = "SHORT"
    LONG = "LONG"
    FULL = "FULL"


class StateStatus(str, Enum):
    KNOWN = "KNOWN"          # the source produced a resolved description
    OPEN = "OPEN"            # the source produced a description whose meaning stays open
    UNKNOWN = "UNKNOWN"      # the source could not tell (never dropped)
    ERROR = "ERROR"          # the source failed (never dropped)


def _canonical(payload: Any) -> str:
    try:
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"payload is not JSON-serializable: {type(exc).__name__}") from None
    if len(text) > MAX_PAYLOAD_CHARS:
        raise ValueError(f"payload exceeds {MAX_PAYLOAD_CHARS} chars")
    return text


@dataclass(frozen=True)
class StateEntry:
    state_id: str
    state_type: str
    source_ref: str
    payload: InitVar[Any] = None
    provenance: tuple[str, ...] = ()
    uncertainty: tuple[str, ...] = ()
    status: StateStatus = StateStatus.KNOWN
    visibility: Visibility = Visibility.SHORT
    tags: tuple[str, ...] = ()
    summary: str = ""
    observed_at: str | None = None        # only when the source grounds it; never invented
    payload_json: str = field(init=False, default="null")   # payload stored frozen as canonical JSON

    def __post_init__(self, payload: Any) -> None:
        for name in ("state_id", "state_type", "source_ref"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be a non-empty string")
        object.__setattr__(self, "payload_json", _canonical(payload))
        for name in ("provenance", "uncertainty", "tags"):
            object.__setattr__(self, name, tuple(str(x) for x in getattr(self, name)))
        object.__setattr__(self, "status", StateStatus(self.status))
        object.__setattr__(self, "visibility", Visibility(self.visibility))
        object.__setattr__(self, "summary", str(self.summary)[:280])

    @property
    def readonly(self) -> bool:
        return True

    @property
    def boundary(self) -> Mapping[str, Any]:
        return BOUNDARY

    def to_dict(self) -> dict[str, Any]:
        d = {"state_id": self.state_id, "state_type": self.state_type, "source_ref": self.source_ref,
             "payload": self.payload, "provenance": list(self.provenance),
             "uncertainty": list(self.uncertainty), "status": self.status.value,
             "visibility": self.visibility.value, "tags": list(self.tags), "summary": self.summary,
             "readonly": True}
        if self.observed_at is not None:
            d["observed_at"] = self.observed_at
        return d


def _payload(self: StateEntry) -> Any:
    return json.loads(self.payload_json)          # a fresh copy on every read: never writes back


StateEntry.payload = property(_payload)


def error_entry(state_id: str, source_ref: str, exc: BaseException, state_type: str = "ADAPTER_ERROR") -> StateEntry:
    """A failed source stays visible as an ERROR entry; only the exception type is kept (no message,
    which may carry secrets)."""
    return StateEntry(state_id=state_id, state_type=state_type, source_ref=source_ref,
                      payload={"error_type": type(exc).__name__}, provenance=(source_ref,),
                      uncertainty=("adapter_error",), status=StateStatus.ERROR, tags=("error",),
                      summary=f"{source_ref} failed ({type(exc).__name__})")


def render_entry(entry: StateEntry, visibility: Visibility) -> dict[str, Any] | None:
    """Deterministic exposure of one entry at one visibility level (HIDE -> None)."""
    visibility = Visibility(visibility)
    if visibility == Visibility.HIDE:
        return None
    view: dict[str, Any] = {"state_id": entry.state_id, "state_type": entry.state_type,
                            "source_ref": entry.source_ref, "status": entry.status.value,
                            "summary": entry.summary, "exposure": visibility.value,
                            "visibility_is_permission": False}
    if visibility == Visibility.SHORT:
        return view
    view.update(provenance=list(entry.provenance), uncertainty=list(entry.uncertainty), tags=list(entry.tags))
    if visibility == Visibility.LONG:
        text = entry.payload_json
        view.update(payload_preview=text[:LONG_PREVIEW_CHARS], payload_chars=len(text),
                    payload_truncated=len(text) > LONG_PREVIEW_CHARS)
        return view
    view["payload"] = entry.payload
    if entry.observed_at is not None:
        view["observed_at"] = entry.observed_at
    return view
