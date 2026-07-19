# GitHub Security Audit — Obsidia X-108

**Généré :** P79 — RSSI Evidence Pack and GitHub Security Audit  
**Date :** 2026-06-09  
**Mode :** AUDIT_ONLY — aucune action exécutée

---

## Résumé

| Élément | Statut |
|---|---|
| SECURITY.md | PRÉSENT |
| CI proof | PRÉSENT (verify-proofs.yml) |
| CI periphery | PRÉSENT (x108-periphery-ci.yml) |
| .gitignore | PRÉSENT (complet) |
| .env.example | PRÉSENT (valeurs vides) |
| CODEOWNERS | ABSENT |
| dependabot.yml | ABSENT |
| Branch protection | NON DOCUMENTÉ |
| Secret scanning CI | ABSENT |
| Dependency audit CI | ABSENT |
| requirements.txt racine | ABSENT |
| Secret hardcodé réel | 1 DÉTECTÉ (zone ARCHIVE) |
| Chemins locaux exposés | 66 fichiers (zones ARCHIVE/DO_NOT_PUBLISH) |

---

## CI Présent

### `.github/workflows/verify-proofs.yml`

Couvre :
- `verify-python-strict` — `python proofs/verify_all.py` bloquant
- `verify-lean` — `lake build` sur `proofs/lean/`
- `verify-sigma-and-qa` — sigma tests + RFC3161 cross-platform
- `verify-tla` — TLC sur `formal/tla/X108_MC.tla`

**Évaluation :** CI proof complet et bien structuré.

### `.github/workflows/x108-periphery-ci.yml`

Couvre :
- `python -m compileall periphery -q`
- `python scripts/generate_recursive_manifest.py`
- `python -m pytest tests/ -q --tb=short`
- Protected files check via `git diff --exit-code` sur sigma/guard.py, contracts.py, proofs/lean/, merkle_seal.json
- `python scripts/check_forbidden_content.py`
- Manifest verify post-test

**Évaluation :** CI periphery solide avec protected files check.

---

## Gaps Sécurité (à adresser avant publication)

### 1. CODEOWNERS manquant

**Impact :** Sans CODEOWNERS, n'importe qui peut merger des changements sur sigma/, proofs/, connectors/ sans review obligatoire.

**Action :** Créer `.github/CODEOWNERS` :
```
sigma/ @obsidia-kernel-team
proofs/ @obsidia-proof-team
connectors/ @obsidia-kernel-team
apps/obsidia_api/ @obsidia-api-team
```

### 2. dependabot.yml manquant

**Impact :** Pas de mise à jour automatique des dépendances GitHub Actions et Python.

**Action :** Créer `.github/dependabot.yml` :
```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### 3. Branch protection non documentée

**Impact :** Sans branch protection GitHub, la branche `main` peut être force-pushée.

**Action :** Configurer via GitHub Settings → Branches :
- Require pull request reviews before merging
- Require status checks to pass (CI must pass)
- Restrict force pushes
- Restrict deletions

### 4. Secret scanning CI absent

**Impact :** Commits futurs pourraient introduire des secrets sans détection.

**Action :** Ajouter dans un workflow CI :
```yaml
- name: Secret scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: main
```

### 5. Dependency audit CI absent

**Impact :** Vulnérabilités dans dépendances Python non détectées automatiquement.

**Action :** Ajouter dans CI si applicable :
```yaml
- name: pip-audit
  run: pip-audit -r requirements.txt
```

---

## .gitignore — Analyse

Le `.gitignore` est complet et bien structuré :
- `.env` et `.env.*` exclus (sauf `.env.example`)
- `node_modules/` exclu
- `_sessions/`, `_local_audits/` exclus
- Archives (*.zip, *.7z, *.tar, *.gz) exclues
- `proofs/PROOFKIT_REPORT.json` listé — **INCONSISTANCE** : fichier présent dans repo

**Action requise :** Vérifier si `proofs/PROOFKIT_REPORT.json` est commité (`git ls-files proofs/PROOFKIT_REPORT.json`). Si oui, décider :
- Option A : Retirer l'entrée gitignore et garder le fichier commité
- Option B : `git rm --cached proofs/PROOFKIT_REPORT.json` et re-générer via CI

---

## Secret Scan

| Fichier | Type | Valeur | Action |
|---|---|---|---|
| `docs/runtime/archive/.../BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md` | NEO4J_PASSWORD | `SECRET_VALUE_REDACTED` | **REQUIRES_SECRET_ROTATION** |
| `scripts/brody_terminal_chat.py` | NEO4J_PASSWORD | `SECRET_VALUE_REDACTED` (template ?) | REQUIRES_REVIEW |
| `proofs/V18_3_1/.../PUBLIC_DEPLOY.md` | MINIO_ROOT_PASSWORD | `SECRET_VALUE_REDACTED` (template) | REQUIRES_REVIEW |

**Note :** Tous les fichiers avec secret potentiel réel sont dans des zones classées ARCHIVE_ONLY ou DO_NOT_PUBLISH per P78. Aucun n'est dans la surface publique safe identifiée en P78.

---

**Verdict :** Audit GitHub sécurité indexé. 5 gaps à adresser. CI présent et fonctionnel. Surface publique safe ne contient pas de secrets.
