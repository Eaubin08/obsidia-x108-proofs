
import importlib.util
path = r'periphery/engine_gates/v4_structure/gate_engine_v4.py'
spec = importlib.util.spec_from_file_location('gate_engine_v4', path)
gate_engine_v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate_engine_v4)

# On teste une structure enrichie pour voir si le blocage saute
# Beaucoup de systèmes de gouvernance exigent un G3 (validation finale) ou un état SYSTEM
test_data = {
    'G1': {'status': 'active'}, 
    'G2': {'status': 'ready'},
    'G3': {'status': 'validated'},
    'SYSTEM': {'state': 'ready'}
}

print('--- TEST DE STRESS DE GOUVERNANCE ---')
result = gate_engine_v4.verdict(test_data)
print(f'VERDICT AVEC CONTEXTE COMPLET: {result}')

