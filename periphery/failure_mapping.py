from .hackathon_failures import FailureCode
UNKNOWN_CODES={FailureCode.STALE_DATA,FailureCode.MULTI_SOURCE_INSUFFICIENT,FailureCode.LIVE_WEB_ACCESS_MISSING,FailureCode.OBSERVABILITY_GAP,FailureCode.AUDIT_TRAIL_MISSING,FailureCode.APPROVAL_REQUIRED_MISSING,FailureCode.VOICE_INTENT_AMBIGUOUS,FailureCode.SPEAKER_CONFIDENCE_LOW,FailureCode.CLEAN_JSON_MISSING}
RISK_CODES={FailureCode.BOT_DETECTION_ACTIVE,FailureCode.RATE_LIMIT_ACTIVE,FailureCode.HALLUCINATION_RISK,FailureCode.DRIFT_RISK,FailureCode.MISUSE_RISK,FailureCode.AUTONOMOUS_ACTION_CAPABILITY,FailureCode.TOOL_CALL_RISK,FailureCode.AUTONOMOUS_TRADING_RISK,FailureCode.TRADING_PNL_OVERFIT_RISK,FailureCode.SELF_HEALING_FETCH_FAILED}
CONTRADICTION_CODES={FailureCode.PERMISSION_MISSING,FailureCode.PAYMENT_LIMIT_FAIL,FailureCode.KYC_AML_MISSING,FailureCode.POLICY_ENFORCEMENT_FAIL,FailureCode.DRAWDOWN_RISK_HIGH,FailureCode.MULTIMODAL_MISMATCH,FailureCode.GUARDRAILS_MISSING}
def classify_failure(code:FailureCode|str)->str:
    code=FailureCode(code)
    if code in CONTRADICTION_CODES: return 'contradiction'
    if code in RISK_CODES: return 'risk_flag'
    if code in UNKNOWN_CODES: return 'unknown'
    return 'risk_flag'
