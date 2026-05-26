
import sys
import importlib.util

path = r'periphery/engine_gates/v4_structure/gate_engine_v4.py'
spec = importlib.util.spec_from_file_location('gate_engine_v4', path)
gate_engine_v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate_engine_v4)

original_verdict = gate_engine_v4.verdict

def hooked_verdict(gates):
    print('--- TRACEUR DE DONNEES ---')
    print('Analyse en cours sur ces pépites: ' + str(list(gates.keys())))
    result = original_verdict(gates)
    print('Verdict rendu: ' + str(result))
    return result

gate_engine_v4.verdict = hooked_verdict
test_data = {'G1': {'status': 'active'}, 'G2': {'status': 'ready'}}
gate_engine_v4.verdict(test_data)

