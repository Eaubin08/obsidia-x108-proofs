# THEOREM_TO_ARCHITECTURE_MAP
# OBSIDIA_INVARIANT_GRAPH_AUDIT_V1
# Date: 2026-06-02

---

| Theorem / Invariant | Rôle architectural | Empêche | Permet | Couche stabilisée |
|---------------------|-------------------|---------|--------|-------------------|
| `D1_determinism` | Base de toute reproductibilité | Variation non déterministe de la décision | Replay fidèle, audit vérifiable | OS0 kernel — toutes couches |
| `E2_no_act_below_threshold` | Gate de base sur le seuil θ | ACT sans condition métrique satisfaite | Décision nuancée par score | OS0/OS1 |
| `X108_no_act_before_tau` | **Gate temporelle principale** | ACT prématuré sur action irréversible | Fenêtre de sécurité τ pour réflexion humaine | OS1 TEMPORAL — toutes périphéries |
| `X108_after_tau_equals_base` | Libération temporelle contrôlée | Blocage permanent au-delà de τ | Retour à la décision de base après délai | OS1 |
| `X108_kernel_never_blocks` | Garantie de non-BLOCK du kernel | BLOCK émanant du kernel (seul HOLD ou ACT) | Distinction propre des verdicts | OS1 — Sigma, Brody, GPS |
| `X108_reversible_equals_base` | Simplification pour actions réversibles | Sur-protection d'actions non critiques | Performance — τ ne s'applique qu'à l'irréversible | OS1 |
| `X108_irreversible_after_tau_equals_base` | Fermeture de la fenêtre temporelle | Holding permanent d'irréversibles | Action irréversible après délai juste | OS1 |
| `Refinement.x108_never_blocks` | Extension du kernel sans BLOCK | BLOCK dans le kernel raffiné | Ajout de couches sans régresser la garantie | OS1→OS2 **clé d'extension** |
| `Refinement.refined_not_block` | Propagation de no-BLOCK au raffinement | Toute décision raffinée d'être BLOCK | Empilement sûr de couches décisionnelles | OS2 |
| `P13_Immutability` (Seal) | Détection de toute modification de fichiers | Falsification de la trace scellée | Preuve cryptographique d'intégrité | OS3 SEAL |
| `P15_Immutability_Strong` (Merkle) | Sensibilité du seal à tout changement de repo | Modification non détectée d'un fichier quelconque | Immutabilité forte du corpus | OS3 MERKLE |
| `merkleRoot_change_if_leaf_change` | Propagation du changement de feuille | Collision de racine après modification | Construction sûre de l'arbre Merkle | OS3 |
| `aggregate4_fail_closed` | **Consensus fail-closed** | Décision sans quorum (< 3/4) | Sécurité Byzantine sous perte de nœuds | OS3 CONSENSUS |
| `no_two_distinct_supermajorities_4` | Unicité du vote majoritaire | Deux décisions contradictoires simultanées | Cohérence forte du consensus | OS3 |
| `canonicalize_preserves_nonneg` | Cohérence temps entier → naturel | Comportement non défini sur temps négatif | Bridge propre entre horloge raw et kernel | OS1 BRIDGE |
| `skew_negative_implies_hold` | **Garde contre clock skew** | ACT sous skew temporel négatif (irréversible) | Robustesse aux désynchronisations d'horloge | OS1 BRIDGE — External Signals |
| `P17_Determinism` | Déterminisme système complet | Non-reproductibilité d'état | Replay, audit, vérification externe | OS2 SYSTEM |
| `P17_AuditGrowth` | Croissance monotone du log | Suppression ou falsification de l'audit | Audit append-only vérifiable | OS2 OS3 |
| `P17_KernelNeverBlocks` | Garantie institutionnelle | BLOCK au niveau institutionnel | Composabilité du kernel | OS2 |
| `SealAssumptions.combine_inj` | Hypothèse cryptographique fondamentale | Collision dans le hash combine | Injectivité du seal (sous hypothèse) | OS3 — fondation |
| `G1_act_above_threshold` | Gate positive | ACT sans condition métrique | Décision fondée sur score S | OS0 |
| `TLA SafetyX108 □(irr∧elapsed<τ→¬ACT)` | Vérification model-checking de la sûreté | Chemins d'exécution violant X108_no_act | Certitude de couverture sur espace d'états borné | OS1 — niveau spec |
| `aggregate4_unanimous` | Cohérence de l'unanimité | Incohérence sous vote unanime | Garantie de base consensus | OS3 |
| V18_7 meet lattice | Composition de gates | Gates s'annulant mutuellement | Composition monotone ALLOW<HOLD<BLOCK | OS2 (V18) |
| V18_7 nonce anti-replay | Anti-replay gate | Rejeu d'action déjà exécutée | Signature d'intégrité temporelle | OS3 (V18) |

---

## Invariants les plus critiques pour l'extensibilité

Ces invariants sont ce qui empêche toute couche ajoutée de s'approprier l'autorité décisionnelle :

| Priorité | Invariant | Raison |
|----------|-----------|--------|
| **#1** | `Refinement.x108_never_blocks` | Prouve que toute couche raffinant X108 hérite de la garantie no-BLOCK |
| **#2** | `X108_no_act_before_tau` | Protège la fenêtre temporelle même en présence de nouvelles couches |
| **#3** | `aggregate4_fail_closed` | Empêche une couche distribuée de décider sans quorum |
| **#4** | `P15_Immutability_Strong` | Empêche toute couche de falsifier la trace sans détection |
| **#5** | `skew_negative_implies_hold` | Empêche les nouvelles couches temporelles (External Signals) de forcer ACT sous skew |
| **#6** | `D1_determinism` | Garantit que toute couche ajoutée n'introduit pas de non-déterminisme |
