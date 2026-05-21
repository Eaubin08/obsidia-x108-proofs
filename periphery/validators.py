from .common import ActionCandidate, PeripheralSignalPacket
def validate_action_candidate(a:ActionCandidate)->None:
    if not a.action_id: raise ValueError('ACTION_ID_REQUIRED')
    if not a.domain: raise ValueError('DOMAIN_REQUIRED')
def validate_packet(p:PeripheralSignalPacket)->None:
    p.assert_non_sovereign()
    if not p.action_id: raise ValueError('PACKET_ACTION_ID_REQUIRED')
