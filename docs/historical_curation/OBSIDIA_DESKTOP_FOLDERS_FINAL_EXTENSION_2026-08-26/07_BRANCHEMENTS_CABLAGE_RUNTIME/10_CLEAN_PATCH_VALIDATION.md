# 10_CLEAN_PATCH_VALIDATION — Validation clean patch V2.1

**Dossier** : `C:\Users\User\Desktop\OBSIDIA_BRODY_DOMAIN_DESTINATION_MAP_V2_1_CLEAN_PATCH\`  
**Date** : 2026-06-24  
**Objectif** : Confirmer que les 3 corrections de propreté documentaire ont été appliquées sans modifier les métriques validées.

---

## Corrections appliquées

### Correction 1 — Table 3 extractibilité non-additive

**Fichier** : `01_AUDIT_TOTAL_RECONCILIATION_FIXED_CLEAN.md`  
**Problème initial** : "390 items nommés + 3963 aggregate = 4353" — formulation laissant croire que 390 est un total additif prouvant 4353.  
**Correction** :
- "390" remplacé par "environ 390 entrées / références nommées extractibles dans les vues PDF, avec chevauchements possibles entre familles, paliers et preuves"
- Avertissement explicite : "Ce chiffre sert à qualifier l'extractibilité documentaire, pas à recalculer le total audit"
- "3963" conservé uniquement comme estimation documentaire non-additive, explicitement labellisé
- La réconciliation 4353 repose exclusivement sur : **61 + 772 + 204 + 3316 = 4353** (Table 1)
- La formule "390+3963=4353" supprimée du tableau

**Statut** : CORRECTION_1_APPLIQUÉE ✓

---

### Correction 2 — Titre "Familles avec 0 Brody-only" supprimé

**Fichier** : `02_BRODY_ONLY_772_RECONCILIATION_FIXED_CLEAN.md`  
**Problème initial** : Section intitulée "Familles avec 0 Brody-only" listait MODULES=36 — contradiction directe avec le titre.  
**Correction** :
- Section contradictoire supprimée
- Remplacée par "Note sur les familles Brody-only permanentes" — table des familles à statut BRODY_ONLY_PERMANENT avec leur count réel
- MODULES = 36 Brody-only confirmé sans ambiguïté
- Règle ajoutée : BRODY_ONLY_PERMANENT = pas de vocation domaine

**Statut** : CORRECTION_2_APPLIQUÉE ✓

---

### Correction 3 — Décompte de lignes CSV remplacé par description non-fragile

**Fichier** : `08_GAP_REPORT_V1_VS_V2_FIXED_CLEAN.md`  
**Problème initial** : "56 active + 5 vérif" — nombre fragile pouvant être faux si le CSV évolue.  
**Correction** :
- Décompte de lignes supprimé de la table et du corps
- Remplacé par : "Le ledger V2.1 est un AGGREGATE_RECONCILED_LEDGER — il ne contient pas 4353 lignes item-level, mais des lignes agrégées famille × statut + lignes de vérification, dont les compteurs réconcilient exactement 4353 items (61+772+204+3316=4353 ✓)"

**Statut** : CORRECTION_3_APPLIQUÉE ✓

---

## Confirmation des métriques — inchangées

| Métrique | Valeur | Vérification | Statut |
|---|---|---|---|
| CANON Brody-only | **27** | Audit V4 page 5 | INCHANGÉ ✓ |
| OK Brody + domaine | **61** | 0+0+10+0+0+0+3+16+0+6+1+0+2+23 = 61 | INCHANGÉ ✓ |
| Brody seulement | **772** | 96+36+24+18+9+35+25+**27**+2+45+11+17+354+73 = 772 | INCHANGÉ ✓ |
| Partiel runtime | **204** | 54+8+6+87+49 = 204 | INCHANGÉ ✓ |
| Non branchés strict | **3316** | 65+0+35+16+1+465+418+449+41+443+488+483+57+355 = 3316 | INCHANGÉ ✓ |
| Grand total | **4353** | 61+772+204+3316 = 4353 | INCHANGÉ ✓ |
| Ledger type | **AGGREGATE_RECONCILED_LEDGER** | — | INCHANGÉ ✓ |

---

## Fichiers du clean patch

| Fichier | Correction appliquée |
|---|---|
| `01_AUDIT_TOTAL_RECONCILIATION_FIXED_CLEAN.md` | Table 3 non-additive |
| `02_BRODY_ONLY_772_RECONCILIATION_FIXED_CLEAN.md` | Section titre contradictoire supprimée |
| `08_GAP_REPORT_V1_VS_V2_FIXED_CLEAN.md` | Décompte CSV fragile remplacé |
| `10_CLEAN_PATCH_VALIDATION.md` | Ce fichier |

---

## Verdict

**V2_1_CLEAN_PATCH_OK**
