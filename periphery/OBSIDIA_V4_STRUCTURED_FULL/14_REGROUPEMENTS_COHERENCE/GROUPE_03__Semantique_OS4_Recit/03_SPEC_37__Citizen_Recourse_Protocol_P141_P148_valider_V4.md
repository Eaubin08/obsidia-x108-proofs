# Spec 37 — Citizen Recourse Protocol (P141-P148) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Citizen Recourse Protocol

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
37) SPEC — Citizen Recourse Protocol
37.0 Objectif
Garantir un droit de recours citoyen effectif contre tout usage d’Obsidia sans ouvrir le système.
37.1 Principe fondamental
Le citoyen ne conteste pas une décision d’IA.
Il conteste une chaîne de gouvernance.
37.2 Déclencheurs recevables
✓ soupçon de violation de policy
✓ soupçon d’absence de veto humain
✓ incohérence audit / exécution
✓ usage hors périmètre déclaré
37.3 Chaîne de recours
[ Citoyen ]
     |
     v
[ Portail Recours ]
     |
     v
[ Audit OS3 ciblé ]
     |
     v
[ Rapport opposable ]
37.4 Garanties procédurales
accès read-only
pas de données personnelles exposées
traçabilité complète du traitement
réponse bornée dans le temps
37.5 Outputs
citizen_recourse_report.pdf
- périmètre audité
- conformité / non-conformité
- actions correctives
- signatures
