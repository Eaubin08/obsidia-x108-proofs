import pytest
from periphery.cssa_supporters_partners_communications_pass5_v0 import (
 CSSACommunicationCaseV0, KINDS, assess_cssa_communication_case_v0,
 build_cssa_communication_campaign_v0,
)

def sample(kind, **kwargs):
    d=dict(case_id="sim:"+kind,kind=kind,audience="SUPPORTER",
       source_scope="CSSA_OPERATIONAL_MAILBOX",source_ref="sim:source",
       evidence_refs=("sim:evidence",),channel="EMAIL",
       subject="Simulation: "+kind,body="Message simulé, non envoyé",
       owner_ref="SIMULATED:OWNER",human_reviewer_ref="SIMULATED:REVIEWER")
    d.update(kwargs)
    return CSSACommunicationCaseV0(**d)

@pytest.mark.parametrize("kind",sorted(KINDS))
def test_all_eleven_communication_types_are_never_sent(kind):
    r=assess_cssa_communication_case_v0(sample(kind))
    assert r["sent"] is False
    assert r["published"] is False
    assert r["crm_mutations"]==0
    assert r["approval_granted"] is False
    assert r["status"]=="HOLD"

def test_personal_ticket_confirmation_is_not_club_task():
    r=assess_cssa_communication_case_v0(sample("TICKET_CONFIRMATION",
       source_scope="PERSONAL_INBOX",audience="TICKET_BUYER"))
    assert r["status"]=="PERSONAL_READONLY"
    assert r["classification"]=="PERSONAL_TRANSACTION_ONLY"
    assert r["crm_work_candidate"] is False

def test_personal_subscription_is_not_internal_evidence():
    r=assess_cssa_communication_case_v0(sample("SUBSCRIPTION",
       source_scope="PERSONAL_INBOX",audience="SUBSCRIBER"))
    assert r["classification"]=="PERSONAL_TRANSACTION_ONLY"
    assert r["crm_work_candidate"] is False

def test_public_partner_request_cannot_become_operational_case():
    r=assess_cssa_communication_case_v0(sample("PARTNER_INVITATION",
       source_scope="PUBLIC_READONLY",audience="PARTNER"))
    assert r["crm_work_candidate"] is False
    assert "NOT_AUTHORIZED_CSSA_OPERATIONAL_SOURCE" in r["reasons"]

def test_trusted_simulated_operational_work_is_candidate_not_write():
    r=assess_cssa_communication_case_v0(sample("SUPPORTER_REQUEST"))
    assert r["classification"]=="WORK_CANDIDATE"
    assert r["crm_work_candidate"] is True
    assert r["status"]=="HOLD"
    assert r["crm_mutations"]==0

def test_contradiction_blocks_communication():
    r=assess_cssa_communication_case_v0(sample("INSTITUTIONAL_MESSAGE",
       contradictions=("APPROVAL_CONFLICT",)))
    assert r["status"]=="BLOCK"
    assert r["crm_work_candidate"] is False

def test_missing_evidence_prevents_crm_candidate():
    r=assess_cssa_communication_case_v0(sample("OPERATIONAL_REQUEST",
        evidence_refs=()))
    assert r["crm_work_candidate"] is False

def test_full_campaign_classifies_and_preserves_no_send():
    cases=(sample("MATCH_INFORMATION"),sample("MARKETING"),
        sample("TICKET_CONFIRMATION",source_scope="PERSONAL_INBOX"),
        sample("SUBSCRIPTION",source_scope="PERSONAL_INBOX"),
        sample("SUPPORTER_REQUEST"),sample("PARTNER_INVITATION",audience="PARTNER"),
        sample("PARTNER_DELIVERY",audience="PARTNER"),
        sample("SPONSOR_CONTRACT",audience="PARTNER"),
        sample("INSTITUTIONAL_MESSAGE",audience="INSTITUTION"),
        sample("OPERATIONAL_REQUEST"),sample("REFUND_REQUEST",audience="TICKET_BUYER"))
    report=build_cssa_communication_campaign_v0(cases)
    assert report["count"]==11
    assert report["emails_sent"]==0
    assert report["crm_writes"]==0
    assert report["real_approvals"]==0
    assert len(report["report_sha256"])==64
    assert report["statuses"]["PERSONAL_READONLY"]==2

def test_duplicate_case_rejected():
    with pytest.raises(ValueError,match="DUPLICATE"):
        build_cssa_communication_campaign_v0((sample("MARKETING"),sample("MARKETING")))

def test_real_send_mode_rejected():
    with pytest.raises(ValueError,match="REAL_SEND_FORBIDDEN"):
        assess_cssa_communication_case_v0(sample("MARKETING",simulation_only=False))
