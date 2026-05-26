
import os

# Fichiers que le moteur cherche à la racine, mais qui sont dans des sous-dossiers
# { 'nom_attendu': 'chemin_reel_relatif' }
proxies = {
    'data_gate.py': 'engine_gates/data_gate.py',
    'agent_contracts.py': 'modules_agents/agent_contracts.py',
    'gencoin_debt_model.py': 'contrats/gencoin_debt_model.py'
}

for name, target in proxies.items():
    proxy_path = os.path.join('periphery', name)
    # On crée un fichier qui importe simplement depuis le vrai emplacement
    with open(proxy_path, 'w', encoding='utf-8') as f:
        # Transformation du chemin relatif en module importable
        module_path = target.replace('/', '.').replace('.py', '')
        f.write(f'from periphery.{module_path} import *')
    print(f'Proxy créé: {proxy_path} -> {target}')

