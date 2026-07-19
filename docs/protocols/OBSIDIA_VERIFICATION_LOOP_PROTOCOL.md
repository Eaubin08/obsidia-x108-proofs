# OBSIDIA_VERIFICATION_LOOP_PROTOCOL

**Version :** V0
**Statut :** Protocole opérationnel
**Authority :** KX108_ONLY
**Decision authority :** Aucune — standardisation du travail uniquement
**Scope :** Post-APPLY, pré-commit, toutes les couches

---

## 1. Purpose

Ce protocole définit la boucle de vérification obligatoire entre un APPLY et un commit.

Il garantit que :
- Aucun fichier hors-scope n'est stagé.
- Aucun fichier protégé n'est contaminé.
- Le code Python compile.
- Les tests ciblés passent.
- Les preuves Lean sont valides.
- Les vérificateurs globaux passent.
- Le diff est propre (pas de trailing whitespace, pas de CRLF).

**Ce protocole ne décide pas.** Il produit `VERIFICATION_LOOP_PASS` ou `VERIFICATION_LOOP_FAIL` avec la raison exacte.

---

## 2. When to Invoke

Invoquer après **tout** APPLY, avant tout `git add` ou `git commit`.

Cas d'invocation obligatoire :

| Trigger | Raison |
|---|---|
| Fichiers Python créés ou modifiés | Vérifier la syntaxe et les tests |
| Fichiers Lean créés ou modifiés | Vérifier la compilation |
| Manifest `proofs/LEAN_PROOF_SURFACE_MANIFEST.json` modifié | Vérifier la cohérence |
| Scripts de vérification modifiés | Vérifier les verifiers eux-mêmes |
| Sigma guidance ou boundary touchés | Vérifier la non-souveraineté |
| Avant tout commit, même "simple" | Vérifier le scope exact |

---

## 3. Inputs

| Input | Source | Obligatoire |
|---|---|---|
| Liste des fichiers touchés par l'APPLY | Scope déclaré en PHASE 0 de l'APPLY | Oui |
| Liste PRE_EXISTING_DIRTY | git status --short en PHASE 0 | Oui |
| Layer de l'APPLY (SIGMA / OBSIDURE / DOCS / TOOLING) | Mode déclaré | Oui |

---

## 4. Required Checks by Scope

La table ci-dessous définit quels checks sont obligatoires selon ce qui a été touché :

| Ce qui a été touché | py_compile | pytest ciblé | Lean check | forbidden scan | verifiers | git diff --check |
|---|---|---|---|---|---|---|
| Python (sigma/, scripts/, periphery/, tests/) | OUI | OUI | NON | OUI | Selon scope | OUI |
| Lean (proofs/lean/) | NON | NON | OUI | OUI | OUI | OUI |
| Manifest JSON | NON | NON | NON | NON | OUI | OUI |
| Docs Markdown uniquement | NON | NON | NON | OUI (léger) | NON | OUI |
| Scripts de vérification | OUI | OUI | NON | OUI | OUI | OUI |

---

## 5. Python Checks

### 5.1 Syntaxe

```bash
python -m py_compile <fichier.py>
```

Attendu : exit 0. Si exit 1 → `VERIFICATION_LOOP_FAIL: py_compile <fichier>`.

### 5.2 Tests ciblés

```bash
python -m pytest <test_file_or_module> -q
```

Cibler uniquement les tests correspondant au scope de l'APPLY.

Ne pas lancer la suite complète sauf si le scope le justifie.

Attendu : `N passed`. Si `FAILED` → `VERIFICATION_LOOP_FAIL: pytest <test_name>`.

### 5.3 Règles Python

- Ne pas patcher silencieusement du code pour faire passer un test sans rapporter la cause de l'échec initial.
- Si un test échoue pour une bonne raison sémantique, corriger la cause, documenter la correction, ré-exécuter.
- Ne pas skiper un test sans justification explicite.

---

## 6. Sigma Checks

### 6.1 Non-souveraineté

```bash
python -c "
from sigma.sigma_guidance import SigmaGuidanceReport, FORBIDDEN_ACTIONS
r = SigmaGuidanceReport()
assert r.readonly is True
assert r.emits_act is False
assert r.decision_authority == 'KX108_ONLY'
assert r.recommended_action.value not in FORBIDDEN_ACTIONS
print('SIGMA_BOUNDARY_PASS')
"
```

### 6.2 Tests stratégie (si sigma/sigma_guidance.py touché)

```bash
python -m pytest sigma/tests/test_sigma_guidance.py -q
```

Attendu : 18/18 PASS (ou le nombre courant).

### 6.3 Tests Sigma Core (si sigma/ touché hors sigma_guidance)

```bash
python -m pytest sigma/tests/ -q
```

---

## 7. Obsidure / Lean Checks

### 7.1 Check individuel

```bash
cd proofs/lean
lake env lean Obsidia/GeneratedPeripheral/<TheoremeXxx>.lean
```

Attendu : exit 0. Si exit 1 → `VERIFICATION_LOOP_FAIL: lean <fichier>`.

### 7.2 Build agrégateur

```bash
cd proofs/lean
lake build Obsidia.GeneratedPeripheral
```

Attendu : `Build completed successfully`. Si fail → ne pas officialiser.

### 7.3 Aggregator Lean

```bash
cd proofs/lean
lake env lean Obsidia/GeneratedPeripheral.lean
```

Attendu : exit 0.

### 7.4 Forbidden scan Lean

Mots-clés interdits dans les fichiers Lean touchés :

```
sorry, admit, axiom, unsafe, P38, Nat.add_comm, "1 + 1 = 2",
import Std, math_memory_context_pack, runtime code, LEAN_SANDBOX
```

Commande :
```bash
python -c "
import pathlib, sys
FORBIDDEN = ['sorry', 'admit', 'axiom', 'unsafe', 'P38', 'Nat.add_comm',
             '1 + 1 = 2', 'import Std', 'math_memory_context_pack',
             'runtime code', 'LEAN_SANDBOX']
files = list(pathlib.Path('proofs/lean/Obsidia/GeneratedPeripheral').glob('*.lean'))
hits = [(f.name, kw) for f in files for kw in FORBIDDEN if kw in f.read_text(encoding='utf-8')]
print('ALL_NONE' if not hits else f'FORBIDDEN_FOUND: {hits}')
sys.exit(1 if hits else 0)
"
```

### 7.5 Manifest regen et vérification

```bash
python scripts/gen_lean_proof_surface_manifest.py
python scripts/verify_proof_branching_v1.py
python scripts/verify_domain_proof_packs.py
python scripts/verify_proof_audit_wiring_g4.py
```

Attendu : 3/3 exit 0.

---

## 8. OIE Checks

Si un script OIE ou un rapport benchmark a été modifié :

```bash
python -m py_compile <oie_script.py>
python -m pytest tests/test_oie_*.py -q
```

Les résultats de benchmark ne sont **jamais** committés sans vérification humaine préalable. Les fichiers JSON de résultats sont des PRE_EXISTING_DIRTY par défaut si déjà modifiés.

---

## 9. Forbidden Checks

### 9.1 Import GuardX108 / X108Gate dans du code non-autorisé

```bash
grep -n "GuardX108\|X108Gate" <fichier.py>
```

Si trouvé dans un fichier qui ne devrait pas y accéder → `VERIFICATION_LOOP_FAIL: forbidden import`.

### 9.2 Import graphiti / neo4j / memory_write

```bash
grep -n "graphiti\|neo4j\|memory_write" <fichier.py>
```

Dans les fichiers Sigma, Obsidure, Docs — attendu : NONE.

### 9.3 Forbidden content global

```bash
python scripts/check_forbidden_content.py
```

Attendu : exit 0.

### 9.4 Fichiers protégés

```bash
python scripts/check_protected_files.py
```

Attendu : `PROTECTED_FILES_PASS`.

---

## 10. Diff / Status Checks

### 10.1 Trailing whitespace / CRLF

```bash
git diff --check -- <fichiers du scope>
```

Attendu : aucune sortie (exit 0 = CHECK_CLEAN).

Si CRLF détecté → corriger via `write_bytes(content.encode('utf-8'))` en Python, jamais via `write_text()` sur Windows.

### 10.2 Diff scopé

```bash
git diff --name-only
```

Vérifier que seuls les fichiers du scope APPLY apparaissent (plus les PRE_EXISTING_DIRTY qui sont normaux en `M` non stagés).

Si un fichier inattendu apparaît → `VERIFICATION_LOOP_FAIL: unexpected modified file <fichier>`.

### 10.3 Staged scope check

```bash
git diff --cached --name-only
```

Attendu avant staging : vide.
Attendu après staging : exactement les fichiers du scope, rien de plus.

---

## 11. Commit Preconditions

Un commit est autorisé si et seulement si **tous** ces points sont verts :

| Précondition | Vérification |
|---|---|
| py_compile OK (si Python) | Exit 0 |
| pytest ciblé OK | N/N PASS |
| Lean checks OK (si Lean) | 10/10 ou N/N OK |
| lake build OK (si Lean) | Build completed |
| Forbidden scan NONE | ALL_NONE |
| check_protected_files PASS | Exit 0 |
| check_forbidden_content OK | Exit 0 |
| verifiers 3/3 exit 0 (si manifest) | Exit 0 |
| git diff --check CLEAN | Aucune sortie |
| staged = exactement scope déclaré | git diff --cached correspond |
| PRE_EXISTING_DIRTY absents du staging | Confirmé |

Si **un seul** check est rouge → **STOP. Ne pas commit.**

---

## 12. Stop Conditions

| Condition | Action |
|---|---|
| py_compile échoue | Corriger la syntaxe avant tout autre check |
| pytest échoue | Diagnostiquer la cause — ne pas patcher silencieusement |
| lake env lean échoue | Ne pas officialiser le théorème |
| Forbidden keyword trouvé | Retirer le fichier du scope — corriger avant de continuer |
| git diff --check détecte CRLF | Reconvertir en LF via write_bytes |
| Fichier protégé dans le diff | STOP — enquêter sur la contamination |
| Fichier PRE_EXISTING_DIRTY stagé | git restore --staged <fichier> immédiatement |
| Verifier retourne exit 1 | Diagnostiquer — ne pas forcer le commit |

**Ne jamais utiliser `--no-verify` pour contourner un hook.**

---

## 13. Final Report Format

```
VERIFICATION_LOOP_<SCOPE>_PASS
ou
VERIFICATION_LOOP_<SCOPE>_FAIL: <raison exacte>

Tableau récapitulatif :
| Check                    | Statut  | Détail |
|--------------------------|---------|--------|
| py_compile               | OK/FAIL | ...    |
| pytest ciblé             | N/N     | ...    |
| Lean checks              | N/N OK  | ...    |
| lake build               | OK/FAIL | ...    |
| forbidden scan           | NONE/FAIL | ...  |
| check_protected_files    | PASS/FAIL | ...  |
| verifiers                | 3/3/FAIL  | ...  |
| git diff --check         | CLEAN/FAIL | ... |
| staged scope             | EXACT/FAIL | ...  |
| PRE_EXISTING_DIRTY       | ABSENT/FAIL | ... |

Recommandation finale : SAFE_TO_COMMIT / CORRECTION_NEEDED
```
