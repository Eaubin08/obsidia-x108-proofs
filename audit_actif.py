
import os
import importlib.util
import inspect

def count_symbols(path):
    stats = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py') and '__init__' not in file:
                mod_path = os.path.join(root, file)
                mod_name = file.replace('.py', '')
                try:
                    spec = importlib.util.spec_from_file_location(mod_name, mod_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    # On compte les fonctions et classes réellement présentes
                    members = inspect.getmembers(module, predicate=lambda m: inspect.isfunction(m) or inspect.isclass(m))
                    stats[file] = len([m for m in members if m[0] != '__init__'])
                except:
                    stats[file] = 0 # Erreur ou module vide
    return stats

folders = ['periphery/pepites_search_algo', 'periphery/engine_gates', 'periphery/v4_regroupements']
print(f'{'FICHIER':<40} | {'FONCTIONS/CLASSES ACTIVES':<20}')
for f in folders:
    if os.path.exists(f):
        results = count_symbols(f)
        for name, count in results.items():
            print(f'{name:<40} | {count:<20}')

