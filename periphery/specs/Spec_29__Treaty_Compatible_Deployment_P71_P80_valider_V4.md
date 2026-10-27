# Spec 29 — Treaty-Compatible Deployment (P71-P80) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Treaty-Compatible Deployment (Inter-États)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
29) SPEC — Treaty-Compatible Deployment (Inter-États)
29.0 Objectif
Permettre des déploiements multi-territoires, interopérables, sans fusion des souverainetés.
29.1 Principe clé
Chaque territoire reste souverain, les audits se fédèrent.
29.2 Architecture fédérée
[ Obsidia FR ] ──┐
                 ├── Audit Federation Layer
[ Obsidia EU ] ──┤
                 └── Read-Only Proof Exchange
29.3 Éléments échangeables
✓ Hash constitution
✓ Hash policy
✓ Hash replay packs
✓ Résumés d’audit signés
❌ Jamais échangés :
logs
données
policies actives
clés privées
29.4 Protocole minimal
audit_summary.json
- territory_id
- constitution_hash
- compliance_status
- violations_count
- signature
29.5 Cas d’usage
Programmes européens
Coopération régulateurs
Audits croisés
Reconnaissance mutuelle
