# P80 — Publication Blockers

**Généré :** P80  
**Date :** 2026-06-09  
**Décision :** `PUBLIC_RELEASE_BLOCKED`

---

> **Ces blockers doivent être résolus AVANT toute publication GitHub publique.**  
> **Les secrets ne sont jamais affichés dans ce document.**

---

## Blockers par priorité

### HIGH — Bloquants immédiats

| ID | Blocker | Fichier concerné | Action |
|---|---|---|---|
| SEC-1 | **SECRET_ROTATION** | `docs/runtime/archive/.../BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md` | Changer mot de passe NEO4J référencé — `SECRET_VALUE_REDACTED` |
| SEC-4 | **Branch protection** | GitHub Settings | Configurer : PR review obligatoire, CI obligatoire, no force push |
| SEC-5 | **Secret scan CI** | `.github/workflows/` | Ajouter trufflehog ou gitleaks |
| PFA-9 | **Gitignore DO_NOT_PUBLISH** | `.gitignore` | Vérifier couverture complète zones DO_NOT_PUBLISH P78 |

### MEDIUM — À résoudre avant publication

| ID | Blocker | Action |
|---|---|---|
| SEC-2 | CODEOWNERS absent | Créer `.github/CODEOWNERS` — protéger sigma/, proofs/, connectors/ |
| SEC-3 | dependabot absent | Créer `.github/dependabot.yml` |
| PFA-7 | node_modules | `git ls-files apps/obsidia-workbench/node_modules/` — supprimer si commité |

### LOW — À traiter

| ID | Blocker | Action |
|---|---|---|
| SEC-6 | PROOFKIT_REPORT.json gitignore | Résoudre inconsistance : untrack OU retirer entrée gitignore |
| PFA-8 | requirements.txt racine absent | Créer avec pins Python |

---

## Zones DO_NOT_PUBLISH confirmées

| Zone | Raison |
|---|---|
| `sigma/` | Runtime souverain — PROTÉGÉ P77 |
| `runtime_wiring/` | Wiring interne — PROTÉGÉ P77 |
| `apps/obsidia_api/` | API interne — PROTÉGÉ P77 |
| `connectors/` | BLOCK_CONNECTOR_RUN P70 + P77 |
| `audit/world_action_bus.jsonl` | Données runtime — PROTÉGÉ P77 |
| `periphery/` | 3278 fichiers propriétaires |
| `docs/gencoin/` + `specs/10_*` | Token non émis — review légale |
| `docs/runtime/` | Archives terrain avec chemins locaux |
| `_source_packs/` | Source packs locaux non canonisés |
| `_tmp_core_import/` | Import temporaire |
| `_freezes/` | Archives lourdes |
| `.local_audits/` | Audits locaux |

---

**Après résolution de tous les blockers HIGH + MEDIUM, re-exécuter :**
```bash
python proofs/verify_all.py
python scripts/check_forbidden_content.py
python scripts/verify_recursive_manifest.py
pytest tests/test_p72_*.py tests/test_p73_*.py ... tests/test_p80_*.py -q
```

Puis ouvrir une review de publication formelle.
