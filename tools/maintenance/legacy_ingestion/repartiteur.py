
import os
import shutil

# mapping [dossier_cible] = [mots_clés_dans_nom_fichier]
mapping = {
    'engine_gates': ['gate', 'verdict', 'engine'],
    'specs': ['spec', 'audit', 'manifest'],
    'modules_agents': ['agent', 'runner', 'adapter'],
    'gardiens_fond': ['guard', 'provenance', 'validation'],
    'contrats': ['contract', 'ledger', 'debt']
}

base = 'periphery'
for file in os.listdir(base):
    if file.endswith('.py') and file != '__init__.py':
        moved = False
        for folder, keywords in mapping.items():
            if any(k in file.lower() for k in keywords):
                src = os.path.join(base, file)
                dst = os.path.join(base, folder, file)
                # Création dossier si besoin
                if not os.path.exists(os.path.join(base, folder)):
                    os.makedirs(os.path.join(base, folder))
                shutil.move(src, dst)
                print(f'Déplacé: {file} -> {folder}/')
                moved = True
                break

