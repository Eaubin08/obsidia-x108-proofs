
import sys
import importlib.util

# Chemin physique exact
path = r'periphery/engine_gates/v4_structure/gate_engine_v4.py'
spec = importlib.util.spec_from_file_location('gate_engine_v4', path)
gate_engine_v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate_engine_v4)

print('--- RÉVÉLATION DES VARIABLES INTERNES ---')
# On inspecte les variables réelles
for name in dir(gate_engine_v4):
    if not name.startswith('_'): # On ignore les trucs système
        item = getattr(gate_engine_v4, name)
        if not callable(item):
            print(f'VARIABLE DÉTECTÉE: {name} | Valeur: {item}')

