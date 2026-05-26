from .common import PeripheralSignalPacket
_PRIORITY={'NONE':0,'HOLD':1,'BLOCK_CANDIDATE':2}
def merge_packets(*packets:PeripheralSignalPacket)->PeripheralSignalPacket:
    if not packets: raise ValueError('NO_PACKETS')
    base=PeripheralSignalPacket(packets[0].action_id, packets[0].domain)
    for p in packets:
        p.assert_non_sovereign()
        if p.action_id!=base.action_id or p.domain!=base.domain: raise ValueError('PACKET_MISMATCH')
        base.extra_metrics.update(p.extra_metrics)
        base.unknowns.extend(p.unknowns); base.risk_flags.extend(p.risk_flags); base.contradictions.extend(p.contradictions); base.evidence_refs.extend(p.evidence_refs)
        if _PRIORITY[p.recommended_gate]>_PRIORITY[base.recommended_gate]: base.recommended_gate=p.recommended_gate
    base.unknowns=sorted(set(base.unknowns)); base.risk_flags=sorted(set(base.risk_flags)); base.contradictions=sorted(set(base.contradictions)); base.evidence_refs=sorted(set(base.evidence_refs))
    return base
