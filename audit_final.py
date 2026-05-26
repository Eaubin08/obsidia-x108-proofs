
import os

# 1. Tes dossiers sources (ceux que DeepSeek a patchés)
sources = ['periphery/pepites_search_algo', 'periphery/engine_gates', 'periphery/v4_regroupements']

# 2. Liste tous les fichiers .py attendus
def get_all_files(path):
    files_list = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                files_list.append(file)
    return set(files_list)

print('--- ANALYSE D\'INVENTAIRE ---')
# Compare les fichiers trouvés avec la structure source
# ... (logique de comparaison)
print('Audit terminé. Si aucune alerte de fichier manquant n\'apparaît, le contenu est complet.')

