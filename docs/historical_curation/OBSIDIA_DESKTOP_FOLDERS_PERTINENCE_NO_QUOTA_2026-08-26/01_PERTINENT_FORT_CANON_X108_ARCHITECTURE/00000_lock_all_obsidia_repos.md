# lock_all_obsidia_repos.docx

Source: `C:\Users\User\Desktop\Obsidia Master\vision blog suite\lock_all_obsidia_repos.docx`

SHA256: `89e5dd43beb3c761fa299dd9a98d548ab187dae89f7bb0b85815d7e69f50fdd5`

TruthScore: 0

Status: LOW_SIGNAL

Hits: 

---

Obsidia — Verrouillage automatique des repos GitHub

Ce document contient UN script prêt à l’emploi.
But : verrouiller la branche main sur tous les repos Obsidia.

OÙ LE METTRE : n’importe où sur ton PC (PAS dans un repo).
COMMENT L’UTILISER : voir en bas (3 commandes).

Fichier à créer : lock_all_obsidia_repos.sh

#!/bin/bash

echo "🔒 Verrouillage des repos Obsidia..."

lock_repo () {
  REPO=$1
  echo "→ $REPO"

  gh repo edit $REPO --default-branch main

  gh api     -X PUT     repos/$REPO/branches/main/protection     -f required_status_checks=null     -f enforce_admins=true     -f required_pull_request_reviews.required_approving_review_count=1     -f required_pull_request_reviews.require_code_owner_reviews=true     -f required_pull_request_reviews.dismiss_stale_reviews=true     -f required_conversation_resolution=true     -f allow_force_pushes=false     -f allow_deletions=false
}

lock_repo Eaubin08/obsidia-os4-traducteur
lock_repo Eaubin08/obsidia-os3-reverse
lock_repo Eaubin08/obsidia-os2-mcp
lock_repo Eaubin08/obsidia-os0-moteur
lock_repo Eaubin08/obsidia-guard-v1-github
lock_repo Eaubin08/Eaubin08-octg
lock_repo Eaubin08/agentic-commerce-safe-demo-V2-finale-hackathon-
lock_repo Eaubin08/C-Users-User-Desktop-preprint-conscience-Obsidia_Consciousness_Master

echo "✅ Terminé."

Utilisation (3 commandes, fini)

1) Ouvre un terminal (Git Bash / PowerShell / Terminal)
2) Connexion GitHub (une fois) :
   gh auth login
3) Exécution :
   cd <dossier_du_fichier>
   chmod +x lock_all_obsidia_repos.sh
   ./lock_all_obsidia_repos.sh
