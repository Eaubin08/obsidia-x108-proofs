# Obsidia_Guide_Chemins_Exemples__4586.docx

Source: `C:\Users\User\Desktop\obsi aleger\OBSIDIA_CLASSE\_DOUBLONS_MIS_DE_COTE\1_Agents-Memoire-IA-Architecture\Obsidia_Guide_Chemins_Exemples__4586.docx`

SHA256: `213f270e1030bf5871f0f5c689cbd99461b1d40a3feb6259a4f5a6136fac5324`

TruthScore: 31

Status: WEAK_SIGNAL

Hits: AVDR:2, ROM:5, PATH-:_DOUBLONS_MIS_DE_COTE

---

📘 Obsidia Hackathon – Guide Complet avec Chemins + Exemples

Ce guide t’explique comment utiliser la structure du dossier `Obsidia_Hackathon_FULL_STRUCTURE_OK.zip`, et ce que tu dois y mettre dans chaque sous-dossier. Chaque exemple est accompagné d’explications simples.

1. 📁 01_Preparation/

→ Dependencies/

Ce dossier contient tout ce que tu dois télécharger à l’avance :
- `python-3.10.12.exe` → installation Python
- `graphviz-setup.exe` → pour générer des schémas
- Tous les fichiers `.whl` ou `.tar.gz` de tes librairies Python
- Option : `git-setup.exe`, `vscode.exe`

→ Modules_Obsidia/

▸ Agents/

Ce dossier doit contenir tous les fichiers `.yaml` qui définissent tes agents :
- `kai_master.yaml` → agent principal de gestion
- `echo_symbolic.yaml` → agent de reformulation symbolique
- `tri_ephemere.yaml` → agent temporaire pour classification automatique

▸ Prompts/

Fichiers `.txt` ou `.md` contenant des instructions prêtes à être utilisées dans les démos ou tests :
- `prompt_tri_obsidia_final_v3.txt` → prompt de tri logique
- `prompt_pitch_structure.md` → prompt qui génère un pitch structuré à partir d’un bloc d’idées

▸ Algo/

Fichiers `.py` qui contiennent les boucles, inférences ou protocoles :
- `proto_OBAN_lock.py` → exemple de protocole de raisonnement bloquant
- `algo_AVDR_loop.py` → mini moteur de décision AVDR

▸ Scripts_Demo/

Scripts que tu pourras lancer avec `streamlit run` ou autre pour ta démo :
- `streamlit_obsidia_app.py` → lance l’interface IA Streamlit
- `auto_tri_fichiers.py` → trie les fichiers texte automatiquement

→ Assets/

▸ Schemas/

Exemples de fichiers :
- `architecture_global.png`
- `obsidia_map_v1.svg`

▸ Visuels/

Illustrations ou captures :
- `mindmap_interactive.png`
- `interface_demo_obsidia.png`

2. 📁 02_Execution/

Contient un fichier `README_execution.md` où tu décris exactement :
- Comment on lance le projet
- Dans quel ordre activer les agents ou scripts

3. 📁 03_Rendu_Final/

▸ Slides/

Contiendra ton pitch final en PDF :
- `obsidia_hackathon_pitch.pdf`

▸ Video/

Ta démo filmée, ou une séquence d’exemple si live impossible :
- `demo_obsidia_capture.mp4`

▸ Docs/

- `README_final.md` → résumé complet du projet pour le jury
- `charte_ethique.md` → les principes et règles symboliques d’Obsidia (facultatif mais puissant)

4. 📁 GitHub_Local/

Ce dossier te permet de préparer ton dépôt GitHub à l’avance.
Tu peux y mettre :
- `README.md` → explication publique
- `.gitignore` → pour ne pas pousser certains fichiers privés
