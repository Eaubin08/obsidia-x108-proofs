from .common import ActionCandidate, PeripheralSignalPacket
from .constants import THETA_OC
def run_operational_constance(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain); beta=float(p.get('oc_beta',1.0)); dphi=float(p.get('oc_delta_phi',p.get('delta_Phi',1.0))); tcost=max(float(p.get('oc_tcost',1.0)),1e-9)
    flip=float(p.get('flip',0.0)); osc=float(p.get('osc',0.0)); tens=float(p.get('tens',0.0)); sigma=0.65*flip+0.20*osc+0.15*tens; S=(beta*dphi)/(tcost*sigma+1e-9)
    fake=bool(p.get('fake_stability',False)); agitation=flip>float(p.get('theta_flip',0.5)) or sigma>float(p.get('theta_sigma',0.7))
    o.extra_metrics.update({'oc_S':S,'oc_sigma':sigma,'flip':flip,'osc':osc,'tens':tens,'fake_stability':fake,'agitation':agitation})
    if fake: o.add_risk('FAKE_STABILITY'); o.extra_metrics['oc_regime']='R3_FAKE_STABILITY_DETECTED'; o.recommended_gate='HOLD'
    elif agitation: o.add_risk('AGITATION_DETECTED'); o.extra_metrics['oc_regime']='R4_AGITATION_DETECTED'; o.recommended_gate='HOLD'
    elif S<float(p.get('theta_oc',THETA_OC)): o.add_unknown('OPERATIONAL_CONSTANCE_LOW'); o.extra_metrics['oc_regime']='R1_REFLEXIVE_HOLD'; o.recommended_gate='HOLD'
    else: o.extra_metrics['oc_regime']='R0_AUTOMATIC_STABLE'
    o.extra_metrics['oc_stable']=S>=float(p.get('theta_oc',THETA_OC)) and not fake and not agitation
    return o
