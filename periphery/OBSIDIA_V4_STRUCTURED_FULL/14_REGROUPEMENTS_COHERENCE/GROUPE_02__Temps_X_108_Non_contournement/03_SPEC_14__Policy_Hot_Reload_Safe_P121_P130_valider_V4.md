# Spec 14 — Policy Hot-Reload Safe (P121-P130) — valider V4

**Statut V4 :** FORMALISÉ_À_VALIDER
**Titre source détaillé :** Policy Hot-Reload (Safe)

## Contrat V4
- Spécification lisible.
- Entrées / sorties / invariants identifiables.
- Audit C obligatoire.

## Contenu source
14) SPEC — Policy Hot-Reload (Safe)
(mise à jour de policy sans casser le déterminisme)
14.0 Objectif
Permettre :
modification de policy sans redémarrage
sans impacter une session active
sans invalider les audits en cours
14.1 Principe fondamental
Une session ne change jamais de policy en cours d’exécution.
14.2 Architecture
policy.json
   ↓ compile
policy.compiled.bin
   ↓ hash + signature
policy_store/
   ├─ policy_v1.bin
   ├─ policy_v2.bin
   └─ active_pointer
14.3 Processus de hot-reload
Nouvelle policy déposée
Compilation → policy_v2.bin
Signature validée
Hash inscrit dans policy_store
active_pointer mis à jour
Nouvelles sessions seulement utilisent la nouvelle policy
👉 Les sessions existantes continuent avec policy_hash_initial
14.4 Règles strictes
Aucune session ne migre
Aucune policy non compilée
Rollback possible instantanément
Chaque session stocke :
policy_id
policy_hash
14.5 Trace obligatoire
Chaque reload produit :
POLICY_COMPILED
POLICY_ACTIVATED
POLICY_ROLLBACK (si besoin)
