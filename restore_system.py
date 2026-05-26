
import os
import shutil
import zipfile

# Sources
sources = [
    r'C:\Users\User\Downloads\OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FREEZE_CANDIDATE.zip',
    r'C:\Users\User\Downloads\OBSIDIA_V4_REGROUPEMENTS_V43_SOUS_DOSSIERS.zip'
]
folders = [
    r'C:\Users\User\Downloads\OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL_LIGHT_PATCH',
    r'C:\Users\User\Downloads\OBSIDIA_V4_REGROUPEMENTS_COMPLETS'
]

target = 'periphery'
if not os.path.exists(target): os.makedirs(target)

print('--- DÉBUT DE RESTAURATION ---')

# 1. Extraction des Zips
for zip_path in sources:
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('temp_extract')
            print(f'Extrait: {zip_path}')

# 2. Copie forcée depuis dossiers et extraits vers target
def copy_recursive(src, dst):
    for root, _, files in os.walk(src):
        for file in files:
            s_path = os.path.join(root, file)
            d_path = os.path.join(dst, os.path.relpath(root, src), file)
            os.makedirs(os.path.dirname(d_path), exist_ok=True)
            shutil.copy2(s_path, d_path)

for folder in folders:
    if os.path.exists(folder):
        copy_recursive(folder, target)
        print(f'Importé depuis dossier: {folder}')

print('--- RESTAURATION TERMINÉE ---')

