
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict
try:
    test_data = {'G1': {'status': 'active'}, 'G2': {'status': 'ready'}}
    result = verdict(test_data)
    print(f'VERDICT FINAL: {result}')
except Exception as e:
    print(f'ERREUR DEXECUTION: {e}')

