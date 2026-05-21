from math import exp, log
from .common import ActionCandidate, PeripheralSignalPacket
def eml(x:float,y:float)->float:
    if y<=0: raise ValueError('EML_Y_MUST_BE_POSITIVE')
    return exp(x)-log(y)
def run_eml_compression(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain); o.extra_metrics['eml_value']=eml(float(p.get('eml_x',0.0)),float(p.get('eml_y',1.0))); o.extra_metrics['eml_is_candidate_only']=True; o.evidence_refs.append('periphery:eml_candidate'); return o
