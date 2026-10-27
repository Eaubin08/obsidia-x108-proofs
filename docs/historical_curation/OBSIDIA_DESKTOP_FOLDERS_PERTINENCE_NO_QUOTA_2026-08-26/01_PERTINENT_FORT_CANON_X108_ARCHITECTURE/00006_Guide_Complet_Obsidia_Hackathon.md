# Guide_Complet_Obsidia_Hackathon.docx

Source: `C:\Users\User\Desktop\dossier complet master\ARCHIVE_FRACTALE_part1\Guide_Complet_Obsidia_Hackathon.docx`

SHA256: `b540fa0d31802a186824e0b246390db25b596a10667278b1e2bd883b8f43e7e9`

TruthScore: 6

Status: LOW_SIGNAL

Hits: ROM:3, PATH-:ARCHIVE_FRACTALE

---

📘 Guide Complet – Préparation & Déploiement Obsidia Hackathon

1. Objectif

Ce guide t’explique comment préparer ton dossier Obsidia Hackathon de A à Z :
- Installer les outils nécessaires
- Remplir les bons dossiers
- Lancer le projet localement
- Uploader sur GitHub proprement pour le jury

2. Outils à Télécharger

Télécharge et place ces fichiers dans le dossier `/01_Preparation/Dependencies/` :

• Python 3.10.12 : https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe

• Graphviz : https://graphviz.org/download/

• Git : https://git-scm.com/downloads

• Visual Studio Code (optionnel) : https://code.visualstudio.com/

3. Installation sur ton nouveau PC

1. Lance l’installeur de Python et coche “Add to PATH”.

2. Ouvre le terminal (cmd ou PowerShell) et tape :

python -m venv obsidia_env

3. Active l’environnement :

obsidia_env\Scripts\activate.bat

4. Installe les dépendances OFFLINE :

pip install --no-index --find-links=01_Preparation/Dependencies -r 01_Preparation/requirements_obsidia.txt

4. Arborescence du projet

Voici les dossiers que tu dois remplir :

• Modules_Obsidia/Agents → fichiers .yaml pour les agents IA

• Modules_Obsidia/Prompts → prompts.txt ou .md

• Modules_Obsidia/Algo → fichiers .py pour les protocoles

• Modules_Obsidia/Scripts_Demo → interface et outils

• Assets → visuels, schémas

5. Lancer le projet localement

Lance le terminal dans le dossier racine et tape :

streamlit run 01_Preparation/Modules_Obsidia/Scripts_Demo/streamlit_obsidia_app.py

6. Déploiement sur GitHub

1. Va sur github.com et crée un nouveau repo public (ex: obsidia-hackathon).

2. Copie le contenu de `/GitHub_Local/` dans un nouveau dossier vide sur ton ordi.

3. Ouvre ce dossier avec Git Bash ou VSCode Terminal.

4. Tape ces commandes :

git init

git add .

git commit -m "Initial commit Hackathon"

git branch -M main

git remote add origin https://github.com/TON_NOM/obsidia-hackathon.git

git push -u origin main

7. Ce qu’il te restera à faire

• Ajouter ton README complet avec instructions et visuels
• Ajouter une capture ou vidéo de démo
• Mettre les agents et prompts réels
• Répéter la démo en local
