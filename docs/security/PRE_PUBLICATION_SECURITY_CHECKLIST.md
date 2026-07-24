# Pre-Publication Security Checklist — Obsidia X-108

**Généré :** P79  
**Date :** 2026-06-09  
**Usage :** Compléter avant toute publication GitHub publique ou PR publique

---

## Checklist obligatoire

### Secrets

- [ ] **SECRET_ROTATION** — Changer le NEO4J_PASSWORD référencé dans :
  `docs/runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md`
  _(fichier en zone DO_NOT_PUBLISH — vérifier qu'il ne sera pas pushé)_

- [ ] **Vérifier** que `scripts/brody_terminal_chat.py` n'a que des placeholders, pas de vraies valeurs

- [ ] **Confirmer** `proofs/V18_3_1/.../PUBLIC_DEPLOY.md` MINIO_ROOT_PASSWORD = template seulement

### Gitignore / fichiers non-tracés

- [ ] **PROOFKIT_REPORT** — Résoudre inconsistance :
  ```
  git ls-files proofs/PROOFKIT_REPORT.json
  ```
  Si commité : décider retirer gitignore entry OU untrack

- [ ] **node_modules** — Vérifier apps/obsidia-workbench/node_modules/ :
  ```
  git ls-files apps/obsidia-workbench/node_modules/ | head -5
  ```
  Si commité : `git rm -r --cached apps/obsidia-workbench/node_modules/`

### GitHub config

- [ ] **CODEOWNERS** — Créer `.github/CODEOWNERS` avec protection sigma/, proofs/, connectors/

- [ ] **dependabot** — Créer `.github/dependabot.yml` pour GitHub Actions

- [ ] **Branch protection** — Configurer via GitHub Settings :
  - Require PR reviews
  - Require CI status checks
  - Restrict force push sur `main`
  - Restrict branch deletion

### CI Security

- [ ] **Secret scanning** — Ajouter trufflehog ou gitleaks dans CI workflow

- [ ] **Dependency audit** — Ajouter pip-audit si requirements.txt créé

### Dépendances

- [ ] **requirements.txt** — Créer à la racine avec pins Python exacts

### Zones DO_NOT_PUBLISH

- [ ] Confirmer que les zones suivantes ne seront PAS dans le push public :
  - `sigma/`
  - `runtime_wiring/`
  - `connectors/`
  - `periphery/`
  - `docs/gencoin/` + `specs/10_VALUE_GENCOIN_JCOIN/`
  - `audit/world_action_bus.jsonl`
  - `docs/runtime/` (chemins locaux + archives)
  - `_source_packs/`
  - `_tmp_core_import/`
  - `_freezes/`

- [ ] Vérifier `.gitignore` couvre bien TOUS les DO_NOT_PUBLISH P78

### Regression tests

- [ ] P80 full regression freeze passé

---

## Validation finale

- [ ] `python proofs/verify_all.py` passe
- [ ] `python scripts/verify_recursive_manifest.py` passe
- [ ] `python scripts/check_forbidden_content.py` passe
- [ ] CI GitHub Actions passe (verify-proofs.yml + x108-periphery-ci.yml)
- [ ] Tous les tests P79 passent : `pytest tests/test_p79_*.py`

---

**Autorité :** P78 DO_NOT_PUBLISH + P77 PROTECTED_FILES + P72 LEAN_PROVEN invariants
