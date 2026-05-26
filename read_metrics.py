
from periphery.engine_gates.v4_structure.gate_engine_v4 import verdict

# On injecte un dictionnaire qui force le moteur à solliciter tes pépites mathématiques
test_context = {
    'G1': {'status': 'active', 'mode': 'compute'},
    'G2': {'status': 'ready', 'mode': 'compute'}
}

# Appel du moteur pour forcer l'exécution des métriques
print('--- EXTRACTION DES MÉTRIQUES ---')
result = verdict(test_context)

# On va chercher si le moteur a stocké des résultats dans un buffer interne
# C'est souvent comme ça que tes pépites communiquent leurs résultats
from periphery.engine_gates.v4_structure import gate_engine_v4
if hasattr(gate_engine_v4, 'get_metrics'):
    print(f'MÉTRIQUES ACTIVES: {gate_engine_v4.get_metrics()}')
else:
    print('Le moteur n\'a pas de fonction get_metrics() publique. Cherchons dans les objets du module.')
    print(f'ÉTAT DU VERDICT: {result}')

