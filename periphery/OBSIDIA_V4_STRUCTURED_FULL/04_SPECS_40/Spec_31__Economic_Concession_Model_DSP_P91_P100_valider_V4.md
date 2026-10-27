# Spec 31 — Economic Concession Model DSP (P91-P100) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Economic Concession Model (DSP)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
31) SPEC — Economic Concession Model (DSP)
31.0 Objectif
Définir un modèle de concession économique permettant le déploiement d’Obsidia comme infrastructure publique via DSP / marchés publics, sans transfert de souveraineté cognitive.
31.1 Principe fondamental
Obsidia n’est pas vendue. Elle est concédée, gouvernée et auditable.
31.2 Acteurs
Autorité concédante
État / Région / Métropole / Autorité indépendante
Exploitant Obsidia
Entité certifiée (publique, mixte ou privée)
Tiers auditeur
Cabinet indépendant / Autorité de contrôle
31.3 Périmètre concédé
✓ Exploitation OS3 (audit)
✓ Sandbox publique contrôlée
✓ Portail régulateur
✓ Maintenance infra
❌ Hors concession :
noyau OS0–OS1 (immutable)
constitution
taxonomies
métriques de vérité
31.4 Flux économiques
Redevance fixe annuelle
+ Redevance variable indexée sur :
   - nombre d’audits
   - volume sandbox
   - agents actifs
❌ Interdit :
paiement à l’appel
facturation au token
dépendance fournisseur
31.5 Clauses structurantes (opposables)
Réversibilité totale
Export audit complet (Replay Packs)
Interdiction de modification des règles
Clés racines hors exploitant
31.6 Indicateurs contractuels
Décisions autonomes : 0
Actions humaines tracées : 100%
Auditabilité : native
Temps de replay garanti
