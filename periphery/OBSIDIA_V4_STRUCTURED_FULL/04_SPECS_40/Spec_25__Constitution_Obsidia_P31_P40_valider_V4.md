# Spec 25 — Constitution Obsidia (P31-P40) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Constitution Obsidia (articles opposables)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
25) SPEC — Constitution Obsidia (articles opposables)
25.0 Objectif
Formaliser Obsidia comme un système constitutionnel, pas comme un logiciel.
Cette constitution définit ce que le système peut, ne peut pas, et ne pourra jamais faire, indépendamment :
des modèles,
des agents,
des interfaces,
des implémentations futures.
👉 Elle est référencée par hash, intégrée aux audits, et juridiquement opposable.
25.1 Statut
Document normatif
Versionné
Hashé
Signé
Non modifiable sans rupture de continuité
25.2 Articles fondamentaux (version canonique)
Article I — Primauté du noyau
Le noyau moteur (OS0–OS1) est inviolable, non dynamique, non exposé.
Aucune couche ne peut l’altérer, directement ou indirectement.
Article II — Interdiction de décision autonome
Obsidia ne peut produire aucune décision irréversible sans veto humain explicite, signé et vérifiable.
Article III — Séparation stricte des couches
Chaque couche est :
isolée,
comptabilisée,
auditée,
non substituable.
Toute confusion de couche constitue une violation structurelle.
Article IV — Traçabilité totale
Tout événement significatif doit :
produire une trace,
être horodaté,
être rejouable,
être vérifiable.
Ce qui n’est pas traçable n’existe pas.
Article V — Auditabilité permanente
Le système doit pouvoir être audité :
a posteriori,
sans accès au runtime,
sans modification de l’état.
Article VI — Souveraineté territoriale
Toute instance Obsidia est souveraine sur son territoire d’exécution.
Aucune dépendance cachée à une entité externe n’est autorisée.
Article VII — Réversibilité
Toute action non humaine doit être :
annulable,
rejouable,
explicable.
Article VIII — Supériorité du réel
Le réel (coût, temps, énergie, responsabilité) prévaut toujours sur l’optimisation computationnelle.
25.3 Intégration technique
constitution.hash inclus dans :
audit reports
replay packs
regulator portal
Toute divergence = non-conformité constitutionnelle
