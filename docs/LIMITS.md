# Limites structurelles — obsidia-x108-proofs

## 1. CryptoAssumptions — Hash abstrait synthétique
Le type `Hash` dans `proofs/lean/Obsidia/CryptoAssumptions.lean` est une
structure inductive synthétique, pas SHA-256 réel.
Les propriétés démontrées sont valides dans le modèle abstrait uniquement.
Pour une preuve crypto réelle, une bibliothèque comme `mathlib4` avec des
hypothèses cryptographiques standards serait nécessaire.

**Impact :** Les invariants crypto sont formellement corrects sur leur modèle.
Ils ne garantissent pas les propriétés de SHA-256 en production.

## 2. TLC — Résultats de model-checking non persistés
Les logs TLC ne sont pas dans le repo par défaut.
Ils sont générés automatiquement via CI (GitHub Actions) et archivés comme artifacts.
Pour relancer manuellement : `tlc formal/tla/X108.tla -config formal/tla/X108.cfg`
Les résultats vont dans `formal/tla/tlc_results/`.

## 3. Fichiers WIP Lean
Les fichiers dans `proofs/lean/wip/` sont des brouillons d'expérimentation.
Ils ne sont pas des preuves finales. Voir `proofs/lean/wip/README.md`.

## 4. TemporalRaw.lean
Si présent, `TemporalRaw.lean` est un fichier brut non vérifié.
À déplacer dans `proofs/lean/wip/` si confirmé comme brouillon.

## 5. CI/CD
GitHub Actions actif via `.github/workflows/verify.yml`.
Relance automatiquement `lake build` (Lean) et TLC à chaque push sur main.
