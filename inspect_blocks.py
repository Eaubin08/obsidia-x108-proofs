
from periphery.engine_gates.v4_structure.gate_engine_v4 import blocking_tasks
try:
    # On passe le même dictionnaire de test
    test_data = {'G1': {'status': 'active'}, 'G2': {'status': 'ready'}}
    # On appelle la fonction de blocage
    blocages = blocking_tasks(test_data)
    print(f'BLOCAGES EN COURS: {blocages}')
except Exception as e:
    print(f'ERREUR D AUDIT: {e}')

