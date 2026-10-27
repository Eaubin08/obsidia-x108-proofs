
import periphery
import inspect

print('--- AUDIT DES LIENS CÂBLÉS ---')
# On regarde quels modules sont maintenant accessibles via le namespace periphery
for name, obj in inspect.getmembers(periphery):
    if inspect.ismodule(obj):
        print(f'MODULE ACTIF: {name}')

# Test de promotion avec le noyau maintenant 'conscient' de ses liens
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict
context = {f'G{i}': {'status': 'OPEN'} for i in range(1, 6)}
print(f'VERDICT FINAL D\'INTÉGRITÉ: {verdict(context)}')

