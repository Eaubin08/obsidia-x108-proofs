
import os

periphery_files = set(f for f in os.listdir('periphery') if f.endswith('.py'))
print(f'FICHIERS ACTIFS DANS PERIPHERY: {len(periphery_files)}')

# On liste ce qui manque par rapport à l'attendu global de 261
print('--- ANALYSE DES LIENS MANQUANTS ---')
# Si on avait une liste de référence de 261, on pourrait comparer
# Mais là, on va juste vérifier si les dossiers 'contrats' ou 'modules' sont vides
for folder in ['contrats', 'modules_agents', 'specs']:
    count = len([f for f in os.listdir(os.path.join('periphery', folder)) if f.endswith('.py')])
    print(f'Dossier {folder}: {count} fichiers trouvés.')

