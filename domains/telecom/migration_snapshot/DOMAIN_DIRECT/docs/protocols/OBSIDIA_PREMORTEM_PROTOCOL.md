# OBSIDIA_PREMORTEM_PROTOCOL

**Version :** V0
**Statut :** Protocole opérationnel
**Authority :** KX108_ONLY
**Decision authority :** Aucune — analyse prospective uniquement
**Scope :** Pré-APPLY, toutes les couches

---

## 1. Purpose

Le premortem est une **analyse prospective** des risques d'un APPLY avant son exécution.

Il répond à la question : **"Si cet APPLY échoue, comment et pourquoi ?"**

Le premortem :
- est READ_ONLY,
- ne modifie aucun fichier,
- ne stage rien,
- ne commite rien,
- peut recommander STOP avant que le travail commence.

Il protège contre : la contamination de fichiers protégés, la perte de travail par mauvais scope, les conflits avec des dirty files, les dépendances oubliées, les hypothèses implicites non vérifiées.

---

## 2. When to Invoke

Invoquer **avant tout APPLY** dont le scope touche :

- des fichiers Python dans `sigma/`, `periphery/`, `scripts/`, `tests/`,
- des fichiers Lean dans `proofs/lean/`,
- le manifest `proofs/LEAN_PROOF_SURFACE_MANIFEST.json`,
- un nouveau sous-répertoire dans le repo,
- plusieurs couches simultanément.

Pour les APPLY de documentation pure (Markdown uniquement, hors scope protégé), le premortem peut être allégé mais reste recommandé.

---

## 3. Inputs

| Input | Source | Obligatoire |
|---|---|---|
| Scope déclaré de l'APPLY (fichiers à créer/modifier) | Mode déclaré par l'opérateur | Oui |
| État du working tree | `git status --short` | Oui |
| Liste des fichiers stagés | `git diff --cached --name-only` | Oui |
| Dernier commit | `git log --oneline -3` | Oui |
| Layer de l'APPLY | Mode déclaré | Oui |
| Preflight report (si disponible) | Session précédente | Recommandé |

---

## 4. Failure-Story Method

Pour chaque fichier dans le scope de l'APPLY, écrire le scénario d'échec le plus probable :

**Template :**
```
Fichier : <chemin>
Action : CREATE / MODIFY
Scénario d'échec : <description en une phrase>
Probabilité : HAUTE / MOYENNE / BASSE
Effet si non détecté : <impact>
Garde-fou : <commande de détection>
```

**Exemples :**

```
Fichier : sigma/sigma_guidance.py
Action : CREATE
Scénario d'échec : write_text() sur Windows génère des CRLF → git diff --check échoue
Probabilité : HAUTE (Windows + Python text mode)
Effet si non détecté : commit bloqué, 400+ lignes en diff parasite
Garde-fou : write_bytes(content.encode('utf-8'))

Fichier : proofs/lean/Obsidia/GeneratedPeripheral.lean
Action : MODIFY (ajout d'imports)
Scénario d'échec : lake env lean échoue car .olean manquants
Probabilité : HAUTE (agrégateur sans lake build préalable)
Effet si non détecté : aggregator invalide, manifest incohérent
Garde-fou : lake build Obsidia.GeneratedPeripheral avant lake env lean

Fichier : proofs/LEAN_PROOF_SURFACE_MANIFEST.json
Action : REGEN
Scénario d'échec : manifest_id pas mis à jour (V1→V2 oublié)
Probabilité : MOYENNE
Effet si non détecté : verify_proof_branching_v1.py retourne exit 1
Garde-fou : vérifier manifest_id dans le JSON après regen
```

---

## 5. Hidden Assumptions

Lister les hypothèses implicites qui pourraient invalider l'APPLY :

| Hypothèse | À vérifier avant de commencer |
|---|---|
| `docs/protocols/` existe déjà | `ls docs/protocols/ 2>/dev/null` |
| Tous les imports requis sont disponibles | `python -c "import <module>"` |
| Le manifest courant est cohérent avec les fichiers sur disque | `python scripts/verify_proof_branching_v1.py` |
| `lake` est disponible dans le PATH | `which lake` |
| Les fichiers à modifier sont en LF dans HEAD | `git show HEAD:<fichier> \| xxd \| grep -c 0d0a` |
| Le scope ne contient aucun fichier protégé | Voir Phase 7 ci-dessous |
| Les PRE_EXISTING_DIRTY ne créent pas de conflit | Voir Phase 8 ci-dessous |
| Les tests existants ne seront pas cassés par les nouveaux fichiers | `python -m pytest -q --co` (collect only) |

---

## 6. Risks by Layer

### Sigma

| Risque | Indicateur | Garde-fou |
|---|---|---|
| Sigma devient décideur | `emits_act=True` dans un objet | Test boundary `assert r.emits_act is False` |
| Import GuardX108 ou X108Gate | Présent dans les imports | `grep "GuardX108\|X108Gate" sigma/sigma_guidance.py` |
| HOLD_RECOMMENDED confondu avec HOLD | Wording dans le code ou les docs | Vérifier que `SigmaAction.HOLD_RECOMMENDED.value != "HOLD"` |

### Obsidure / Lean

| Risque | Indicateur | Garde-fou |
|---|---|---|
| sorry/admit/axiom dans un fichier candidat | Keyword présent | Forbidden scan avant officialisation |
| Aggregator invalide après ajout d'import | `lake env lean` échoue | `lake build` avant `lake env lean` |
| Manifest count incorrect | `verify_proof_branching_v1.py` exit 1 | Vérifier count = nb fichiers réels |
| Fichier `Basic.lean` ou `TemporalKernel.lean` touché | Dans le scope | BLOCK immédiat |

### Python / Scripts

| Risque | Indicateur | Garde-fou |
|---|---|---|
| CRLF sur Windows | `write_text()` en Python | Utiliser `write_bytes(content.encode('utf-8'))` |
| Import circulaire | `ImportError` au py_compile | Tester les imports isolément |
| Test qui brise un test existant | Conflit de nommage ou fixture | `python -m pytest --co -q` avant l'APPLY |

### Docs / Markdown

| Risque | Indicateur | Garde-fou |
|---|---|---|
| Wording interdit ("Sigma décide", "Sigma autorise") | Présent dans le doc | `grep "Sigma decides\|Sigma autorise\|Sigma allows"` |
| Référence à l'outillage externe comme architecture | `.claude` dans le corps | `grep "\.claude" docs/protocols/` |
| Contradiction avec la doctrine Sigma V0 | `FORBIDDEN_ACTIONS` non référencés | Vérification manuelle |

---

## 7. Protected Files Check

Avant tout APPLY, vérifier qu'aucun fichier protégé n'est dans le scope déclaré.

**Fichiers et répertoires protégés :**

```
sigma/guard.py
sigma/contracts.py
sigma/protocols.py
sigma/aggregation.py
sigma/sigma_guidance.py          (Sigma Guidance V0 — commits e97fc64e)
proofs/lean/Obsidia/Basic.lean
proofs/lean/Obsidia/TemporalKernel.lean
proofs/LEAN_PROOF_SURFACE_MANIFEST.json  (sauf si APPLY Obsidure explicite)
merkle_seal.json
server.kernel.sealed.cjs
runtime_terrain_bank_trading_gps/server.kernel.sealed.cjs
periphery/obsidure_math_memory_readonly/  (MathMemory — readonly strict)
```

**Commande :**
```bash
python scripts/check_protected_files.py
```

Si un fichier protégé apparaît dans le scope → **`BLOCKED_BY_BOUNDARY`**. Ne pas continuer.

---

## 8. Dirty Tree Check

```bash
git status --short
git diff --cached --name-only
```

**Règles :**

1. Si `staged != 0` → **`BLOCKED_BY_DIRTY_TREE`**. Résoudre avant de continuer.
2. Les fichiers `M` non stagés (PRE_EXISTING_DIRTY) sont **normaux** — les enregistrer explicitement.
3. Les PRE_EXISTING_DIRTY ne doivent **jamais** être stagés dans ce scope.
4. Les fichiers `??` non trackés sont ignorés sauf s'ils sont dans le scope de l'APPLY.

**Template de rapport dirty tree :**
```
staged : 0 (OK) / N (BLOCKED)
PRE_EXISTING_DIRTY : <liste>
Risque de contamination : NONE / <fichier à risque>
```

---

## 9. Scope Risk

Évaluer le risque du scope en 3 dimensions :

| Dimension | Question | Réponse |
|---|---|---|
| **Surface** | Combien de fichiers sont touchés ? | 1–3 = LOW, 4–10 = MEDIUM, >10 = HIGH |
| **Irréversibilité** | Les changements sont-ils faciles à rollback ? | Markdown = LOW, Python = MEDIUM, Lean/Manifest = HIGH |
| **Dépendances** | Le scope touche-t-il des fichiers dont d'autres dépendent ? | Manifest, Aggregator, GuardX108 = HIGH |

**Matrice de décision :**

| Surface × Irréversibilité × Dépendances | Recommandation |
|---|---|
| LOW × LOW × NONE | SAFE_TO_APPLY |
| MEDIUM × LOW × NONE | SAFE_TO_APPLY avec VERIFICATION_LOOP complet |
| HIGH × MEDIUM × MEDIUM | NEEDS_MORE_AUDIT ou SPLIT_SCOPE |
| ANY × ANY × HIGH (manifest, guard, kernel) | NEEDS_MORE_AUDIT obligatoire |
| Fichier protégé dans scope | BLOCKED_BY_BOUNDARY |

---

## 10. Rollback Path

Pour chaque fichier dans le scope, définir le chemin de rollback :

| Type de fichier | Rollback |
|---|---|
| Fichier nouveau (CREATE) | `git rm <fichier>` ou suppression directe si non stagé |
| Fichier modifié (MODIFY) | `git checkout HEAD -- <fichier>` (restaure depuis HEAD) |
| Répertoire nouveau (CREATE DIR) | `rm -rf <dir>` si non committé |
| Manifest régénéré | `git checkout HEAD -- proofs/LEAN_PROOF_SURFACE_MANIFEST.json` |
| Fichier stagé par erreur | `git restore --staged <fichier>` |

**Règle de rollback :**
- Ne jamais utiliser `git reset --hard` sans confirmation explicite de l'opérateur.
- Un rollback de commit nécessite `git revert` (safe) ou `git reset` (destructif, confirmation requise).

---

## 11. Recommendation Categories

| Catégorie | Condition | Action |
|---|---|---|
| `SAFE_TO_APPLY` | Scope propre, aucun fichier protégé, dirty tree documenté, risque LOW | Procéder à l'APPLY |
| `NEEDS_MORE_AUDIT` | Scope ambigu, dépendances non vérifiées, risque MEDIUM/HIGH | Audit supplémentaire avant APPLY |
| `SPLIT_SCOPE` | Scope trop large (>10 fichiers ou >2 couches simultanées) | Décomposer en 2+ APPLY séparés |
| `BLOCKED_BY_BOUNDARY` | Fichier protégé (Kernel/X108/Lean Core/Sigma Core) dans le scope | STOP — retirer le fichier protégé du scope |
| `BLOCKED_BY_DIRTY_TREE` | `staged != 0` | STOP — vider le staging area avant de continuer |
| `BLOCKED_BY_MISSING_PROOF` | APPLY Obsidure sans Lean check passant ou manifest cohérent | STOP — valider les preuves avant d'officialiser |

---

## 12. Final Report Format

```
PREMORTEM_<SCOPE>_COMPLETE

| Critère                    | Valeur                          |
|----------------------------|---------------------------------|
| staged                     | 0 / N                           |
| PRE_EXISTING_DIRTY         | <liste>                         |
| Fichiers protégés dans scope | YES (BLOCKED) / NO             |
| Surface (nb fichiers)      | N                               |
| Irréversibilité            | LOW / MEDIUM / HIGH             |
| Dépendances critiques      | NONE / <liste>                  |
| Scénarios d'échec          | N identifiés                    |
| Hypothèses cachées         | N vérifiées                     |
| Rollback path défini       | YES / PARTIAL                   |

Recommandation : SAFE_TO_APPLY / NEEDS_MORE_AUDIT / SPLIT_SCOPE /
                 BLOCKED_BY_BOUNDARY / BLOCKED_BY_DIRTY_TREE /
                 BLOCKED_BY_MISSING_PROOF

Raison : <une ligne>
```
