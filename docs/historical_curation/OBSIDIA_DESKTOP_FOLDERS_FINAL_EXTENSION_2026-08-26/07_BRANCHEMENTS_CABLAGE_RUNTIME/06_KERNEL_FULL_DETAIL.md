# 06_KERNEL_FULL_DETAIL — Kernel X-108 : inventaire complet nom-par-nom

**Règle** : KX108_ONLY — BLOCK > HOLD > ALLOW non inversible — FAIL-CLOSED — SIGNED_DECISION_RECEIPT obligatoire
**Source** : V1 Readonly 02_KERNEL_ONLY_AUTHORITY.md + Checklist P4 + Audit V4

---

## Table 1 — Composants kernel/ (P4-01 à P4-19)

| ID | Fichier | Rôle | Brody ? | Bank ? | Trading ? | GPS ? | Entrée | Sortie | Preuve attendue | Interdit |
|---|---|---|---|---|---|---|---|---|---|---|
| K-01 / P4-01 | kernel/gardien_amont.py | Garde d'entrée — IR(C)=0 and CIZ(C)=0 → ADMIT/REFUSE/ESCALATE | NON | OUI | OUI | OUI | Paquets domaine via API bridge | ADMIT / REFUSE / ESCALATE | SIGNED_DECISION_RECEIPT.json | Bypass sans IR+CIZ |
| K-02 / P4-02 | kernel/trajectory_state.py | État trajectoire : past_trace / current / intended / projected | NON | NON | OUI | OUI | Contexte session SRL | État trajectoire structuré | Trace dans SIGNED_RECEIPT | Écriture directe par Brody |
| K-03 / P4-03 | kernel/tls_score.py | Score TLS — 5 composantes (integrity/governance/readiness/...) | NON | OUI | OUI | OUI | Données contexte + domaine | Score numérique 0–100 | Score dans envelope | Modification score externe |
| K-04 / P4-04 | kernel/temporal_action_authority_layer.py | Temporal Zero Trust layer | NON | OUI | OUI | OUI | Timestamp + contexte session | Autorisation temporelle | Timestamp signé | Bypass temporel |
| K-05 / P4-05 | kernel/rpl_x108.py | RPL-X108 claim_state machine (candidate→upper-bound→restricted→blocked→admissible) | NON | OUI | OUI | OUI | Claim entrant | État claim transitionné | Claim state dans receipt | Promotion automatique |
| K-06 / P4-06 | kernel/code_authorization_gate.py | Invariant TEST_PASS ≠ AUTHORIZED | NON | OUI | OUI | OUI | Résultat de test + code | AUTH / REJECT | Gate log dans receipt | Confondre test_pass et authorized |
| K-07 / P4-07 | kernel/signed_decision_receipt.py | Génère SIGNED_DECISION_RECEIPT.json | NON | OUI | OUI | OUI | Décision kernel complète | SIGNED_DECISION_RECEIPT.json | Fichier JSON généré | Omission du receipt |
| K-08 / P4-08 | kernel/path_admission.py | Admission de chemin décisionnel | NON | OUI | OUI | OUI | Chemin proposé | ADMIT / DENY | Path dans receipt | Admettre sans validation |
| K-09 / P4-09 | kernel/claim_state_machine.py | Machine d'états claim | NON | OUI | OUI | OUI | Claim signé | State transition | State log | Transition non autorisée |
| K-10 / P4-10 | kernel/temporal_zero_trust.py | Zero Trust temporel — confiance implicite interdite | NON | OUI | OUI | OUI | Requête horodatée | Confiance / Refus temporel | Trust log | Trust implicite sans vérif |
| K-11 / P4-11 | kernel/pre_action_authorization_gate.py | Gate pré-action — avant toute action domaine | NON | OUI | OUI | OUI | Requête d'action | PRE_AUTH | Gate decision | Action sans pre-auth |
| K-12 / P4-12 | kernel/temporal_policy_layer.py | Politique temporelle — contexte temporel de la décision | NON | OUI | OUI | OUI | Politique + contexte | ALLOW/BLOCK temporel | Policy log | Override politique externe |
| K-13 / P4-13 | kernel/decision_path_guard.py | Garde chemin décision | NON | OUI | OUI | OUI | Chemin complet | Garde validé / refusé | Guard log | Chemin court-circuité |
| K-14 / P4-14 | kernel/agentic_security_layer_v0.py | Couche sécurité agentique — agents doivent être enregistrés | NON | OUI | OUI | OUI | Agent request | Sécurité validée / BLOCK | Security log | Agent non enregistré |
| K-15 / P4-15 | kernel/agentic_decision_envelope.py | CanonicalDecisionEnvelope V3 — enveloppe structurée | NON | OUI | OUI | OUI | Données décision | Envelope JSON structurée | Envelope JSON | Envelope sans kernel |
| K-16 / P4-16 | kernel/trust_boundary_checker.py | Vérificateur frontière confiance cross-domaine | NON | OUI | OUI | OUI | Requête cross-domaine | Trust boundary vérifié | Boundary log | Cross sans checker |
| K-17 / P4-17 | kernel/runtime_behavior_gate.py | Gate comportement runtime — agent action | NON | OUI | OUI | OUI | Agent + action | ALLOW / BLOCK runtime | Runtime gate log | Agent non enregistré |
| K-18 / P4-18 | kernel/watchtower_observer.py | Observateur Watchtower — BLOQUÉ NUD-N02 | NON | NON | NON | NON | OS3 advisory flag | Observation seulement | NUD-N02 requis | Connexion sans NUD-N02 |
| K-19 / P4-19 | kernel/entropy_hold_rule.py | Entropy > seuil → HOLD automatique | NON | OUI | OUI | OUI | Score entropie signal | HOLD forcé si seuil dépassé | Entropy log | Bypass HOLD entropie |

---

## Table 2 — Composants obsidia_core/ (P4-20 à P4-23)

| ID | Fichier | Rôle | Brody ? | Bank ? | Trading ? | GPS ? | Entrée | Sortie | Preuve | Interdit |
|---|---|---|---|---|---|---|---|---|---|---|
| KC-01 / P4-20 | obsidia_core/guardians/path_fidelity_guard.py | Garde fidélité chemin — GPS prioritaire | NON | NON | PARTIEL | OUI | Chemin décisionnel | FIDELITY/BLOCK | Guard log | Chemin infidèle promu |
| KC-02 / P4-21 | obsidia_core/types/path_context.py | Types contexte chemin — GPS/Trading | NON | NON | OUI | OUI | Données contexte | Contexte typé structuré | Schema validé | Type sans validation kernel |
| KC-03 / P4-22 | obsidia_core/selfplay/sgs_x108_loop.py | SGS sandbox — auto-jeu SEULEMENT | NON | NON | NON | NON | Scénarios auto-jeu | Candidats pour validation | — | Connexion kernel directe |
| KC-04 / P4-23 | obsidia_core/memory/brody_triadic_memory_governor.py | Gouverneur mémoire triadique Brody — memory_write=false strict | OUI lecture | NON | NON | NON | Brody Enriched → gouverneur | Contexte mémoire lu | memory_write=false | Toute écriture |

---

## Table 3 — Gates domaines (pont kernel ↔ domaine)

| ID | Composant | Domaine | Règle | Interdit |
|---|---|---|---|---|
| KD-01 / P3-01 | domains/bank/bank_x108_gate.py | BANK | Tout paquet bank passe par gate avant décision kernel | Court-circuit gate |
| KD-02 / P3-03 | domains/trading/trading_x108_gate.py | TRADING | Tout paquet trading passe par gate | Court-circuit gate |
| KD-03 / P3-05 | domains/gps/gps_x108_gate.py | GPS_AVIATION | Tout paquet GPS passe par gate | Court-circuit gate |

---

## Table 4 — Preuves Lean kernel (L-01 à L-07)

**Statut** : A_CREER (D13+D14 requis) — DO_NOT_TOUCH une fois créés

| ID | Nom | Domaine prouvé | Dépendance | Statut |
|---|---|---|---|---|
| L-01 | Théorème Lean 01 | Garde amont P4-01 | D13 + D14 validés | A_CREER |
| L-02 | Théorème Lean 02 | Trajectoire state P4-02 | D13 + D14 | A_CREER |
| L-03 | Théorème Lean 03 | Code authorization P4-06 | D13 + D14 | A_CREER |
| L-04 | Théorème Lean 04 | Receipt P4-07 | D13 + D14 | A_CREER |
| L-05 | Théorème Lean 05 | Entropy hold P4-19 | D13 + D14 | A_CREER |
| L-06 | Théorème Lean 06 | Path fidelity P4-20 | D13 + D14 | A_CREER |
| L-07 | Théorème Lean 07 | Trust boundary P4-16 | D13 + D14 | A_CREER |

**Distinction** : L-01 à L-07 (théorèmes kernel avec tiret) ≠ L01-L09 (lois logiques Brody sans tiret)

---

## Table 5 — Composants P4-32 à P4-35 (non nommés individuellement dans sources)

| Plage | Statut | Note |
|---|---|---|
| P4-32 | ITEM_LEVEL_NOT_AVAILABLE_IN_SOURCE_PDF | Composant kernel numéroté — nom non extrait PDF |
| P4-33 | ITEM_LEVEL_NOT_AVAILABLE_IN_SOURCE_PDF | Composant kernel numéroté — nom non extrait PDF |
| P4-34 | ITEM_LEVEL_NOT_AVAILABLE_IN_SOURCE_PDF | Composant kernel numéroté — nom non extrait PDF |
| P4-35 | ITEM_LEVEL_NOT_AVAILABLE_IN_SOURCE_PDF | Composant kernel numéroté — nom non extrait PDF |

---

## Invariants kernel non bypassables

| Invariant | Règle | Conséquence si violé |
|---|---|---|
| BLOCK > HOLD > ALLOW | Non inversible — ALLOW ne précède jamais BLOCK | Violation FAIL-CLOSED |
| TEST_PASS ≠ AUTHORIZED | Passer les tests ≠ être autorisé (P4-06) | Violation code_authorization_gate |
| SIGNED_DECISION_RECEIPT obligatoire | Toute décision → receipt.json signé | Décision non traçable |
| api_allowed_to_decide = False | API ne prend jamais de décision | Violation KX108_ONLY |
| does_not_authorize_action = true | Aucun agent/domaine n'autorise sans kernel | Bypass gate |
| entropy_hold_rule | Entropie > seuil → HOLD forcé (P4-19) | Instabilité non détectée |
| memory_write=false | Graphiti et mémoire : readonly permanent | Corruption mémoire |
| CORE_X108 = INTOUCHABLE | Fichiers kernel sealed — aucune édition | Invalidation chaîne crypto |
