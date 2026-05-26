
import os

print('--- SCAN DE LOCALISATION DES 261 FICHIERS ---')
found_files = []
for root, _, files in os.walk(r'C:\Users\User'): # Scan depuis la racine utilisateur
    if 'pepites' in root.lower() or 'engine' in root.lower() or 'specs' in root.lower():
        for file in files:
            if file.endswith('.py'):
                found_files.append(os.path.join(root, file))

print(f'Nombre total de fichiers .py trouvés: {len(found_files)}')
for f in found_files[:20]: # On affiche les 20 premiers pour voir le chemin
    print(f'Trouvé: {f}')

