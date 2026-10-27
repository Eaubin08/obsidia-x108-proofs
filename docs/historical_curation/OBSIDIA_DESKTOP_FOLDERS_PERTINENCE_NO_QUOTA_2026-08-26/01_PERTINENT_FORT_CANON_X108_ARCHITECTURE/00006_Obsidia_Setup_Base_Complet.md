# Obsidia_Setup_Base_Complet.docx

Source: `C:\Users\User\Desktop\BUREAU_OBSIDIA_2026\5_ARCHIVES_ZIP\C_Corpus_Doctrine_Structure\Nouveau dossier (4)\dossier complet master\ARCHIVE_FRACTALE_part2\Obsidia_Setup_Base_Complet.docx`

SHA256: `86d30caa1337de558f08ede263437fe54c00346fc9a10be4aa37c6db7e73d264`

TruthScore: 6

Status: LOW_SIGNAL

Hits: AVDR:1, ROM:3, PATH-:ARCHIVE_FRACTALE, PATH-:Nouveau dossier

---

📘 Guide Ultra Clair – Setup de Base Obsidia Hackathon

1. Objectif

Ce guide t’aide à préparer le setup minimum d’Obsidia sur ton disque dur externe :
- Télécharger et organiser tous les outils
- Installer Python et les librairies
- Préparer les modules AGI
- Lancer le projet en local le jour J
- Mettre ton projet sur GitHub

2. Outils à Télécharger

Télécharge ces fichiers et place-les dans `/01_Preparation/Dependencies/` sur ton disque dur :

• Python 3.10.12 : https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe

• Graphviz : https://graphviz.org/download/

• Git : https://git-scm.com/downloads

• Visual Studio Code (optionnel) : https://code.visualstudio.com/

3. Librairies Python de base

Tu as un fichier `requirements_obsidia.txt` dans ton dossier. Voici comment télécharger les librairies en avance :

Sur ton PC actuel (avec Internet) :

pip download -r requirements_obsidia.txt -d 01_Preparation/Dependencies

Ensuite tu les mets sur ton disque dur externe dans `/Dependencies/`.

Le jour J (sur le PC cible) :

1. Installe Python avec le fichier `.exe` téléchargé

2. Crée un environnement :

python -m venv obsidia_env

3. Active-le :

obsidia_env\Scripts\activate.bat

4. Installe les librairies offline :

pip install --no-index --find-links=01_Preparation/Dependencies -r 01_Preparation/requirements_obsidia.txt

4. Préparer les Modules AGI

Tu peux préparer les fichiers maintenant (même si tu ne les exécutes que plus tard).

Place les bons fichiers dans ces dossiers :

• Agents : `kai_master.yaml`, `echo_symbolic.yaml`...

• Prompts : `prompt_tri_obsidia_final_v3.txt`, `prompt_pitch_structure.md`...

• Algo : `proto_OBAN_lock.py`, `algo_AVDR_loop.py`...

• Scripts_Demo : `streamlit_obsidia_app.py`, `auto_tri_fichiers.py`...

5. Ordre Chronologique

1. Télécharger Python, Graphviz, Git

2. Télécharger les librairies avec pip (sur ton PC actuel)

3. Créer la structure de dossiers

4. Copier les fichiers AGI dans les bons dossiers

5. Installer Python sur le PC cible

6. Créer et activer l’environnement

7. Installer les librairies offline

8. Lancer le projet :

streamlit run 01_Preparation/Modules_Obsidia/Scripts_Demo/streamlit_obsidia_app.py

6. Uploader ton projet sur GitHub

1. Crée un repo sur https://github.com (ex: obsidia-hackathon)

2. Ouvre Git Bash ou Terminal dans le dossier `/GitHub_Local/`

3. Tape les commandes suivantes :

git init

git add .

git commit -m "Initial commit Hackathon"

git branch -M main

git remote add origin https://github.com/TON_NOM/obsidia-hackathon.git

git push -u origin main

7. Et ensuite ?

• Préparer les visuels (MindMap, schema)
• Faire une vidéo de démo (ou capture d’écran)
• Remplir le README du repo
• Ajouter les derniers fichiers le jour J
