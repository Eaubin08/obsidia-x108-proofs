# NO_PACKAGES_RUNTIME_BOUNDARY
# runtime_contracts/boundaries/NO_PACKAGES_RUNTIME_BOUNDARY.md
# Status: CONTRACT_SKELETON_ONLY

---

## 1. Boundary Statement

```
packages/ = INTERDIT dans ce repo en Plan 3 P0
runtime_contracts/ = documentation contractuelle uniquement
∀ fichier f ∈ runtime_contracts/ : f ≠ code exécutable
∀ fichier f ∈ runtime_contracts/ : extension(f) ∈ {.md, .json}
∀ f : .py ↛ créé pendant Plan 3 P0
∀ f : .ts, .js, .py, .yaml (code) ↛ créé dans runtime_contracts/
```

---

## 2. Applies To

Toute la séquence Plan 3 P0. Toutes les vagues de création de fichiers.

---

## 3. Allowed

- Créer des fichiers `.md` (contrats, boundaries, dry-run, rapports)
- Créer des fichiers `.json` (schemas JSON documentaires)
- Créer des sous-dossiers dans `runtime_contracts/`
- Créer des fichiers de backup dans `_backups/`
- Créer des rapports d'audit dans `_source_discovery/`

---

## 4. Forbidden

```
❌ Créer packages/
❌ Créer des fichiers .py
❌ Créer des fichiers .ts, .js, .mjs
❌ Créer des adapters Python actifs
❌ Créer des executors
❌ Créer des tests exécutables (.py, .test.ts)
❌ Créer des scripts d'installation
❌ Modifier periphery/, apps/, sigma/, connectors/, proofs/, formal/, tests/
```

---

## 5. Raison de l'interdiction packages/

3 fichiers identifiés dans la résolution de collision comme ciblant `packages/` :
- Ces fichiers appartiennent à des packets External Signals qui voudraient aller dans `packages/shared/packets/external_signals/`
- `packages/` est une interdiction absolue dans ce repo (COLLISION_RESOLUTION_PLAN.md classe ces 3 entrées comme `HUMAN_REVIEW_REQUIRED`)
- La décision de ne pas créer packages/ est validée par le Plan 2 et la collision resolution

---

## 6. Failure Mode

- `packages/` créé pendant Plan 3 → PLAN3_BACKUP_GUARD_VIOLATION + BLOCKED
- Fichier `.py` créé dans runtime_contracts/ → violation
- Adapter actif créé → violation

---

## 7. Claim-Scope

**Autorisé :** "Plan 3 P0 crée uniquement des contrats documentaires — aucun runtime actif"
**Interdit :** "Plan 3 P0 installe des packages" / "Plan 3 P0 active des runtimes"

---

## 8. Verification

```bash
# Vérification attendue après Plan 3 P0
find runtime_contracts/ -name "*.py" | wc -l  # doit être 0
test -d packages/ && echo "VIOLATION" || echo "OK"
```

---

## 9. Tests Required Later

- `test_no_packages_dir_created` (validation post-Plan3)
- `test_no_py_in_runtime_contracts`

---

## 10. Example Violation

```
mkdir packages/shared/packets/
# VIOLATION — packages/ interdit
```

---

## 11. Correct Handling

```
# CORRECT
# Créer uniquement runtime_contracts/contracts/ContextPacket.contract.md
# Les packets External Signals restent dans specs/external_signals/packets/ (déjà importés)
```
