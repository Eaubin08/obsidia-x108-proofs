
import os
import re

# Dossier contenant tes agents
agents_dir = r'periphery/agents'
# On remplace l'import erroné
bad_import = 'from ..agent_contracts'
good_import = 'from periphery.agent_contracts'

for file in os.listdir(agents_dir):
    if file.endswith('.py'):
        path = os.path.join(agents_dir, file)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if bad_import in content:
            new_content = content.replace(bad_import, good_import)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Patché: {file}')

