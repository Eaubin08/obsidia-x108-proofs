# Post-P80 — Secret Rotation Plan

**Généré :** post-P80 Security Hardening  
**Date :** 2026-06-09  
**Blocker :** SEC-1 — PUBLICATION_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY

---

> **La valeur du secret n'est JAMAIS affichée dans ce document.**  
> **SECRET_VALUE_REDACTED — rotation manuelle externe requise.**

---

## Contexte

En P79, un secret potentiel de type `NEO4J_PASSWORD` a été détecté dans :

```
docs/runtime/archive/phase10_12_legacy_untracked_20260527/
  BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md
```

Ce fichier est classé :
- **`KEEP_ARCHIVE_ONLY`** (P78) — `docs/runtime/` zone archive
- **`DO_NOT_PUBLISH`** (P78) — exclus de toute publication publique
- **`REDACT_BEFORE_PUBLIC`** (P79) — à redacter si jamais envisagé de publier

Le fichier est dans un répertoire d'archive locale et ne fait PAS partie de la surface public safe.

---

## Qui doit agir

L'équipe responsable du système Neo4j utilisé dans l'environnement Obsidia local.

---

## Étapes de rotation (manuelle, externe à ce repo)

1. **Identifier** l'instance Neo4j concernée (locale ou distante)
2. **Changer** le mot de passe via la console Neo4j
3. **Mettre à jour** toutes les configurations qui utilisent l'ancien mot de passe (`.env` local, scripts de connexion)
4. **Vérifier** la connexion après rotation
5. **Documenter** la rotation (sans noter le nouveau mot de passe ici)

---

## Actions dans ce repo (post-rotation)

Une fois la rotation externe effectuée :

### Option A — Redacter l'archive (recommandée si publication envisagée)

```bash
# Ouvrir le fichier archive et remplacer la valeur par REDACTED
# docs/runtime/archive/.../BRODY_PHASE12E4_A2_DOMAIN_RACCORD_AUDIT_20260527.md
# Remplacer la ligne contenant le mot de passe par :
# "next_action": "Set $env:NEO4J_PASSWORD='REDACTED_SEE_ENV_FILE'"
```

**Note :** Cette redaction doit être faite avec validation explicite — pas dans ce palier.

### Option B — Confirmer le DO_NOT_PUBLISH (si publication non envisagée)

Documenter que `docs/runtime/` restera DO_NOT_PUBLISH et ne sera jamais pushé. Aucune modification du fichier requise.

---

## Statut au moment du freeze P80

| Élément | Statut |
|---|---|
| Secret détecté | OUI — NEO4J_PASSWORD `SECRET_VALUE_REDACTED` |
| Fichier en zone DO_NOT_PUBLISH | OUI |
| Fichier dans gitignore | NON (docs/runtime/ non gitignored) |
| Impact sur freeze local | AUCUN |
| Impact sur publication GitHub | BLOCKER — rotation requise |

---

## Vérification post-rotation

Après rotation et redaction (si Option A) :

```bash
python scripts/check_forbidden_content.py
python proofs/verify_all.py
# Puis: re-run secret scan CI (trufflehog + gitleaks)
```

---

**Décision :** `PUBLICATION_BLOCKED_UNTIL_SECRET_ROTATED_EXTERNALLY`  
**Freeze local :** NON BLOQUÉ — local freeze reste `LOCAL_FREEZE_APPROVED_WITH_SECURITY_NOTE`
