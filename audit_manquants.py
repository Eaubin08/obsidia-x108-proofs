
import os

# Tes répertoires attendus
expected = {
    'periphery/pepites_search_algo': 161,
    'periphery/engine_gates': 12,
    'periphery/v4_regroupements': 0, # Besoin de tes stats
    'periphery/specs': 40,
    'periphery/modules_agents': 24,
    'periphery/gardiens_fond': 12,
    'periphery/contrats': 12
}

print(f'{'DOSSIER':<30} | {'ATTENDU':<10} | {'TROUVÉ':<10} | {'ÉTAT':<10}')
for folder, count in expected.items():
    if os.path.exists(folder):
        found = len([f for f in os.listdir(folder) if f.endswith('.py')])
        status = 'OK' if found >= count else 'MANQUANT'
        print(f'{folder:<30} | {count:<10} | {found:<10} | {status:<10}')
    else:
        print(f'{folder:<30} | {count:<10} | 0 | INTROUVABLE')

