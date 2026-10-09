"""B8 immutable records and the single pure transition gate — T1–T12 (spec §3, §4, §5.1–§5.3, §6, §7, §9).

One gate (`evaluate_transition`) for every claim transition, T9 included (no second promotion authority).
Every guard reads the same immutable pre-transition snapshot; a guard whose inputs are not evaluable
contributes no reason; reasons are the complete, deduplicated set sorted by canonical ReasonCode string.
No clock read (recorded_at is injected), no IO, no persistence, the input snapshot is never mutated.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Mapping, Optional

from app.knowledge.b8.artifacts import (
    EvidenceRef, HumanAttestation, KnowledgeClaim, VerificationRecord, canonical_value,
)
from app.knowledge.b8.contracts import (
    ADMISSIBLE_VERIFIER_FAMILY, HUMAN_CLASSES, OBJECT_TOTAL_BOUND, REQUIRES_HUMAN_REVIEW, STALENESS_TRIGGERS,
    AttestationKind, ClaimState, ReasonCode, StalenessMechanism, TransitionVerdict, VerificationVerdict,
)
from app.knowledge.b8.serialization import canonical_json, full_identity
from app.knowledge.b8.temporal import TEMPORALLY_INDETERMINATE, contains, overlaps

GATE_CONTRACT_VERSION = "B8_KNOWLEDGE_PROMOTION_SPEC_V1"

_S = ClaimState
_R = ReasonCode
# §9.2 (from, to) pairs; None = ∅ (T1). PROMOTED → SUPERSEDED exists only inside a T9 bundle (§9.4).
LEGAL_PAIRS = frozenset({
    (None, _S.CANDIDATE),                                                                # T1
    (_S.CANDIDATE, _S.HELD),                                                             # T2
    (_S.CANDIDATE, _S.REJECTED), (_S.HELD, _S.REJECTED),                                 # T3
    (_S.CANDIDATE, _S.SUPPORTED), (_S.HELD, _S.SUPPORTED),                               # T4
    (_S.SUPPORTED, _S.VERIFIED),                                                         # T5
    (_S.VERIFIED, _S.PROMOTED),                                                          # T6 / T9 new claim
    (_S.SUPPORTED, _S.CONTESTED), (_S.VERIFIED, _S.CONTESTED), (_S.PROMOTED, _S.CONTESTED),  # T7
    (_S.CONTESTED, _S.SUPPORTED),                                                        # T8
    *((s, _S.INVALIDATED) for s in (_S.CANDIDATE, _S.HELD, _S.SUPPORTED, _S.VERIFIED,
                                    _S.PROMOTED, _S.CONTESTED, _S.STALE)),               # T10
    (_S.PROMOTED, _S.STALE),                                                             # T11
    (_S.STALE, _S.VERIFIED),                                                             # T12
})
_WITHDRAWN = frozenset({_S.INVALIDATED, _S.REJECTED})


@dataclass(frozen=True)
class KnowledgeRecord:
    claim_id: str
    claim_version: int
    record_version: int
    state: ClaimState
    previous_record_id: Optional[str]
    refs: tuple = ()
    recorded_at: Optional[str] = None
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    contested_by: tuple = ()
    staleness_trigger_refs: tuple = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "refs", tuple(self.refs))
        object.__setattr__(self, "contested_by", tuple(self.contested_by))
        object.__setattr__(self, "staleness_trigger_refs", tuple(self.staleness_trigger_refs))

    def to_canonical(self) -> dict:
        return {"claim_id": self.claim_id, "claim_version": self.claim_version,
                "record_version": self.record_version, "state": canonical_value(self.state),
                "refs": list(self.refs), "supersedes": self.supersedes, "superseded_by": self.superseded_by,
                "contested_by": list(self.contested_by), "recorded_at": self.recorded_at,
                "previous_record_id": self.previous_record_id,
                "staleness_trigger_refs": list(self.staleness_trigger_refs)}

    @property
    def record_id(self) -> str:
        return full_identity("b8rec_", self.to_canonical())

    @property
    def identity(self) -> str:
        return self.record_id


@dataclass(frozen=True)
class TransitionRequest:
    claim_id: str
    expected_claim_version: int
    expected_state: Optional[ClaimState]
    expected_record_version: int
    slot_id: str
    expected_slot_revision: int
    target_state: ClaimState
    refs: tuple
    requester_ref: str
    reason: str
    supersedes_claim_id: Optional[str] = None      # T9 only
    supersedes_record_id: Optional[str] = None     # T9 only

    def __post_init__(self) -> None:
        object.__setattr__(self, "refs", tuple(self.refs))

    @property
    def is_supersession(self) -> bool:
        return self.supersedes_claim_id is not None or self.supersedes_record_id is not None

    def to_canonical(self) -> dict:
        return {"claim_id": self.claim_id, "expected_claim_version": self.expected_claim_version,
                "expected_state": canonical_value(self.expected_state),
                "expected_record_version": self.expected_record_version, "slot_id": self.slot_id,
                "expected_slot_revision": self.expected_slot_revision,
                "target_state": canonical_value(self.target_state), "refs": list(self.refs),
                "requester_ref": self.requester_ref, "reason": self.reason,
                "supersedes_claim_id": self.supersedes_claim_id, "supersedes_record_id": self.supersedes_record_id}

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
        return {"request_id": self.request_id, "verdict": canonical_value(self.verdict),
                "claim_id": self.claim_id, "claim_version": self.claim_version,
                "from_state": canonical_value(self.from_state), "to_state": canonical_value(self.to_state),
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
class SupersessionTransitionBundle:
    """T9 atomic result (§9.3): both records, both receipts, both links, or nothing."""
    request_id: str
    old_claim_id: str
    old_from_record_id: str
    old_to_record_id: str
    new_claim_id: str
    new_from_record_id: str
    new_to_record_id: str
    old_transition_receipt: TransitionReceipt
    new_transition_receipt: TransitionReceipt
    supersedes_link: tuple
    superseded_by_link: tuple
    recorded_at: Any
    gate_contract_version: str

    def _body(self) -> dict:
        return {"request_id": self.request_id, "old_claim_id": self.old_claim_id,
                "old_from_record_id": self.old_from_record_id, "old_to_record_id": self.old_to_record_id,
                "new_claim_id": self.new_claim_id, "new_from_record_id": self.new_from_record_id,
                "new_to_record_id": self.new_to_record_id,
                "old_transition_receipt": self.old_transition_receipt.to_canonical(),
                "new_transition_receipt": self.new_transition_receipt.to_canonical(),
                "supersedes_link": list(self.supersedes_link), "superseded_by_link": list(self.superseded_by_link),
                "recorded_at": self.recorded_at, "gate_contract_version": self.gate_contract_version}

    @property
    def bundle_id(self) -> str:
        return full_identity("b8bundle_", self._body())

    def to_canonical(self) -> dict:
        return {**self._body(), "bundle_id": self.bundle_id}

    @property
    def bundle_digest(self) -> str:
        return hashlib.sha256(canonical_json(self.to_canonical()).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SlotSnapshot:
    """One canonical slot snapshot: record history (current state = unique max record_version), claims, applied results."""
    slot_id: str
    slot_revision: int
    records: tuple
    applied_requests: Mapping[str, Any] = field(default_factory=dict)
    claims: tuple = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))
        object.__setattr__(self, "claims", tuple(self.claims))
        object.__setattr__(self, "applied_requests", MappingProxyType(dict(self.applied_requests)))


@dataclass(frozen=True)
class TransitionResult:
    verdict: TransitionVerdict
    receipt: TransitionReceipt
    snapshot: SlotSnapshot
    bundle: Optional[SupersessionTransitionBundle] = None


# ---------------------------------------------------------------- gate context

def current_records(records) -> tuple[dict, frozenset]:
    """The single canonical current-state selector (§10 LATEST_EPISTEMIC_STATE).

    Current record of a claim = the unique record with maximal record_version; history is expected and kept.
    Two distinct records at the maximal version make the history ambiguous: the claim is reported, never
    resolved by input order, recorded_at or record id. Returns ({claim_id: record}, ambiguous claim ids).
    """
    tops: dict = {}
    for r in records:
        best = tops.get(r.claim_id)
        if best is None or r.record_version > best[0].record_version:
            tops[r.claim_id] = [r]
        elif r.record_version == best[0].record_version and r not in best:
            best.append(r)
    current = {cid: recs[0] for cid, recs in tops.items() if len(recs) == 1}
    return current, frozenset(cid for cid, recs in tops.items() if len(recs) > 1)


class _Context:
    """Immutable read-only view of the pre-transition inputs (built once, never written back)."""

    def __init__(self, snapshot, request, artifacts, trusted):
        self.snapshot, self.request, self.trusted = snapshot, request, frozenset(trusted)
        registry: dict = {}
        for c in snapshot.claims:
            objs = registry.setdefault(c.claim_id, [])
            if c not in objs:
                objs.append(c)
        self.claims = {cid: objs[0] for cid, objs in registry.items() if len(objs) == 1}
        self.ambiguous_claims = frozenset(cid for cid, objs in registry.items() if len(objs) > 1)
        self.latest, self.ambiguous = current_records(snapshot.records)
        self.record = self.latest.get(request.claim_id)
        supplied = {}
        for a in artifacts:
            supplied[a.claim_id if isinstance(a, KnowledgeClaim) else a.identity] = a
        self.supplied = supplied
        self.artifact_claims = tuple(a for a in artifacts if isinstance(a, KnowledgeClaim))
        self.subject = self.claims.get(request.claim_id) or (
            supplied.get(request.claim_id) if isinstance(supplied.get(request.claim_id), KnowledgeClaim) else None)
        version = self.record.claim_version if self.record else request.expected_claim_version
        bound, wrong = [], []
        ref_claims = []
        for ref in sorted(set(request.refs)):
            obj = supplied.get(ref)
            if isinstance(obj, (EvidenceRef, VerificationRecord, HumanAttestation)):
                (bound if (obj.claim_id, obj.claim_version) == (request.claim_id, version) else wrong).append(obj)
            elif ref in self.claims and ref != request.claim_id:
                ref_claims.append(self.claims[ref])
            # an unresolvable ref has no semantic effect (no IO lookup, no transform admission)
        self.bound, self.wrong, self.ref_claims = bound, wrong, ref_claims

    def bound_of(self, kind):
        return [a for a in self.bound if isinstance(a, kind)]

    def wrong_of(self, kind):
        return any(isinstance(a, kind) for a in self.wrong)

    def slot_view_complete(self) -> bool:
        """Complete canonical slot view (T6 / T9): every current record has exactly one claim in the snapshot
        registry, and no supplied claim object disagrees with it. Artifacts never complete the registry and
        no claim is reconstructed from records (CURRENT_RECORD_WITHOUT_CLAIM_OBJECT = not evaluable)."""
        if self.ambiguous or self.ambiguous_claims:
            return False
        if any(cid not in self.claims for cid in self.latest):
            return False
        return all(a == self.claims[a.claim_id] for a in self.artifact_claims if a.claim_id in self.claims)

    def slot_claims(self):
        """Other claims of this slot with their latest record, in canonical identity order."""
        out = []
        for cid in sorted(self.claims):
            c = self.claims[cid]
            if cid != self.request.claim_id and c.slot_id == self.snapshot.slot_id and cid in self.latest:
                out.append((c, self.latest[cid]))
        return out


def _evidence_guard(ctx, reasons, failure):
    bound = ctx.bound_of(EvidenceRef)
    if any(e.complete_provenance for e in bound):
        return
    # a correctly bound inadmissible ref, or no ref at all, fails; a wrongly bound ref alone is
    # ref_binding_mismatch only (§9.5) and never hides a different bound ref's own failure
    if bound or not ctx.wrong_of(EvidenceRef):
        reasons.add(failure)


def _attestation_guard(ctx, reasons, kind):
    candidates = [a for a in ctx.bound_of(HumanAttestation) if a.attestation_kind is kind]
    if any(a.admissible(ctx.trusted) for a in candidates):
        return
    if candidates:
        reasons.add(_R.attestation_inadmissible)
    else:                                        # a wrongly bound attestation is no candidate (own fact: ref_binding_mismatch)
        reasons.add(_R.attestation_missing)


def _verification_guard(ctx, reasons):
    """T5 / T12 (SA5): wrong binding, inadmissible family and unsatisfied verdict are disjoint facts."""
    cls = ctx.subject.claim_class if ctx.subject else None
    if cls in HUMAN_CLASSES:
        _attestation_guard(ctx, reasons, AttestationKind.PRIMARY_DECLARATION)
        return
    family = ADMISSIBLE_VERIFIER_FAMILY.get(cls)
    records = ctx.bound_of(VerificationRecord)
    admissible = [v for v in records if family is not None and v.verifier_family == family]

    def is_eligible(v):
        if v.verdict is not VerificationVerdict.SATISFIED:
            return False
        if ctx.record and ctx.record.state is _S.STALE:
            if ctx.subject:
                for r in ctx.snapshot.records:
                    if r.claim_id == ctx.subject.claim_id and r.claim_version == ctx.subject.claim_version:
                        if v.identity in r.refs:
                            return False
            if v.basis_record_id != ctx.record.record_id:
                return False
            triggers = set(ctx.record.staleness_trigger_refs)
            if not triggers.issubset(set(v.evidence_refs)):
                return False
        return True

    if any(is_eligible(v) for v in admissible):
        return
    if len(admissible) < len(records) or ctx.bound_of(HumanAttestation):
        reasons.add(_R.verifier_inadmissible)    # includes a human attestation offered on an objective class
    if admissible or not (records or ctx.bound_of(HumanAttestation) or ctx.wrong_of(VerificationRecord)
                          or ctx.wrong_of(HumanAttestation)):
        reasons.add(_R.verification_not_satisfied)


def _promotion_guards(ctx, reasons):
    """T6 / T9 shared conditions + free slot (T6) or eligible predecessor set E (T9)."""
    subj, req = ctx.subject, ctx.request
    if not ctx.slot_view_complete():             # slot semantics not evaluable: no occupancy / E conclusion
        reasons.add(_R.malformed_object)
        if subj is not None and subj.claim_class in REQUIRES_HUMAN_REVIEW:
            _attestation_guard(ctx, reasons, AttestationKind.REVIEW_AUTHORIZATION)
        return None
    if subj is None:
        reasons.add(_R.malformed_object)
        return None
    if subj.claim_class in REQUIRES_HUMAN_REVIEW:
        _attestation_guard(ctx, reasons, AttestationKind.REVIEW_AUTHORIZATION)
    promoted = []
    for other, rec in ctx.slot_claims():
        if rec.state is _S.CONTESTED:            # open contradiction on the slot / time
            rel = overlaps(subj.valid_time, other.valid_time)
            if rel is TEMPORALLY_INDETERMINATE:
                reasons.add(_R.temporal_relation_indeterminate)
            elif rel:
                reasons.add(_R.open_contradiction)
        elif rec.state is _S.PROMOTED:           # current state only, never historical records
            promoted.append((other, rec))
    if not req.is_supersession:
        for other, _ in promoted:
            rel = overlaps(subj.valid_time, other.valid_time)
            if rel is TEMPORALLY_INDETERMINATE:
                reasons.add(_R.temporal_relation_indeterminate)
            elif rel:
                reasons.add(_R.slot_occupied)
        return None
    return _t9_guards(ctx, reasons, promoted)


def _t9_guards(ctx, reasons, promoted):
    """SA6 / SA7: E evaluable first; designation fact and eligibility fact are independent."""
    subj, req = ctx.subject, ctx.request
    designated = ctx.claims.get(req.supersedes_claim_id)
    d_rec = ctx.latest.get(req.supersedes_claim_id)
    d_same_slot = False
    if designated is None or d_rec is None:
        reasons.add(_R.malformed_object)
    elif designated.slot_id != ctx.snapshot.slot_id:
        reasons.add(_R.slot_mismatch)
    else:
        d_same_slot = True
        if d_rec.state is not _S.PROMOTED:
            reasons.add(_R.referenced_claim_not_promoted)
    evaluable = all(overlaps(subj.valid_time, c.valid_time) is not TEMPORALLY_INDETERMINATE for c, _ in promoted)
    if not evaluable:
        reasons.add(_R.temporal_relation_indeterminate)
        return None                              # no cardinality of E is asserted
    eligible = [(c, r) for c, r in promoted if overlaps(subj.valid_time, c.valid_time)]
    if not eligible:
        reasons.add(_R.no_eligible_predecessor)
        return None
    if len(eligible) > 1:
        reasons.add(_R.multiple_predecessors_unsupported)
        return None
    if not (d_same_slot and d_rec.state is _S.PROMOTED):
        return None
    (member, member_rec), = eligible
    if member.claim_id != req.supersedes_claim_id or req.supersedes_record_id != member_rec.record_id:
        reasons.add(_R.predecessor_mismatch)
        return None
    if not contains(subj.valid_time, member.valid_time):
        reasons.add(_R.containment_not_satisfied)
        return None
    return member, member_rec


def _contest_guard(ctx, reasons):
    """T7: admissible contradicting evidence, or a contradicting claim whose overlap is established in-frame."""
    admissible = any(e.complete_provenance for e in ctx.bound_of(EvidenceRef))
    contradicting, indeterminate = [], False
    if ctx.subject is not None:
        for other in ctx.ref_claims:
            if other.slot_id != ctx.snapshot.slot_id:
                continue
            rel = overlaps(ctx.subject.valid_time, other.valid_time)
            if rel is TEMPORALLY_INDETERMINATE:
                indeterminate = True
            elif rel:
                contradicting.append(other.claim_id)
    if admissible or contradicting:
        return tuple(sorted(contradicting))
    reasons.add(_R.temporal_relation_indeterminate if indeterminate else _R.contradiction_inadmissible)
    return ()


def _resolution_guard(ctx, reasons):
    """T8: explicit resolution only — every contradicting side withdrawn and referenced, or new verification."""
    cls = ctx.subject.claim_class if ctx.subject else None
    family = ADMISSIBLE_VERIFIER_FAMILY.get(cls)
    
    def is_fresh_and_satisfied(v):
        if v.verdict is not VerificationVerdict.SATISFIED:
            return False
        if v.verifier_family != family:
            return False
        if ctx.subject:
            for r in ctx.snapshot.records:
                if r.claim_id == ctx.subject.claim_id and r.claim_version == ctx.subject.claim_version:
                    if v.identity in r.refs:
                        return False
        return True

    if any(is_fresh_and_satisfied(v) for v in ctx.bound_of(VerificationRecord)):
        return
    sides = ctx.record.contested_by if ctx.record else ()
    referenced = {c.claim_id for c in ctx.ref_claims}
    if sides and all(s in referenced and s in ctx.latest and ctx.latest[s].state in _WITHDRAWN for s in sides):
        return
    reasons.add(_R.contradiction_unresolved)


def _staleness_guard(ctx, reasons):
    mechanisms = STALENESS_TRIGGERS.get(ctx.subject.claim_class, frozenset()) if ctx.subject else frozenset()
    allowed = {m.value for m in mechanisms if isinstance(m, StalenessMechanism)}
    valid = [e for e in ctx.bound_of(EvidenceRef) if e.complete_provenance and e.kind in allowed]
    if not valid:
        reasons.add(_R.staleness_trigger_inadmissible)
        return None
    return tuple(sorted(set(e.identity for e in valid)))


def _rule_guards(ctx, pair, reasons):
    """Rule-specific preconditions (§9.2). Returns rule data needed to apply (T7 contesters, T9 predecessor)."""
    frm, to = pair
    if frm is None:                                                         # T1
        if not isinstance(ctx.subject, KnowledgeClaim) or ctx.subject.claim_id != ctx.request.claim_id:
            reasons.add(_R.malformed_object)
        elif ctx.subject.slot_id != ctx.snapshot.slot_id:
            reasons.add(_R.slot_mismatch)
        return None
    if ctx.record is None:                                                  # subject guards not evaluable
        return None
    if to is _S.SUPPORTED and frm in (_S.CANDIDATE, _S.HELD):               # T4
        _evidence_guard(ctx, reasons, _R.evidence_inadmissible)
    elif to is _S.VERIFIED:                                                 # T5 / T12
        _verification_guard(ctx, reasons)
    elif to is _S.PROMOTED:                                                 # T6 / T9
        return _promotion_guards(ctx, reasons)
    elif to is _S.CONTESTED:                                                # T7
        return _contest_guard(ctx, reasons)
    elif frm is _S.CONTESTED and to is _S.SUPPORTED:                        # T8
        _resolution_guard(ctx, reasons)
    elif to is _S.INVALIDATED:                                              # T10
        _evidence_guard(ctx, reasons, _R.evidence_inadmissible)
    elif to is _S.STALE:                                                    # T11
        return _staleness_guard(ctx, reasons)
    return None                                                             # T2 / T3: reason only


def _successor(record, state, request, recorded_at, **links):
    return KnowledgeRecord(claim_id=record.claim_id, claim_version=record.claim_version,
                           record_version=record.record_version + 1, state=state,
                           previous_record_id=record.record_id, refs=request.refs, recorded_at=recorded_at, **links)


def _receipt(request_id, before, after, recorded_at):
    return TransitionReceipt(request_id=request_id, verdict=TransitionVerdict.APPLIED, claim_id=after.claim_id,
                             claim_version=after.claim_version, from_state=before.state if before else None,
                             to_state=after.state, from_record_version=before.record_version if before else None,
                             to_record_version=after.record_version,
                             from_record_id=before.record_id if before else None, to_record_id=after.record_id,
                             reasons=(), gate_contract_version=GATE_CONTRACT_VERSION, recorded_at=recorded_at)


def evaluate_transition(snapshot: SlotSnapshot, request: TransitionRequest, *, recorded_at: Any,
                        artifacts: tuple = (), trusted_identity_sources: frozenset = frozenset()) -> TransitionResult:
    """Pure, deterministic gate: every guard reads the same immutable pre-transition snapshot."""
    try:
        request_json = canonical_json(request.to_canonical())
        request_id = request.request_id
    except ValueError:
        request_json, request_id = None, None

    # identical request already applied → NO_OP_DUPLICATE with the original receipt / bundle (§9.1)
    if request_id is not None and request_id in snapshot.applied_requests:
        original = snapshot.applied_requests[request_id]
        if isinstance(original, SupersessionTransitionBundle):
            return TransitionResult(TransitionVerdict.NO_OP_DUPLICATE, original.new_transition_receipt, snapshot,
                                    original)
        return TransitionResult(TransitionVerdict.NO_OP_DUPLICATE, original, snapshot)

    ctx = _Context(snapshot, request, artifacts, trusted_identity_sources)
    record = ctx.record
    reasons: set[ReasonCode] = set()
    if request_json is None:
        reasons.add(_R.malformed_object)
    elif len(request_json) > OBJECT_TOTAL_BOUND:
        reasons.add(_R.oversize_object)
    pair = (request.expected_state, request.target_state)
    legal = pair in LEGAL_PAIRS and (not request.is_supersession or pair == (_S.VERIFIED, _S.PROMOTED))
    if not legal:                                     # evaluated on the request alone (§9.5)
        reasons.add(_R.forbidden_transition)
    if not isinstance(request.reason, str) or not request.reason.strip():
        reasons.add(_R.reason_missing)
    if request.slot_id != snapshot.slot_id:
        reasons.add(_R.slot_mismatch)
    if ctx.ambiguous:                                 # ambiguous history: fail closed, no hidden tie-break
        reasons.add(_R.malformed_object)
    if request.expected_state is None:                # T1 compare-and-set: the claim must not exist yet
        stale = (request.claim_id in ctx.latest or request.claim_id in ctx.ambiguous
                 or request.expected_record_version != 0
                 or (ctx.subject is not None and request.expected_claim_version != ctx.subject.claim_version))
    elif request.claim_id in ctx.ambiguous:           # subject version guard not evaluable
        stale = False
    else:
        stale = (record is None or request.expected_claim_version != record.claim_version
                 or request.expected_state is not record.state
                 or request.expected_record_version != record.record_version)
    if stale or request.expected_slot_revision != snapshot.slot_revision:
        reasons.add(_R.stale_request)
    if ctx.wrong:
        reasons.add(_R.ref_binding_mismatch)
    rule_data = _rule_guards(ctx, pair, reasons) if legal else None

    if reasons:
        receipt = TransitionReceipt(
            request_id=request_id, verdict=TransitionVerdict.REJECTED, claim_id=request.claim_id,
            claim_version=record.claim_version if record else None, from_state=record.state if record else None,
            to_state=None, from_record_version=record.record_version if record else None, to_record_version=None,
            from_record_id=record.record_id if record else None, to_record_id=None,
            reasons=tuple(sorted(reasons, key=lambda r: r.value)), gate_contract_version=GATE_CONTRACT_VERSION,
            recorded_at=recorded_at)
        return TransitionResult(TransitionVerdict.REJECTED, receipt, snapshot)

    if request.expected_state is None:                # T1
        new = KnowledgeRecord(claim_id=request.claim_id, claim_version=ctx.subject.claim_version, record_version=1,
                              state=_S.CANDIDATE, previous_record_id=None, refs=request.refs, recorded_at=recorded_at)
        receipt = _receipt(request_id, None, new, recorded_at)
        after = replace(snapshot, slot_revision=snapshot.slot_revision + 1, records=snapshot.records + (new,),
                        claims=snapshot.claims + (ctx.subject,),
                        applied_requests={**snapshot.applied_requests, request_id: receipt})
        return TransitionResult(TransitionVerdict.APPLIED, receipt, after)

    if request.is_supersession:                       # T9 atomic bundle, one slot_revision step
        _, old = rule_data
        new_rec = _successor(record, _S.PROMOTED, request, recorded_at, supersedes=old.claim_id)
        old_rec = KnowledgeRecord(claim_id=old.claim_id, claim_version=old.claim_version,
                                  record_version=old.record_version + 1, state=_S.SUPERSEDED,
                                  previous_record_id=old.record_id, recorded_at=recorded_at,
                                  superseded_by=record.claim_id)
        new_receipt = _receipt(request_id, record, new_rec, recorded_at)
        old_receipt = _receipt(request_id, old, old_rec, recorded_at)
        bundle = SupersessionTransitionBundle(
            request_id=request_id, old_claim_id=old.claim_id, old_from_record_id=old.record_id,
            old_to_record_id=old_rec.record_id, new_claim_id=record.claim_id, new_from_record_id=record.record_id,
            new_to_record_id=new_rec.record_id, old_transition_receipt=old_receipt,
            new_transition_receipt=new_receipt, supersedes_link=(record.claim_id, old.claim_id),
            superseded_by_link=(old.claim_id, record.claim_id), recorded_at=recorded_at,
            gate_contract_version=GATE_CONTRACT_VERSION)
        after = replace(snapshot, slot_revision=snapshot.slot_revision + 1,
                        # append-only (§10); (old, new) is a non-semantic serialization order (§9.3 field order)
                        records=snapshot.records + (old_rec, new_rec),
                        applied_requests={**snapshot.applied_requests, request_id: bundle})
        return TransitionResult(TransitionVerdict.APPLIED, new_receipt, after, bundle)

    links = {"contested_by": rule_data} if request.target_state is _S.CONTESTED else {}
    if request.target_state is _S.STALE and rule_data is not None:
        links["staleness_trigger_refs"] = rule_data
    new_record = _successor(record, request.target_state, request, recorded_at, **links)
    receipt = _receipt(request_id, record, new_record, recorded_at)
    after = replace(snapshot, slot_revision=snapshot.slot_revision + 1,
                    records=snapshot.records + (new_record,),          # append-only history (§10)
                    applied_requests={**snapshot.applied_requests, request_id: receipt})
    return TransitionResult(TransitionVerdict.APPLIED, receipt, after)
