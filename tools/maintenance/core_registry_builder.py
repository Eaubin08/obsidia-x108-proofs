
import os
import importlib.util

def force_branch_all():
    root_dir = 'periphery'
    total_files = 0
    registry = {}
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py') and '__init__' not in file:
                full_path = os.path.join(root, file)
                module_name = full_path.replace(os.path.sep, '.').replace('.py', '')
                
                # Enregistrement brut dans le registre
                registry[module_name] = full_path
                total_files += 1
                
    # Écriture du registre forcé pour que le kernel les voit
    with open('periphery/core_registry.py', 'w') as f:
        f.write('REGISTRY = ' + str(registry) + '\\n')
        f.write('def get_all(): return REGISTRY.keys()')
    
    print(f'BRANCHEMENT TERMINÉ : {total_files} fichiers indexés.')

force_branch_all()

