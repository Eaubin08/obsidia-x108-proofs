from .common import ActionCandidate, PeripheralSignalPacket
from .constants import THETA_CONTEXT_DRIFT,THETA_TRAJECTORY_DIVERGENCE
from .hackathon_failures import FailureCode
def run_timeverse(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain); div=float(p.get('trajectory_divergence',0.0)); drift=float(p.get('context_drift',0.0)); async_action=bool(p.get('async_action',False))
    o.extra_metrics.update({'trajectory_score':float(p.get('trajectory_score',1.0)),'trajectory_divergence':div,'context_drift':drift,'async_action':async_action})
    if async_action: o.add_unknown(FailureCode.ASYNC_RECHECK_REQUIRED.value); o.extra_metrics['x108_recheck_required_at_exec']=True
    if drift>=float(p.get('theta_context_drift',THETA_CONTEXT_DRIFT)): o.add_risk('CONTEXT_DRIFT'); o.recommended_gate='HOLD'
    if div>=float(p.get('theta_trajectory_divergence',THETA_TRAJECTORY_DIVERGENCE)): o.add_risk('TRAJECTORY_DIVERGENCE'); o.recommended_gate='HOLD'
    return o
