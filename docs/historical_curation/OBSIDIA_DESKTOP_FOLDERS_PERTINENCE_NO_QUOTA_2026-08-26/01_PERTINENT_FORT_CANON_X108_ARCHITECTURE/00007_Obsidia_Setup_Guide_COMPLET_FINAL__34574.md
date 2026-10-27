# Obsidia_Setup_Guide_COMPLET_FINAL__34574.docx

Source: `C:\Users\User\Desktop\obsi aleger\OBSIDIA_CLASSE\_DOUBLONS_MIS_DE_COTE\1_Agents-Memoire-IA-Architecture\Obsidia_Setup_Guide_COMPLET_FINAL__34574.docx`

SHA256: `1b21a8b808b11e8f2ac17fa1e7c725030d4dd5f3638f665c809360f5c0371cc8`

TruthScore: 7

Status: LOW_SIGNAL

Hits: ROM:4, PATH-:_DOUBLONS_MIS_DE_COTE

---

📘 Guide Complet – Setup de Base + Structure AGI – Obsidia Hackathon

1. 🎯 Objectif

Ce guide t’aide à préparer le dossier complet pour ton hackathon Raise Your Hack avec Obsidia :
- Télécharger et organiser les outils + librairies
- Préparer les modules AGI à l'avance
- Installer et tester le tout en offline
- Déployer sur GitHub proprement

2. 🧰 Outils à Télécharger (et leur rôle)

• Python 3.10.12 → Langage principal pour les scripts et APIs
  https://www.python.org/ftp/python/3.10.12/python-3.10.12-amd64.exe

• Graphviz → Génération de schémas pour les cartes mentales et les visualisations
  https://graphviz.org/download/

• Git → Permet de créer ton dépôt GitHub
  https://git-scm.com/downloads

• Visual Studio Code (optionnel) → Éditeur de code pour ouvrir tous tes fichiers rapidement
  https://code.visualstudio.com/

3. 🐍 Librairies Python de base (requirements)

Tu peux toutes les pré-télécharger d’un coup :

pip download -r requirements_obsidia.txt -d 01_Preparation/Dependencies

Puis place-les dans ton disque dur ici : `/01_Preparation/Dependencies/`

Librairies principales à comprendre :

• FastAPI → Créer l'API backend rapide

• Streamlit → Créer l'interface visuelle simple pour le test / démo

• uvicorn → Lancer le serveur FastAPI

• llama-cpp-python → Faire tourner Llama localement sans accès à Internet

• openai → Utiliser des modèles type GPT si besoin plus tard

• groq → Connexion à la Groq API (optionnel, partenaire)

• graphviz → Créer des graphes et mindmaps

• pyyaml → Lire les fichiers agents au format YAML

• python-dotenv → Gérer les fichiers .env pour les clés API

4. 📁 Dossiers Modules AGI – À remplir

Tu peux déjà préparer les fichiers dans les dossiers suivants :

🔹 Agents → fichiers `.yaml` (ex : `kai_master.yaml`)
Contenu : rôles cognitifs, fonctions internes, mémoire
Activable : oui, dès le jour J
Préparation autorisée = ✅

🔹 Prompts → `.txt` ou `.md` (ex : `prompt_tri_obsidia.txt`)
Contenu : instructions de tri, résumé, génération
Préparation autorisée = ✅

🔹 Algo → `.py` (ex : `proto_OBAN_lock.py`)
Contenu : boucles logiques, inférences, protocoles
Préparation autorisée = ✅

🔹 Scripts_Demo → `.py` (ex : `streamlit_obsidia_app.py`)
Contenu : démo, interface, moteur
Préparation autorisée = ✅

🔹 Assets → `.png`, `.svg`, `.mermaid` (schémas, visuels)
Contenu : architecture, agents, workflows
Préparation autorisée = ✅

5. 🧭 Ordre Chronologique Complet

• Télécharge Python, Graphviz, Git

• Télécharge les librairies avec pip

• Décompresse le ZIP complet sur ton disque dur

• Copie les fichiers préparés (agents, prompts...) dans les bons dossiers

• Sur le PC du hackathon : installe Python et Graphviz

• Crée l’environnement virtuel : python -m venv obsidia_env

• Active-le : obsidia_env\Scripts\activate.bat

• Installe les dépendances offline avec install_offline.sh ou la commande pip

• Lance ton interface : streamlit run 01_Preparation/Modules_Obsidia/Scripts_Demo/streamlit_obsidia_app.py

6. 🌐 GitHub – Dépôt Officiel pour le Jury

Tu as le droit de préparer ton repo en avance.

1. Va sur github.com → Crée un repo `obsidia-hackathon` (public le temps du jury)

2. Va dans `/GitHub_Local/` et colle ce qu’il doit apparaître :

- README.md
   - structure de ton code (mais pas d’agent secret si confidentiel)
   - visuels, documentation
   - scripts démo si autorisés

3. Dans Git Bash ou terminal :

git init

git add .

git commit -m "Initial commit Hackathon"

git branch -M main

git remote add origin https://github.com/TON_NOM/obsidia-hackathon.git

git push -u origin main

Tu pourras refaire un `git add .` et `git push` le soir même si tu ajoutes des fichiers de dernière minute.

7. ✅ Ce qu’il te restera à faire

• Vérifier que tous tes modules sont prêts à être lancés
• Générer un visuel 16:9 de ton MindMap (ou capture interface)
• Préparer une vidéo (ou au moins une séquence cliquable)
• Ajouter au moins 2-3 agents ou prompts actifs pour montrer le système
