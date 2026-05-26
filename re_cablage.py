
import os
import shutil

# Mapping nom de dossier -> mots-clés dans le nom du fichier
mapping = {
    'contrats': ['contract', 'gencoin_ledger', 'gencoin_debt'],
    'modules_agents': ['agent_', 'memory_governor', 'world_action'],
    'specs': ['spec', 'manifest', 'audit']
}

periphery = 'periphery'
for file in os.listdir(periphery):
    if file.endswith('.py'):
        # On essaie de trier le fichier
        for folder, keywords in mapping.items():
            if any(k in file.lower() for k in keywords):
                src = os.path.join(periphery, file)
                dst = os.path.join(periphery, folder, file)
                shutil.move(src, dst)
                print(f'Déplacé: {file} -> {folder}/')

