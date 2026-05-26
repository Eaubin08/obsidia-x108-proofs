# Document A — Taxonomie Canonique des Statuts Obsidia

**Date :** 20 avril 2026  
**Objet :** Définition stricte, exclusive et exhaustive des 7 statuts du corpus documentaire et du code source.

---

## 1. La Règle des Deux Compteurs (Séparation stricte)

Pour mettre fin à toute contradiction entre le dépôt GitHub et les documents Word, la taxonomie repose sur **deux compteurs mathématiquement indépendants** :

1. **Compteur Code (Le Réel)** : Ce qui compile dans le dépôt `obsidia-x108-proofs` (branche `freeze/x108-local-20260411`).
2. **Compteur Corpus (La Carte)** : Ce qui est écrit dans les 158 emails et les 5 documents DOCX de vision.

---

## 2. Les 7 Statuts Canoniques Gelés

Chaque pépite (P1 à P161) possède **un et un seul statut documentaire principal** parmi les 6 premiers, et peut posséder le statut secondaire **OPÉRATOIRE**.

### 🟢 1. LEAN_PROUVÉ (Compteur Code : 61)
* **Définition :** Le théorème mathématique est écrit en Lean 4, il compile sans erreur et sans utiliser la commande `sorry`.
* **Preuve d'existence :** Présent dans un fichier `.lean` du repo GitHub.
* **Exemple :** `P13_Immutability` dans `Seal.lean`.

### 🔵 2. PÉPITE_ANCRÉE (Compteur Corpus : 7)
* **Définition :** La pépite conceptuelle d'origine (écrite en français dans les emails) qui a donné naissance à un ou plusieurs théorèmes `LEAN_PROUVÉ`.
* **Règle :** Une `PÉPITE_ANCRÉE` peut générer plusieurs théorèmes `LEAN_PROUVÉ` (ex: P43 a généré 4 théorèmes).
* **Liste exhaustive (7) :** P13, P15, P17, P41, P43, P86, P87.

### 🟦 3. FORMALISÉ (Compteur Corpus : 131)
* **Définition :** La pépite possède une formulation narrative ET une formule mathématique explicite (équations, invariants, structures ensemblistes) dans les documents de référence (`v1cano.docx`, `formalisermath.docx`, etc.).
* **Exemple :** P1 (Mémoire ≠ stockage : $M(t+1) = f(M(t), I(t))$).

### 🟡 4. À_PROUVER (Compteur Corpus : 3)
* **Définition :** La pépite est `FORMALISÉ` et possède en plus une esquisse de code Lean 4 dans les documents (ex: `formalisermath.docx`), mais ce code n'a pas encore été intégré ni compilé dans le repo GitHub.
* **Liste exhaustive (3) :** P36, P107, P161.
* **Note sur P161 :** P161 possède un objet mathématique minimal via les étapes LP-0 à LP-7 dans `formalisermath.docx`. Il n'est donc pas À_FORMALISER. Le travail restant est la compilation Lean.

### 🔴 5. À_FORMALISER (Compteur Corpus : 19)
* **Définition :** La pépite existe sous forme de texte (narratif/philosophique) dans les documents, mais n'a pas encore été traduite en formule mathématique stricte.
* **Règle de correction :** Les pépites dont la formulation mathématique est jugée trop légère ou trop narrative ont été reclassées de `FORMALISÉ` à `À_FORMALISER`.
* **Liste canonique exacte (19) :** P47 à P63 (Cosmos) + P149 + P155 (Récit).

### 🟣 6. VISION (Compteur Corpus : 1)
* **Définition :** Pépite purement conceptuelle ou hors-scope mathématique (ex: AGI finale).
* **Exemple :** P160 (AGI déterministe).

### ⚙️ 7. OPÉRATOIRE (Statut Secondaire : 12)
* **Définition :** La pépite est implémentée en code TypeScript/Python actif dans les modules OS4 (ex: `DecisionLayer.ts`, `TemporalBridge.ts`).
* **Règle :** C'est un statut orthogonal. Une pépite peut être `FORMALISÉ` + `OPÉRATOIRE` ou `PÉPITE_ANCRÉE` + `OPÉRATOIRE`.
* **Exemple :** P86 (Loi de non-forçage) est `PÉPITE_ANCRÉE` (Lean) ET `OPÉRATOIRE` (TypeScript).

---

## 3. Matrice de Résolution des Contradictions

| Si le document X dit... | Et le document Y dit... | La vérité canonique est... |
|---|---|---|
| "Il y a 61 pépites prouvées" | "Il y a 7 pépites ancrées" | Les deux sont vrais. 61 théorèmes Lean dérivent de 7 pépites conceptuelles. |
| "P161 est À_FORMALISER" | "P161 est À_PROUVER" | **P161 est À_PROUVER.** Un objet mathématique minimal existe (LP-0 à LP-7). |
| "P47 est FORMALISÉ" | "P47 n'a pas de formule" | **P47 est À_FORMALISER.** Le statut `FORMALISÉ` de la V2 était abusif. |
| "P86 est OPÉRATOIRE" | "P86 est LEAN_PROUVÉ" | **P86 est PÉPITE_ANCRÉE + OPÉRATOIRE.** (LEAN_PROUVÉ s'applique au théorème, pas à la pépite). |
