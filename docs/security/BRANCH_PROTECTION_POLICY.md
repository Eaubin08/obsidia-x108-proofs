# Branch Protection Policy — Obsidia X-108

**Généré :** post-P80 Security Hardening  
**Date :** 2026-06-09  
**Mode :** DOCUMENTATION UNIQUEMENT — la configuration se fait via GitHub Settings

---

## Configuration requise avant publication

### Branche : `main`

À configurer via **GitHub Settings → Branches → Branch protection rules** sur `main` :

#### Règles obligatoires

| Règle | Valeur |
|---|---|
| Require a pull request before merging | ✓ ACTIVÉ |
| Required number of approvals | 1 minimum (idéalement 2) |
| Dismiss stale pull request approvals when new commits are pushed | ✓ ACTIVÉ |
| Require review from Code Owners | ✓ ACTIVÉ (requiert CODEOWNERS) |
| Require status checks to pass before merging | ✓ ACTIVÉ |
| Status checks requises | `verify-python-strict`, `verify-lean`, `verify-sigma-and-qa`, `verify-tla`, `trufflehog`, `gitleaks` |
| Require branches to be up to date before merging | ✓ ACTIVÉ |
| Require conversation resolution before merging | ✓ ACTIVÉ |
| Restrict pushes that create matching branches | ✓ ACTIVÉ |
| Allow force pushes | ✗ DÉSACTIVÉ |
| Allow deletions | ✗ DÉSACTIVÉ |

#### Justification

- **Force push interdit** : protège l'historique des commits P56→P80
- **CODEOWNERS requis** : review obligatoire sur sigma/, proofs/, connectors/
- **CI obligatoire** : verify_all.py + secret scan avant tout merge
- **Pas de suppression** : préserve les branches d'audit P56→P80

---

## Branches à protéger

| Branche | Protection | Raison |
|---|---|---|
| `main` | OBLIGATOIRE | Branche de publication |
| `p*-*` | Recommandé | Branches audit paliers |

---

## Zones CODEOWNERS protégées

Voir `.github/CODEOWNERS` — zones nécessitant review :
- `sigma/` → @obsidia-kernel-team
- `runtime_wiring/` → @obsidia-kernel-team
- `connectors/` → @obsidia-kernel-team
- `proofs/lean/` → @obsidia-proof-team
- `proofs/merkle_root.json` → @obsidia-proof-team
- `.github/workflows/` → @obsidia-kernel-team

---

**Autorité :** KX108_ONLY — GuardX108 final.  
**Note :** Ce document est un guide de configuration, pas un outil automatique.
