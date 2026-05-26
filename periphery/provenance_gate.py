from .common import ActionCandidate, PeripheralSignalPacket
def run_provenance_gate(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain)
    prov=float(p.get('provenance_score',1.0)); mim=float(p.get('mimetic_risk',0.0)); fake=bool(p.get('fake_provenance_detected',False))
    o.extra_metrics.update({'provenance_score':prov,'mimetic_risk':mim,'fake_provenance_detected':fake})
    if prov<0.6: o.add_unknown('PROVENANCE_WEAK'); o.recommended_gate='HOLD'
    if mim>0.7: o.add_risk('MIMETIC_RISK')
    if fake: o.add_contradiction('FAKE_PROVENANCE'); o.recommended_gate='BLOCK_CANDIDATE'
    return o
