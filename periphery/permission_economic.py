from .common import ActionCandidate, PeripheralSignalPacket
from .hackathon_failures import FailureCode
def run_permission_economic(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain)
    approval_required=bool(p.get('approval_required',False)); approval_obtained=bool(p.get('approval_obtained',not approval_required))
    permission_ok=all(bool(p.get(k,True)) for k in ['role_ok','tool_ok','domain_ok','action_ok','amount_ok','identity_ok']) and approval_obtained
    economic_ok=all(bool(p.get(k,True)) for k in ['spending_limit_ok','policy_ok','recipient_ok','kyc_aml_ok','audit_record_ok'])
    o.extra_metrics.update({'permission_ok':permission_ok,'economic_ok':economic_ok,'approval_required':approval_required,'approval_obtained':approval_obtained})
    if not permission_ok: o.add_contradiction(FailureCode.PERMISSION_MISSING.value); o.recommended_gate='BLOCK_CANDIDATE' if a.irreversible else 'HOLD'
    if not bool(p.get('spending_limit_ok',True)): o.add_contradiction(FailureCode.PAYMENT_LIMIT_FAIL.value); o.recommended_gate='BLOCK_CANDIDATE'
    if approval_required and not approval_obtained: o.add_unknown(FailureCode.APPROVAL_REQUIRED_MISSING.value); o.recommended_gate='HOLD'
    if not bool(p.get('kyc_aml_ok',True)): o.add_contradiction(FailureCode.KYC_AML_MISSING.value); o.recommended_gate='BLOCK_CANDIDATE'
    if not bool(p.get('policy_ok',True)): o.add_contradiction(FailureCode.POLICY_ENFORCEMENT_FAIL.value); o.recommended_gate='BLOCK_CANDIDATE'
    if not bool(p.get('audit_record_ok',True)): o.add_unknown(FailureCode.AUDIT_READY_RECORD_MISSING.value); o.recommended_gate='HOLD'
    return o
