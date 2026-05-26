from .common import ActionCandidate, PeripheralSignalPacket
from .constants import THETA_MEMORY
def clip(x,lo=-1.0,hi=1.0): return max(lo,min(hi,x))
def run_memory_governor(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain)
    phi=float(p.get('phi_t',1.0)); prev=float(p.get('phi_prev',phi)); dt=max(float(p.get('delta_t',1.0)),1e-9); chi=clip((phi-prev)/dt)
    dR=float(p.get('delta_R',0.0)); dI=float(p.get('delta_I',0.0)); dC=float(p.get('delta_C',0.0)); delta_phi=dR+dI+dC+abs(chi)
    o.extra_metrics.update({'phi_context_alignment':phi,'chi_memory_torsion':chi,'delta_R':dR,'delta_I':dI,'delta_C':dC,'delta_Phi':delta_phi})
    if delta_phi>=float(p.get('tau_memory',THETA_MEMORY)):
        o.add_risk('MEMORY_UNSTABLE'); o.add_unknown('CONTEXT_DRIFT'); o.extra_metrics.update({'memory_status':'UNSTABLE','memory_write_policy':'FROZEN'}); o.recommended_gate='HOLD'
    else: o.extra_metrics.update({'memory_status':'STABLE','memory_write_policy':'CANDIDATE_ONLY'})
    return o
