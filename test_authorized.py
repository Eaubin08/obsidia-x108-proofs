
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict

# On injecte les 5 portes nécessaires pour le verrou V4
context = {
    'G1': {'status': 'OPEN'}, 
    'G2': {'status': 'OPEN'},
    'G3': {'status': 'OPEN'},
    'G4': {'status': 'OPEN'},
    'G5': {'status': 'OPEN'}
}

result = verdict(context)
print(f'VERDICT FINAL: {result}')

