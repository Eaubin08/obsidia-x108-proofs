from .common import ActionCandidate, PeripheralSignalPacket
def run_ocs_generation(a:ActionCandidate)->PeripheralSignalPacket:
    p=a.payload; o=PeripheralSignalPacket(a.action_id,a.domain); generated=bool(p.get('generated_output',False)); replay=bool(p.get('replay_config_present',True))
    o.extra_metrics.update({'generated_output':generated,'modality':p.get('modality','text'),'generation_cost':float(p.get('generation_cost',0.0)),'replay_config_present':replay})
    if generated: o.add_risk('GENERATED_OUTPUT_NOT_TRUTH')
    if not replay: o.add_unknown('REPLAY_CONFIG_MISSING'); o.recommended_gate='HOLD'
    if p.get('multimodal_mismatch',False): o.add_contradiction('MULTIMODAL_MISMATCH'); o.recommended_gate='HOLD'
    if p.get('voice_intent_ambiguous',False): o.add_unknown('VOICE_INTENT_AMBIGUOUS'); o.recommended_gate='HOLD'
    if p.get('speaker_confidence_low',False): o.add_unknown('SPEAKER_CONFIDENCE_LOW'); o.add_risk('IDENTITY_UNCERTAIN'); o.recommended_gate='HOLD'
    return o
