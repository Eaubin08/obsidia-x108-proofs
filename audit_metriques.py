
import os
import re

# Liste les fichiers critiques qui contiennent tes métriques (ex: matrices, Lyapunov)
metriques_pattern = re.compile(r'Lyapunov|tensor|matrix|AVDR|sigma|phi')

def extract_signatures(path):
    signatures = {}
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # On cherche la densité des mots-clés mathématiques
                    matches = len(metriques_pattern.findall(content))
                    signatures[file] = matches
    return signatures

# 1. Signature des fichiers originaux (dans ton archive zip extraite)
sig_original = extract_signatures('source_zip_de_reference')
# 2. Signature des fichiers patchés
sig_patched = extract_signatures('periphery')

print('--- ANALYSE COMPARATIVE DES MÉTRIQUES ---')
for name, val in sig_original.items():
    if sig_patched.get(name, 0) != val:
        print(f'ALERTE LISSAGE: {name} | Original: {val} mots-clés | Patché: {sig_patched.get(name, 0)}')

