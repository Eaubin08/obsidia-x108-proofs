
import os

folders = {
    'periphery/pepites_search_algo': 161,
    'periphery/engine_gates': 12,
    'periphery/specs': 40,
    'periphery/modules_agents': 24,
    'periphery/gardiens_fond': 12,
    'periphery/contrats': 12
}

total_found = 0
print(f'{'DOSSIER':<30} | {'ATTENDU':<10} | {'TROUVÉ':<10} | {'ÉTAT':<10}')
for folder, count in folders.items():
    if os.path.exists(folder):
        found = len([f for f in os.listdir(folder) if f.endswith('.py')])
        total_found += found
        status = 'OK' if found >= count else 'MANQUANT'
        print(f'{folder:<30} | {count:<10} | {found:<10} | {status:<10}')
    else:
        print(f'{folder:<30} | {count:<10} | 0 | INTROUVABLE')

print('-' * 70)
print(f'TOTAL GÉNÉRAL : {total_found} / 261 fichiers')

