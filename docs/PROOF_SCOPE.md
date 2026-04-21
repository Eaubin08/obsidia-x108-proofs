# PROOF_SCOPE.md — Taxonomie Canonique du Périmètre de Preuve Public

**Version :** 1.0.0  
**Dernière mise à jour :** 2026-04-20

---

## But du document

Ce fichier sert de **source de vérité unique** pour interpréter correctement les chiffres, claims et objets de preuve mentionnés dans le dépôt public `obsidia-x108-proofs`.

Il répond à une ambiguïté simple :

- un **invariant** n'est pas un **théorème** ;
- un **pack de vérification** n'est pas une **famille d'invariants** ;
- un **nombre d'états TLA+ explorés** n'est pas un **nombre de preuves Lean** ;
- le **repo public** n'est pas l'**écosystème complet Obsidia**.

---

## Règle de lecture obligatoire

Tout chiffre ou claim public doit être lu selon **sa catégorie**.

Les catégories canoniques sont les suivantes :

1. **Invariants publics nommés**
2. **Théorèmes Lean**
3. **Packs / checkers exécutés publiquement**
4. **États TLA+ explorés**
5. **Artefacts cryptographiques et auditables**
6. **Éléments documentés mais non intégralement publics**

Ces catégories **ne sont pas directement comparables entre elles**.

---

## Tableau canonique des claims publics

| Claim / compteur | Ce que cela désigne réellement | Catégorie | Périmètre | Vérifiable publiquement dans ce repo ? | Artefact source |
|---|---|---|---|---|---|
| `D1 / E2 / G1 / G2 / G3` | Invariants explicitement nommés dans le statut public | Invariants publics nommés | Repo public | Oui | `PUBLIC_STATUS.md`, `docs/KERNEL_OVERVIEW.md` |
| `8 invariants du noyau` | Formulation README plus large sur les invariants du noyau public | Invariants publics (formulation README) | Repo public / façade publique | Partiellement, taxonomie détaillée à aligner | `README.md` |
| `33 théorèmes` | Volume de théorèmes Lean mentionné au niveau écosystème / intégration | Théorèmes Lean | Écosystème élargi, pas seulement le sous-périmètre vérifié par `verify_all.py` | Pas intégralement via un seul script public | `ECOSYSTEM.md` |
| `1.2M états` | États explorés via model checking TLA+ | États TLA+ explorés | Repo public | Oui | `proofs/tla/X108.tla`, docs associés |
| `V18.3.1 / V18.7 / V18.8` | Packs / checkers réellement exécutés par le pipeline public | Packs de vérification exécutés | Repo public exécutable | Oui | `proofs/verifiers/verify_all.py`, `proofs/PROOFKIT_REPORT.json` |
| `PASS` dans `PROOFKIT_REPORT.json` | Résultat effectif du pipeline public lancé | Résultat de run | Repo public exécutable | Oui | `proofs/PROOFKIT_REPORT.json` |
| `Sigma partiellement public` | Documentation + tests + configuration exposés, code de production complet non exposé | Élément documenté mais partiellement public | Repo public + écosystème | Partiellement | `PUBLIC_STATUS.md`, `docs/SIGMA.md` |

---

## Interprétation correcte des nombres

### 1. Les 5 invariants nommés
Quand le repo parle de `D1 / E2 / G1 / G2 / G3`, il parle d'un **sous-ensemble explicitement nommé** dans le statut public.

### 2. Les 8 invariants du README
Quand le README mentionne `8 invariants du noyau`, il ne faut pas lire cela comme "8 checks exécutés par `verify_all.py`". C'est une **formulation de façade publique**, qui doit être interprétée à la lumière du présent fichier.

### 3. Les 33 théorèmes
Quand `ECOSYSTEM.md` mentionne `33 théorèmes`, il parle d'un **périmètre plus large** que le seul pipeline de vérification publique `verify_all.py`.

### 4. Les V18.x
Quand `verify_all.py` exécute `V18_3_1`, `V18_7`, `V18_8`, il parle de **packs / familles de checks exécutés**, et non du total de toutes les preuves mathématiques existantes dans l'écosystème.

### 5. Les 1.2M états
Ce compteur concerne **TLA+**. Il ne doit pas être confondu avec le nombre de théorèmes Lean ni avec le nombre d'invariants publics nommés.

---

## Formulation publique recommandée

Pour éviter les dérives documentaires, les autres fichiers du dépôt devraient employer les formulations suivantes :

- **"Voir `docs/PROOF_SCOPE.md` pour l'interprétation exacte des compteurs et claims publics."**
- **"Le périmètre public vérifiable par script est défini par `proofs/verifiers/verify_all.py` et résumé dans `proofs/PROOFKIT_REPORT.json`."**
- **"Les mentions d'écosystème (ex. nombre total de théorèmes Lean) ne décrivent pas nécessairement le sous-périmètre public exécutable de ce dépôt seul."**

---

## Hiérarchie de vérité

En cas de doute, lire les couches dans cet ordre :

1. `docs/PROOF_SCOPE.md` — taxonomie canonique
2. `proofs/verifiers/verify_all.py` — périmètre exécutable réel
3. `proofs/PROOFKIT_REPORT.json` — résultat de run effectif
4. `PUBLIC_STATUS.md` — état public narré
5. `README.md` — façade de présentation
6. `ECOSYSTEM.md` — écosystème élargi

---

## Déclaration finale

**Ce dépôt public ne doit pas être lu comme si tous ses chiffres parlaient du même objet.**

Il contient plusieurs niveaux de vérité :
- façade publique,
- statut public discipliné,
- pipeline de vérification effectivement exécutable,
- et documentation d'écosystème plus large.

Le présent fichier sert à empêcher toute confusion entre ces niveaux.
