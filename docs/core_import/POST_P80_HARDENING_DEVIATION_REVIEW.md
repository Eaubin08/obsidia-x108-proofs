# Post-P80 Hardening — Deviation Review

**Audit ID :** POST_P80_HARDENING_DEVIATION_REVIEW  
**Branch :** `post-p80-hardening-deviation-review`  
**Mode :** AUDIT_ONLY  
**Date :** 2026-06-09  
**Verdict :** `POST_P80_HARDENING_DEVIATION_REVIEW_READY`

---

## Périmètre audité

| Fichier / Répertoire | Rôle |
|---|---|
| `scripts/check_forbidden_content.py` | Script de détection — whitelist modifiée |
| `.gitignore` | Entrée PROOFKIT_REPORT.json supprimée |
| `.github/workflows/secret-scan.yml` | Nouveau workflow CI secret scan |
| `docs/security/*` | Plans de rotation et hardening |
| `docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.*` | Rapport post-P80 |

---

## Q1 — La whitelist check_forbidden_content.py est-elle trop large ?

**Verdict : NON_TOO_BROAD**

Trois entrées ajoutées à `ALLOWED_PATH_FRAGMENTS` :

| Entrée | Portée | Fichiers actuels couverts | Justification |
|---|---|---|---|
| `"docs/security/"` | Tous les fichiers de docs/security/ avec "secret" dans le nom | 3 fichiers (plans de rotation/hardening) | Documentation technique uniquement — pas d'env/config |
| `".github/workflows/"` | Tous les fichiers de .github/workflows/ avec "secret" dans le nom | 1 fichier (secret-scan.yml) | CI workflow — contenu scanné par TruffleHog/Gitleaks |
| `"docs/core_import/POST_P80_SECRET_ROTATION"` | Fragment narrow — 2 fichiers seulement | JSON + MD post-P80 | Très étroit — aucun risque d'élargissement involontaire |

**Point clé :** `check_forbidden_content.py` ne scanne **jamais** le contenu des fichiers — uniquement les noms. La whitelist ne bypass donc que la détection par nom, pas par contenu. Le contenu est couvert par TruffleHog + Gitleaks en CI.

**Risque résiduel :** `"docs/security/"` est la plus large des trois entrées. Si un fichier avec "token" ou "credential" dans son nom était ajouté dans docs/security/, le script ne le flaguerait pas. Mitigé : CI scanne les contenus + CODEOWNERS protège docs/core_import/.

---

## Q2 — `docs/security/` peut-il cacher un vrai secret sans être détecté ?

**Verdict : RISK_CONTAINED**

Scan de contenu effectué sur tous les fichiers de `docs/security/` :

| Fichier | Patterns dangereux | Résultat |
|---|---|---|
| `BRANCH_PROTECTION_POLICY.md` | Aucun | OK |
| `GITHUB_SECURITY_AUDIT.md` | Aucun | OK |
| `POST_P80_PUBLICATION_HARDENING_PLAN.md` | Aucun | OK |
| `PRE_PUBLICATION_SECURITY_CHECKLIST.md` | Aucun | OK |
| `POST_P80_SECRET_ROTATION_PLAN.md` | WARN (faux positif) | OK — voir détail |

**Détail WARN L58 de POST_P80_SECRET_ROTATION_PLAN.md :**
```
# "next_action": "Set $env:NEO4J_PASSWORD='REDACTED_SEE_ENV_FILE'"
```
Pattern `NEO4J_PASSWORD=...` déclenché mais valeur = `'REDACTED_SEE_ENV_FILE'` — commentaire de documentation montrant la syntaxe PowerShell avec un placeholder explicite. Aucun secret réel.

**Garantie complémentaire :** TruffleHog (`--only-verified`) et Gitleaks scannent le contenu de tous les fichiers commités, y compris docs/security/.

---

## Q3 — `.github/workflows/` peut-il cacher un vrai secret sans être détecté ?

**Verdict : RISK_CONTAINED**

Analyse de `.github/workflows/secret-scan.yml` :
- Aucun secret hardcodé
- `${{ secrets.GITHUB_TOKEN }}` : référence à un secret GitHub géré par la plateforme (non committé, non lisible dans les logs)
- `fetch-depth: 0` : scan complet de l'historique git
- TruffleHog et Gitleaks sont eux-mêmes déclenchés sur le contenu des fichiers pushés, y compris les workflows

**Garantie :** GitHub Actions ne permet pas d'exfiltrer un secret via un workflow committé sans qu'il soit explicitement référencé dans les logs.

---

## Q4 — `docs/core_import/POST_P80_SECRET_ROTATION*` est-il sûr à whitelister ?

**Verdict : SAFE_TO_WHITELIST**

Fragment étroit : `"docs/core_import/POST_P80_SECRET_ROTATION"` — uniquement 2 fichiers correspondants :
- `POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json`
- `POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.md`

Contenu JSON vérifié :
- `"secret_value_printed": false`
- `"publication_decision": "STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY"`
- Aucun pattern `bolt+s://`, `NEO4J_PASSWORD=<valeur>`, `password=<valeur>` — confirmé par scan

---

## Q5 — `.gitignore` protège-t-il bien PROOFKIT_REPORT.json ?

**Verdict : GITIGNORE_CONSISTENT — NOTE_ON_TRACKING_STATE**

| Aspect | Avant post-P80 | Après post-P80 |
|---|---|---|
| Entrée dans .gitignore | Présente (`proofs/PROOFKIT_REPORT.json`) | Supprimée |
| Statut git actuel | Fichier ignoré (gitignored) | Fichier non tracké (`??`) |
| Contenu | Sortie de verify_all.py — uniquement métadonnées de preuves | Idem |
| Risque secret | AUCUN — pas de données sensibles | AUCUN |

**Note sur l'état :** Le commentaire dans .gitignore indique le fichier comme "intentionnellement tracké" mais `git ls-files proofs/PROOFKIT_REPORT.json` retourne vide sur cette branche — le fichier est actuellement **non tracké** (untracked). La suppression de l'entrée gitignore est correcte (git peut maintenant le voir), mais le fichier n'a pas encore été commité. Aucune implication sécuritaire — PROOFKIT_REPORT.json ne contient que des métadonnées de preuves (hashes, comptages).

**Action recommandée (post-audit) :** Mettre à jour le commentaire gitignore de "intentionnellement tracké" à "eligible à tracking" pour refléter l'état réel.

---

## Q6 — NEO4J_PASSWORD reste-t-il documenté comme blocker externe ?

**Verdict : CONFIRMED_BLOCKER_DOCUMENTED**

Chaîne de documentation active :
- `docs/security/POST_P80_SECRET_ROTATION_PLAN.md` → PUBLICATION_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY
- `docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json` → `"secret_rotation_required": true`
- `docs/core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json` → SEC-1 `"resolved": false`
- `docs/core_import/P80_FULL_REGRESSION_FREEZE.json` → `"secret_rotation_required": true`

La valeur du secret n'est **jamais affichée** — `SECRET_VALUE_REDACTED` dans toutes les occurrences.

---

## Q7 — La publication reste-t-elle bloquée ?

**Verdict : PUBLICATION_STILL_BLOCKED**

| Rapport | publication_decision |
|---|---|
| P79 | `SECURITY_AUDIT_INDEXED_NO_PUBLICATION` |
| P80 | `PUBLIC_RELEASE_BLOCKED` |
| Post-P80 | `STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY` |
| Post-P80 Deviation Review | `STILL_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY` |

Cohérence confirmée sur toute la chaîne P79 → post-P80 → review.

---

## Résumé des findings

| ID | Question | Verdict | Sévérité |
|---|---|---|---|
| DEV-1 | Whitelist trop large ? | NON_TOO_BROAD | INFO |
| DEV-2 | docs/security/ cache secret ? | RISK_CONTAINED | INFO |
| DEV-3 | .github/workflows/ cache secret ? | RISK_CONTAINED | INFO |
| DEV-4 | POST_P80_SECRET_ROTATION whitelist sûr ? | SAFE_TO_WHITELIST | INFO |
| DEV-5 | .gitignore PROOFKIT protège bien ? | GITIGNORE_CONSISTENT | NOTE |
| DEV-6 | NEO4J_PASSWORD documenté blocker ? | CONFIRMED_BLOCKER_DOCUMENTED | OK |
| DEV-7 | Publication bloquée ? | PUBLICATION_STILL_BLOCKED | OK |

**Sévérité maximale détectée : NOTE** (aucun blocker nouveau, aucune regression sécurité)

---

## Recommandation optionnelle (hors scope palier)

Optionnellement, `"docs/security/"` pourrait être remplacé par des entrées de fichiers individuels pour réduire la portée de la whitelist :
```python
"docs/security/POST_P80_SECRET_ROTATION_PLAN.md",
"docs/security/POST_P80_PUBLICATION_HARDENING_PLAN.md",
"docs/security/BRANCH_PROTECTION_POLICY.md",
"docs/security/GITHUB_SECURITY_AUDIT.md",
"docs/security/PRE_PUBLICATION_SECURITY_CHECKLIST.md",
```
Décision : KX108_ONLY — non implémenté dans ce palier (AUDIT_ONLY).

---

> Rapport JSON : `docs/core_import/POST_P80_HARDENING_DEVIATION_REVIEW.json`
