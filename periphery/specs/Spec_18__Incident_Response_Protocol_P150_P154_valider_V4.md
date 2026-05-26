# Spec 18 — Incident Response Protocol (P150-P154) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Incident Response Protocol

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
18) SPEC — Incident Response Protocol
(quand quelque chose déraille)
18.0 Objectif
Gérer un incident sans improvisation, sans panique, sans écriture post-hoc.
18.1 Déclencheurs
Un incident est ouvert si :
violation CRITICAL
divergence replay
signature invalide
MCP non attesté
policy compromise
18.2 États de l’incident
OPEN → CONTAINED → ANALYZED → RESOLVED → ARCHIVED
18.3 Actions automatiques (non humaines)
👉 Aucune suppression possible
18.4 Actions humaines autorisées
lecture dashboard
export audit
notification institution
changement de policy pour les futures sessions seulement
❌ Interdit :
modifier une trace
rejouer en live
“corriger” après coup
18.5 Rapport d’incident
Chaque incident produit :
audit ZIP
rapport PDF signé
timeline complète
classification taxonomy
18.6 Clôture
Un incident n’est clos que si :
toutes les vérifications passent
signatures valides
rapport archivé
🔒 Conclusion système
À ce stade, Obsidia possède :
une gouvernance lisible
une exportabilité légale
un protocole d’incident non manipulable
👉 C’est une infrastructure institutionnelle, pas un produit logiciel classique.
Si tu veux, suite logique possible :
spec “Governance UI wireframe (textual)”
spec “Regulatory compliance mapping (EU / FR)”
spec “Disaster recovery / cold restart protocol”
Parfait. On continue strictement dans le registre spec, lisible par un comité, un juriste ou un architecte, sans UX bullshit, sans extrapolation produit.
