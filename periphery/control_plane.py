from .common import ActionCandidate, PeripheralSignalPacket
from .validators import validate_action_candidate
from .merge import merge_packets
from .data_gate import run_data_gate
from .provenance_gate import run_provenance_gate
from .memory_governor import run_memory_governor
from .eml_compression import run_eml_compression
from .energy_thermo import run_energy_thermo
from .timeverse import run_timeverse
from .ocs_generation import run_ocs_generation
from .operational_constance import run_operational_constance
from .permission_economic import run_permission_economic
def run_control_plane(a:ActionCandidate)->PeripheralSignalPacket:
    validate_action_candidate(a)
    packet=merge_packets(run_data_gate(a),run_provenance_gate(a),run_memory_governor(a),run_eml_compression(a),run_energy_thermo(a),run_timeverse(a),run_ocs_generation(a),run_operational_constance(a),run_permission_economic(a))
    packet.assert_non_sovereign(); return packet
