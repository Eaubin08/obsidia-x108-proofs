"""CSSA pass 5: read-only supporters, partner and communications campaign.

Pure deterministic proposals. Never sends email, publishes posts, mutates CRM
or imports identities/consents. Personal transactions never become club tasks.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

KINDS={"MATCH_INFORMATION","MARKETING","TICKET_CONFIRMATION","SUBSCRIPTION","SUPPORTER_REQUEST","PARTNER_INVITATION","PARTNER_DELIVERY","SPONSOR_CONTRACT","INSTITUTIONAL_MESSAGE","OPERATIONAL_REQUEST","REFUND_REQUEST"}
AUDIENCES={"PUBLIC","SUPPORTER","SUBSCRIBER","TICKET_BUYER","PARTNER","STAFF","INSTITUTION"}
SOURCES={"PUBLIC_READONLY","PERSONAL_INBOX","CSSA_OPERATIONAL_MAILBOX","SIMULATED_CRM"}
CHANNELS={"EMAIL","SOCIAL","WEB","CRM"}
PERSONAL_ONLY={"TICKET_CONFIRMATION","SUBSCRIPTION"}
SENSITIVE={"REFUND_REQUEST","SPONSOR_CONTRACT"}
WORK={"SUPPORTER_REQUEST","PARTNER_INVITATION","PARTNER_DELIVERY","SPONSOR_CONTRACT","INSTITUTIONAL_MESSAGE","OPERATIONAL_REQUEST","REFUND_REQUEST"}

@dataclass(frozen=True)
class CSSACommunicationCaseV0:
    case_id: str
    kind: str
    audience: str
    source_scope: str
    source_ref: str | None
    evidence_refs: tuple[str,...]
    channel: str
    subject: str
    body: str
    owner_ref: str | None = None
    recipient_scope_verified: bool = False
    legal_basis_verified: bool = False
    content_approved: bool = False
    human_reviewer_ref: str | None = None
    operational_authority_verified: bool = False
    unknowns: tuple[str,...] = ()
    contradictions: tuple[str,...] = ()
    simulation_only: bool = True

def assess_cssa_communication_case_v0(row: CSSACommunicationCaseV0) -> dict:
    if not isinstance(row,CSSACommunicationCaseV0): raise ValueError("CSSA_COMM_TYPE_INVALID")
    if not row.case_id or row.kind not in KINDS or row.audience not in AUDIENCES or row.source_scope not in SOURCES or row.channel not in CHANNELS:
        raise ValueError("CSSA_COMM_CONTRACT_INVALID")
    if not row.simulation_only: raise ValueError("CSSA_COMM_REAL_SEND_FORBIDDEN")
    reasons=[]
    if row.contradictions: reasons.extend("CONTRADICTION:"+x for x in row.contradictions)
    if row.unknowns: reasons.extend("UNKNOWN:"+x for x in row.unknowns)
    if not row.source_ref or not row.evidence_refs: reasons.append("SOURCE_PROVENANCE_MISSING")
    if not row.subject.strip() or not row.body.strip(): reasons.append("CONTENT_MISSING")
    if row.kind in WORK and row.source_scope!="CSSA_OPERATIONAL_MAILBOX":
        reasons.append("NOT_AUTHORIZED_CSSA_OPERATIONAL_SOURCE")
    if row.kind in PERSONAL_ONLY and row.source_scope=="PERSONAL_INBOX":
        classification="PERSONAL_TRANSACTION_ONLY"
    elif row.kind in {"MATCH_INFORMATION","MARKETING"}:
        classification="INFORMATION_OR_MARKETING"
    elif row.kind in WORK:
        classification="WORK_CANDIDATE" if row.source_scope=="CSSA_OPERATIONAL_MAILBOX" else "SHADOW_ONLY"
    else:
        classification="SHADOW_ONLY"
    if not row.owner_ref and row.kind in WORK: reasons.append("OWNER_MISSING")
    if not row.human_reviewer_ref: reasons.append("HUMAN_REVIEW_REQUIRED")
    if not row.recipient_scope_verified: reasons.append("RECIPIENT_SCOPE_UNVERIFIED")
    if not row.legal_basis_verified: reasons.append("LEGAL_BASIS_UNVERIFIED")
    if not row.content_approved: reasons.append("CONTENT_NOT_APPROVED")
    if not row.operational_authority_verified: reasons.append("CLUB_AUTHORITY_UNVERIFIED")
    if row.kind in SENSITIVE and not row.evidence_refs: reasons.append("SENSITIVE_CASE_EVIDENCE_MISSING")
    if row.kind in PERSONAL_ONLY and row.source_scope=="PERSONAL_INBOX":
        status="PERSONAL_READONLY"
    elif row.contradictions: status="BLOCK"
    else: status="HOLD"
    return {"id":row.case_id,"kind":row.kind,"audience":row.audience,
       "classification":classification,"status":status,"reasons":tuple(reasons),
       "communication_draft":{"subject":row.subject,"body":row.body} if row.body.strip() and row.subject.strip() else None,
       "crm_work_candidate":classification=="WORK_CANDIDATE" and not row.contradictions and bool(row.source_ref) and bool(row.evidence_refs) and bool(row.owner_ref),
       "sent":False,"published":False,"crm_mutations":0,"approval_granted":False}

def build_cssa_communication_campaign_v0(cases: tuple[CSSACommunicationCaseV0,...]) -> dict:
    from collections import Counter
    seen=set()
    entries=[]
    for row in cases:
        if row.case_id in seen: raise ValueError("CSSA_COMM_DUPLICATE_CASE")
        seen.add(row.case_id)
        entries.append(assess_cssa_communication_case_v0(row))
    payload={"schema":"CSSA_PASS05_SUPPORTERS_PARTNERS_COMMS_V0",
        "entries":entries,"count":len(entries),
        "classifications":dict(Counter(x["classification"] for x in entries)),
        "statuses":dict(Counter(x["status"] for x in entries)),
        "emails_sent":0,"publications":0,"crm_writes":0,
        "real_approvals":0,"decision_authority":"KX108_ONLY",
        "scope":"SIMULATION_READONLY"}
    payload["report_sha256"]=sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,default=list,separators=(",",":")).encode()).hexdigest()
    return payload
