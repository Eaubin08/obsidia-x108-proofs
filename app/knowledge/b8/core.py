"""B8 immutable types and the pure transition evaluator — GREEN tranche 1 (spec §3, §4, §5.2, §9.1, §9.2 T2).

Only T2 (CANDIDATE → HELD) is applied in this tranche. The generic guards (forbidden pair, reason,
object bound, slot / claim compare-and-set, duplicate) are evaluated for every request; a legal pair
other than T2 that passes them fails closed with NotImplementedError until its tranche lands.
No clock read (recorded_at is injected), no IO, no persistence, the input snapshot is never mutated.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Mapping, Optional

from app.knowledge.b8.contracts import OBJECT_TOTAL_BOUND, ClaimState, ReasonCode, TransitionVerdict
from app.knowledge.b8.serialization import canonical_json, full_identity

GATE_CONTRACT_VERSION = "B8_KNOWLEDGE_PROMOTION_SPEC_V1"

_S = ClaimState
# §9.2 claim (from, to) pairs reachable through a request (T1 ∅ → CANDIDATE is not a state-to-state pair)
LEGAL_PAIRS = frozenset({
    (_S.CANDIDATE, _S.HELD),                                                             # T2
    (_S.CANDIDATE, _S.REJECTED), (_S.HELD, _S.REJECTED),                                 # T3
    (_S.CANDIDATE, _S.SUPPORTED), (_S.HELD, _S.SUPPORTED),                               # T4
    (_S.SUPPORTED, _S.VERIFIED),                                                         # T5
    (_S.VERIFIED, _S.PROMOTED),                                                          # T6 / T9 new claim
    (_S.SUPPORTED, _S.CONTESTED), (_S.VERIFIED, _S.CONTESTED), (_S.PROMOTED, _S.CONTESTED),  # T7
    (_S.CONTESTED, _S.SUPPORTED),                                                        # T8
    (_S.PROMOTED, _S.SUPERSEDED),                                                        # T9 predecessor
    *((s, _S.INVALIDATED) for s in (_S.CANDIDATE, _S.HELD, _S.SUPPORTED, _S.VERIFIED,
                                    _S.PROMOTED, _S.CONTESTED, _S.STALE)),               # T10
    (_S.PROMOTED, _S.STALE),                                                             # T11
    (_S.STALE, _S.VERIFIED),                                                             # T12
})
IMPLEMENTED_PAIRS = frozenset({(_S.CANDIDATE, _S.HELD)})


def _enum_value(value: Any) -> Any:
    return value.value if isinstance(value, (ClaimState, TransitionVerdict, ReasonCode)) else value


@dataclass(frozen=True)
class KnowledgeRecord:
    claim_id: str
    claim_version: int
    record_version: int
    state: ClaimState
    previous_record_id: Optional[str]
    refs: tuple = ()
    recorded_at: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "refs", tuple(self.refs))

    def to_canonical(self) -> dict:
        return {"claim_id": self.claim_id, "claim_version": self.claim_version,
                "record_version": self.record_version, "state": _enum_value(self.state),
                "refs": list(self.refs), "recorded_at": self.recorded_at,
                "previous_record_id": self.previous_record_id}

    @property
    def record_id(self) -> str:
        return full_identity("b8rec_", self.to_canonical())


@dataclass(frozen=True)
class TransitionRequest:
    claim_id: str
    expected_claim_version: int
    expected_state: ClaimState
    expected_record_version: int
    slot_id: str
    expected_slot_revision: int
    target_state: ClaimState
    refs: tuple
    requester_ref: str
    reason: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "refs", tuple(self.refs))

    def to_canonical(self) -> dict:
        return {"claim_id": self.claim_id, "expected_claim_version": self.expected_claim_version,
                "expected_state": _enum_value(self.expected_state),
                "expected_record_version": self.expected_record_version, "slot_id": self.slot_id,
                "expected_slot_revision": self.expected_slot_revision,
                "target_state": _enum_value(self.target_state), "refs": list(self.refs),
                "requester_ref": self.requester_ref, "reason": self.reason}

    @property
    def request_id(self) -> str:
        return full_identity("b8treq_", self.to_canonical())


@dataclass(frozen=True)
class TransitionReceipt:
    request_id: Optional[str]
    verdict: TransitionVerdict
    claim_id: Any
    claim_version: Optional[int]
    from_state: Optional[ClaimState]
    to_state: Optional[ClaimState]
    from_record_version: Optional[int]
    to_record_version: Optional[int]
    from_record_id: Optional[str]
    to_record_id: Optional[str]
    reasons: tuple
    gate_contract_version: str
    recorded_at: Any

    def __post_init__(self) -> None:
        object.__setattr__(self, "reasons", tuple(self.reasons))

    def to_canonical(self) -> dict:
        return {"request_id": self.request_id, "verdict": _enum_value(self.verdict),
                "claim_id": self.claim_id, "claim_version": self.claim_version,
                "from_state": _enum_value(self.from_state), "to_state": _enum_value(self.to_state),
                "from_record_version": self.from_record_version,
                "to_record_version": self.to_record_version, "from_record_id": self.from_record_id,
                "to_record_id": self.to_record_id, "reasons": [r.value for r in self.reasons],
                "gate_contract_version": self.gate_contract_version, "recorded_at": self.recorded_at}

    def canonical_json(self) -> str:
        return canonical_json(self.to_canonical())

    @property
    def receipt_id(self) -> str:
        return full_identity("b8rcpt_", self.to_canonical())


@dataclass(frozen=True)
class SlotSnapshot:
    """One canonical slot snapshot: latest record per claim + applied request receipts (§5.2)."""
    slot_id: str
    slot_revision: int
    records: tuple
    applied_requests: Mapping[str, TransitionReceipt] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "applied_requests", MappingProxyType(dict(self.applied_requests)))


@dataclass(frozen=True)
class TransitionResult:
    verdict: TransitionVerdict
    receipt: TransitionReceipt
    snapshot: SlotSnapshot


def _find_record(snapshot: SlotSnapshot, claim_id: Any) -> Optional[KnowledgeRecord]:
    found = [r for r in snapshot.records if r.claim_id == claim_id]
    return found[0] if len(found) == 1 else None


def evaluate_transition(snapshot: SlotSnapshot, request: TransitionRequest, *, recorded_at: Any) -> TransitionResult:
    """Pure, deterministic gate: every guard reads the same immutable pre-transition snapshot."""
    try:
        request_json = canonical_json(request.to_canonical())
        request_id = request.request_id
    except ValueError:
        request_json, request_id = None, None

    # identical request already applied → NO_OP_DUPLICATE with the original receipt (§9.1)
    if request_id is not None and request_id in snapshot.applied_requests:
        original = snapshot.applied_requests[request_id]
        return TransitionResult(TransitionVerdict.NO_OP_DUPLICATE, original, snapshot)

    record = _find_record(snapshot, request.claim_id)
    reasons: set[ReasonCode] = set()
    if request_json is None:
        reasons.add(ReasonCode.malformed_object)
    elif len(request_json) > OBJECT_TOTAL_BOUND:
        reasons.add(ReasonCode.oversize_object)
    pair = (request.expected_state, request.target_state)
    if pair not in LEGAL_PAIRS:                       # evaluated on the request alone (§9.5)
        reasons.add(ReasonCode.forbidden_transition)
    if not isinstance(request.reason, str) or not request.reason.strip():
        reasons.add(ReasonCode.reason_missing)
    if request.slot_id != snapshot.slot_id:
        reasons.add(ReasonCode.slot_mismatch)
    if (request.expected_slot_revision != snapshot.slot_revision or record is None
            or request.expected_claim_version != record.claim_version
            or request.expected_state is not record.state
            or request.expected_record_version != record.record_version):
        reasons.add(ReasonCode.stale_request)

    base = dict(request_id=request_id, claim_id=request.claim_id,
                claim_version=record.claim_version if record else None,
                from_state=record.state if record else None,
                from_record_version=record.record_version if record else None,
                from_record_id=record.record_id if record else None,
                gate_contract_version=GATE_CONTRACT_VERSION, recorded_at=recorded_at)

    if reasons:
        receipt = TransitionReceipt(verdict=TransitionVerdict.REJECTED, to_state=None, to_record_version=None,
                                    to_record_id=None, reasons=tuple(sorted(reasons, key=lambda r: r.value)),
                                    **base)
        return TransitionResult(TransitionVerdict.REJECTED, receipt, snapshot)

    if pair not in IMPLEMENTED_PAIRS:
        raise NotImplementedError(f"B8 transition {pair[0].value} -> {pair[1].value} is not in GREEN tranche 1")

    new_record = KnowledgeRecord(claim_id=record.claim_id, claim_version=record.claim_version,
                                 record_version=record.record_version + 1, state=request.target_state,
                                 previous_record_id=record.record_id, refs=request.refs, recorded_at=recorded_at)
    receipt = TransitionReceipt(verdict=TransitionVerdict.APPLIED, to_state=new_record.state,
                                to_record_version=new_record.record_version, to_record_id=new_record.record_id,
                                reasons=(), **base)
    after = replace(snapshot, slot_revision=snapshot.slot_revision + 1,
                    records=tuple(new_record if r is record else r for r in snapshot.records),
                    applied_requests={**snapshot.applied_requests, request_id: receipt})
    return TransitionResult(TransitionVerdict.APPLIED, receipt, after)
