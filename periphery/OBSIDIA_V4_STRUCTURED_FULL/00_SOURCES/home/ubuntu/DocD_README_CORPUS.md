# Document D — README_CORPUS : Hiérarchie Documentaire Officielle du Corpus Obsidia

**Date :** 20 avril 2026 (version V3.1 — après correction des 3 contradictions résiduelles)  
**Statut :** OFFICIEL — Ce fichier est la porte d'entrée du corpus. Lire en premier.

---

## Qu'est-ce que le corpus Obsidia ?

Le corpus Obsidia est l'ensemble des documents, preuves, spécifications et implémentations du projet Obsidia. Il est organisé en **4 couches hiérarchiques** :

```
COUCHE 1 — VISION (narratif, concepts)
    ↓
COUCHE 2 — FORMALISATION (objets mathématiques)
    ↓
COUCHE 3 — PREUVES (théorèmes Lean 4)
    ↓
COUCHE 4 — IMPLÉMENTATION (code TypeScript/Python)
```

---

## Document maître par rôle

| Rôle | Document maître | Pourquoi |
|---|---|---|
| **Vision totale / architecture** | `RapportIntégraletExhaustif_L'ArchitectureComplèted'Obsidia.md` | 17 blocs, vision système complète |
| **Granularité / statuts / formules** | `RapportIntégraldes161PépitesObsidia.md` | 161 pépites avec formules + code Lean + TypeScript |
| **Tableau de pilotage** | `MatriceIntégraledeFormalisationObsidia_V3.md` (ce document C) | Statuts officiels recalés |
| **Preuves techniques / Lean** | `RapportComplémentaireExhaustif—LaProfondeurTechniqued'Obsidia.md` | 61 théorèmes Lean avec code source |
| **Gouvernance opératoire** | `Plans_Checklists_Obsidia_Final.md` | Ordres de build, AVDR, LTCU, 4 couches, 7 régimes |
| **Taxonomie des statuts** | `Document_A_Taxonomie_Canonique.md` (ce document A) | Table de référence unique |
| **Mapping blocs/pépites** | `Document_B_Mapping_17Blocs_161Pepites.md` (ce document B) | Relation hiérarchique officielle |
| **Audit mails 8–14 mars** | `Audit_Exhaustif_Integral_Obsidia_7J.md` | 59 mails retranscrits intégralement |
| **Audit mails 15–28 mars** | `Audit_Exhaustif_Integral_Obsidia_Part2.md` | 99 mails retranscrits intégralement |
| **Référence externe** | `deep-research-report20.04.26.md` | Analyse ChatGPT — utile pour pitch |

---

## Hiérarchie de vérité

En cas de contradiction entre deux documents, la règle de priorité est :

```
Repo GitHub (branche freeze) > Document A (taxonomie) > Matrice V3 > Rapport 161 Pépites > Autres
```

**Le repo GitHub est toujours la vérité ultime sur ce qui est prouvé.**

---

## 3 Arbitrages Canoniques Gelés (V3.1)

### Arbitrage 1 — P161 : Route B retenue

P161 (calibration énergétique temporelle) possède un objet mathématique minimal via les étapes LP-0 à LP-7 dans `formalisermath.docx`. Il est classé `À_PROUVER`. Il ne figure plus dans la liste des `À_FORMALISER`. Le compteur `À_FORMALISER` passe de 20 à **19**.

### Arbitrage 2 — Mapping 17 blocs : Option 1 retenue

Chaque pépite possède **exactement un bloc principal**. Elle peut avoir des blocs secondaires (références croisées). La somme des blocs principaux est exactement 161.

### Arbitrage 3 — OPÉRATOIRE : Colonne booléenne

Le statut `OPÉRATOIRE` est une propriété orthogonale, représentée comme colonne `Opératoire = Oui/Non` dans la Matrice V3. Il ne remplace pas le statut principal.

---

## Ce qui est fermé (ne pas modifier)

| Élément | Localisation | Statut |
|---|---|---|
| 61 théorèmes Lean | Branche `freeze/x108-local-20260411` | GELÉ — 0 sorry |
| Taxonomie des 7 statuts | Document A | GELÉ |
| Mapping 17 blocs ↔ 161 pépites | Document B | GELÉ |
| Architecture OS0→OS4 | `obsidia_engine_v1_0_0-1.zip` | GELÉ |
| Payload Validation Matrix | `os4_runtime_validation_freeze_bundle_v1.zip` | GELÉ |
| Statut de P161 = À_PROUVER | Document A + Matrice V3.1 | GELÉ |
| Compteur À_FORMALISER = 19 | Document A + Matrice V3.1 | GELÉ |
| Liste À_FORMALISER = P47–P63, P149, P155 | Document A + Matrice V3.1 | GELÉ |
| Bloc 17 = P19, P20, P44, P45, P46 (5 pépites) | Document B V3.1 | GELÉ |

---

## Ce qui reste ouvert (à faire)

| Priorité | Action | Pépites concernées | Document cible |
|---|---|---|---|
| **P0 — Immédiat** | Compiler P161 en Lean (code déjà esquissé) | P161 | `P161Proofs.lean` |
| **P0 — Immédiat** | Prouver P36 (quintuplet) en Lean | P36 | `SystemModel.lean` |
| **P1 — Court terme** | Prouver P107 (Lyapunov δ-ε) en Lean | P107 | `TemporalKernel.lean` |
| **P1 — Court terme** | Formaliser les 19 pépites cosmos/récit | P47–P63, P149, P155 | `v1cano.docx` |
| **P2 — Moyen terme** | Spécifier Gencoin (loi d'émission exacte) | P58 | `obsidia/specs/gencoin.md` |
| **P2 — Moyen terme** | Spécifier GPS / défense / aviation | P59 | `obsidia/specs/gps.md` |
| **P3 — Long terme** | Unifier Balance (BUV) avec kernel | P53 | `obsidia/specs/balance.md` |

---

## Arborescence cible du corpus

```
obsidia/
├── README_CORPUS.md          ← CE FICHIER (porte d'entrée)
├── specs/
│   ├── 00_kernel_contract.md
│   ├── 01_latent_space.md
│   ├── 02_cognitive_layers.md
│   ├── 03_protocols.md
│   ├── 04_metrics.md
│   ├── 05_stability_criteria.md
│   ├── 06_geometries.md
│   ├── 07_latent_regimes.md
│   ├── 08_probatory_objects.md
│   ├── 09_macro_components.md
│   ├── 10_agents.md
│   ├── 11_test_matrix.md
│   ├── gencoin.md            ← À CRÉER
│   └── gps.md                ← À CRÉER
├── proofs/
│   └── lean/                 ← Branche freeze (61 théorèmes)
├── core/
│   └── [code Python OS0-OS2]
└── layers/
    └── [code TypeScript OS3-OS4]
```

---

## Formule de clôture canonique

> `spec → types → code → invariants → tests → freeze`

Chaque pépite suit ce chemin. Une pépite est **fermée** quand elle a traversé les 6 étapes.  
Aujourd'hui : **7 pépites fermées** (P13, P15, P17, P41, P43, P86, P87).  
Objectif : **161 pépites fermées**.

---

## Compteurs V3.1 (État d'art corrigé)

| Statut | Nb |
|---|---|
| 🟢 Théorèmes Lean prouvés (repo) | **61** |
| 🔵 Pépites ancrées (corpus) | **7** |
| 🟦 Formalisées | **131** |
| 🟡 À prouver (Lean esquissé) | **3** (P36, P107, P161) |
| 🔴 À formaliser | **19** (P47–P63, P149, P155) |
| 🟣 Vision | **1** (P160) |
| **Total pépites** | **161** |
