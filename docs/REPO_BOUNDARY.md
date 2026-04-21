# REPO_BOUNDARY.md — Frontière Canonique du Dépôt Public

**Version :** 1.0.0  
**Dernière mise à jour :** 2026-04-20

---

## Déclaration centrale

**`obsidia-x108-proofs` n'est pas “Obsidia entier”.**

Ce dépôt est la **façade publique de preuve, d'audit et d'intelligibilité** du noyau X-108.

Il permet :
- de comprendre le paradigme de gouvernance ex ante,
- d'auditer un sous-périmètre public de preuves,
- de vérifier des artefacts cryptographiques et des scripts publics,
- d'examiner des exemples de flux de décision,
- de situer le dépôt dans l'écosystème Obsidia.

Il **ne contient pas** l'intégralité du moteur, des couches hautes ni du corpus complet Obsidia.

---

## Ce qui est dans le périmètre de ce dépôt

### 1. Preuves publiques du noyau X-108
- spécification TLA+ publique,
- entrée Lean publique,
- scripts de vérification publics,
- rapport ProofKit public,
- documentation du noyau.

### 2. Auditabilité et traçabilité publiques
- Merkle,
- ancrage / audit trail,
- guides et limites,
- enveloppes de décision d'exemple.

### 3. Documentation bridge / intégration
- rôle de Sigma,
- rôle du kernel,
- rôle du dépôt dans l'écosystème.

---

## Ce qui est hors périmètre de ce dépôt

### 1. Le moteur de production complet
Ce dépôt n'est pas le repo principal de développement ni l'intégralité de l'implémentation runtime.

### 2. Le corpus haut complet Obsidia
Ce dépôt ne porte pas intégralement :
- les **40 blocs**,
- les **7 flux**,
- le **LTO-16D** complet,
- la **mémoire fractale** comme couche math stable exhaustive,
- les **régimes latents détaillés**,
- les **lois hautes**,
- l'**anatomie complète**,
- les couches de **sens / symbolique / math / cosmos**,
- la **checklist de freeze math intégrale**.

### 3. Le code de production complet de Sigma
Sigma est documenté publiquement et partiellement testé publiquement, mais son code de production complet n'est pas entièrement inclus ici.

### 4. L'écosystème complet des autres dépôts
L'écosystème élargi implique d'autres dépôts et d'autres périmètres : cognition, runtime, tests exhaustifs, intégrations, etc.

---

## Tableau de frontière

| Élément | Présent ici ? | Niveau |
|---|---|---|
| X-108 public | Oui | Noyau public |
| TLA+ public | Oui | Preuve publique |
| verify scripts publics | Oui | Vérification publique |
| exemples de décisions | Oui | Pédagogie / audit |
| Sigma documenté | Oui | Bridge public |
| Sigma complet de production | Non, pas intégralement | Hors périmètre public |
| moteur complet / runtime total | Non | Hors périmètre public |
| 40 blocs complets | Non, pas comme corpus canonique complet | Hors périmètre public |
| 7 flux complets | Non, pas comme corpus canonique complet | Hors périmètre public |
| LTO-16D complet | Non, pas comme corpus canonique complet | Hors périmètre public |
| freeze math intégral | Non | Hors périmètre public |
| écosystème multi-repo complet | Partiellement documenté seulement | Écosystème élargi |

---

## Règle de lecture obligatoire

Un lecteur externe doit comprendre ceci :

1. **Ce dépôt = support public structuré**
2. **Ce dépôt ≠ moteur complet**
3. **Ce dépôt ≠ totalité du corpus obsidien**
4. **Ce dépôt ≠ totalité des preuves en cours de fermeture**

---

## Formulation publique recommandée

Dans les autres documents du dépôt, la formule recommandée est :

> **Ce dépôt public expose un sous-périmètre vérifiable du noyau X-108 et de son auditabilité. Il ne prétend pas contenir l'intégralité du système Obsidia ni de son corpus de formalisation complet.**

---

## Liens internes recommandés

- `README.md` → vue d'ensemble du dépôt public
- `docs/PROOF_SCOPE.md` → taxonomie des claims et compteurs
- `PUBLIC_STATUS.md` → état réel public
- `ECOSYSTEM.md` → contexte élargi multi-repo

---

## Déclaration finale

La bonne lecture de `obsidia-x108-proofs` est :

**repo public de preuve / audit / intelligibilité du noyau X-108**

et non :

**totalité d'Obsidia**.
