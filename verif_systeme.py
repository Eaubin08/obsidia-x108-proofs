
import os
import periphery.engine_gates.v4_structure.gate_engine_v4 as engine

# 1. On scanne ce que le moteur voit réellement dans periphery/
periphery_files = [f for f in os.listdir('periphery') if f.endswith('.py')]
print(f'FICHIERS DÉTECTÉS DANS PERIPHERY: {len(periphery_files)}')

# 2. Test du verdict avec un contexte élargi
context = {f'G{i}': {'status': 'OPEN'} for i in range(1, 6)}
result = engine.verdict(context)

print(f'VERDICT DU MOTEUR APRÈS INJECTION: {result}')

