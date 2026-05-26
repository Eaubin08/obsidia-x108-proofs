
# -*- coding: utf-8 -*-
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict
try:
    test_data = {'G1': {'status': 'active'}, 'G2': {'status': 'ready'}}
    result = verdict(test_data)
    print(f'RESULTAT BRUT: {result}')
except Exception as e:
    print(f'LOG D AUDIT COMPLET: {e}')

