
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict
# On injecte le contexte complet pour lever le blocage
context = {
    'G1': {'status': 'active'}, 
    'G2': {'status': 'ready'},
    'SYSTEM': {'state': 'ready', 'mode': 'production'}
}
result = verdict(context)
print(f'VERDICT AVEC CONTEXTE SYSTEM: {result}')

