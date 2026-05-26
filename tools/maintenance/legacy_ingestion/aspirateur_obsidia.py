
import os
import shutil

source_dirs = [
    r'C:\Users\User\Downloads\OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1_FINAL_LIGHT_PATCH',
    r'C:\Users\User\Downloads\OBSIDIA_V4_REGROUPEMENTS_COMPLETS'
]
dest_dir = r'C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\periphery'

print('--- DÉBUT DE L\'ASPIRATION TOTALE ---')
count = 0

for source in source_dirs:
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.endswith('.py'):
                src_file = os.path.join(root, file)
                # On copie tout à la racine de periphery pour les rendre visibles
                dst_file = os.path.join(dest_dir, file)
                
                # Gestion des collisions si deux fichiers portent le même nom
                if os.path.exists(dst_file):
                    dst_file = os.path.join(dest_dir, os.path.basename(root) + '_' + file)
                
                shutil.copy2(src_file, dst_file)
                count += 1
                
print(f'ASPIRATION TERMINÉE : {count} fichiers injectés dans periphery/')

