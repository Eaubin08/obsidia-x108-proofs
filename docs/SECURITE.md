# Sécurité d'Obsidia

> Guide rédigé le 2026-09-15 à partir du code. Les liens **(H)** pointent vers la branche [`integration/harness-runtime-binder-v1`](https://github.com/Eaubin08/obsidia-x108-proofs/tree/integration/harness-runtime-binder-v1).
> À lire avec : [Comprendre Obsidia](COMPRENDRE_OBSIDIA.md) · [Trajets de la donnée](TRAJETS.md) · [Entraînement, éducation, naissance](EDUCATION.md).

---

## L'idée : la sécurité est dans l'architecture, pas dans un filtre

Les garde-fous habituels de l'IA sont **comportementaux** : prompts, fine-tuning, filtres. Ils fonctionnent jusqu'au jour où ils ne fonctionnent plus, et rien ne prouve alors qu'ils étaient là.

Obsidia met la sécurité **dans la forme du système** :

```text
Personne ne peut agir sauf X-108.   Personne ne peut écrire la vérité sauf par validation humaine.
Tout ce qui n'est pas autorisé est refusé (fail-closed).   Chaque garantie est testée ou prouvée.
```

La sécurité tient en **sept couches techniques** qui se recouvrent, plus une huitième encore en vision. Si l'une échoue, les autres tiennent.

---

## 1. L'autorité isolée

- **Une seule autorité** : le noyau X-108 (`KX108_ONLY`). Il juge **avant** l'exécution et rend `ACT`, `HOLD` ou `BLOCK`. En cas de doute, il retient ou bloque (fail-closed). Voir [`KERNEL_OVERVIEW.md`](KERNEL_OVERVIEW.md).
- **Chaque module déclare ses non-droits** dans un bloc `BOUNDARY` écrit en dur : `emits_act=false`, `allowed_to_decide=false`, `memory_write=false`, `kernel_mutation=false`, `decision_authority="KX108_ONLY"`. C'est le cas de Brody, MEMZUM, la mémoire native, OS Trad, les calibrateurs, les agents…
- **Les invariants du noyau sont prouvés** : Lean 4 et TLA+ ([couche 24](couches/24_FORMAL_METHODS.md)).

### 1.1 Comprendre, proposer, décider, agir

Obsidia se protège d'abord en séparant les verbes :

| Verbe | Organe possible | Produit | Limite |
|---|---|---|---|
| comprendre | OS Trad, Brody, domaines | représentation, contexte, lecture située | ne donne aucune permission |
| proposer | Brody, Obsidure, domaines | option candidate, patch, trajectoire | reste possible, pas réel |
| vérifier | Sigma, tests, Lean, ProofKit, replay | contradiction, résultat, preuve bornée | ne décide pas |
| décider | X-108 | `ACT`, `HOLD`, `BLOCK` | autorité unique |
| agir | executor borné après autorisation | effet réel ou dry-run | doit produire receipt et conséquence vérifiable |

La capacité technique d'un organe ne vaut donc jamais autorité. Un outil peut savoir modifier un fichier ; cela ne veut pas dire qu'il a le droit de le faire. Un domaine peut comprendre un risque ; cela ne veut pas dire qu'il peut trancher. Brody peut formuler une réponse ; cela ne veut pas dire qu'il peut agir.

## 2. La non-souveraineté, testée

Le dossier [`tests/non_sovereignty/`](../tests/non_sovereignty/) vérifie, **organe par organe**, qu'aucun ne peut prendre le pouvoir. Il contient 35 tests, par exemple :

| Organe | Tests |
|---|---|
| Brody | `test_brody_no_act`, `test_brody_no_decision`, `test_brody_response_never_emits_verdict` |
| Sigma et périphérie | `test_sigma_cannot_bypass_x108`, `test_periphery_cannot_emit_act`, `test_control_plane_cannot_emit_act` |
| Agents | `test_agents_cannot_emit_act`, `test_agent_no_direct_internet` |
| Mémoire | `test_memory_cannot_decide`, `test_memory_promotion_not_automatic`, `test_memory_candidate_ledger_no_promotion` |
| Contexte et ingress | `test_context_packet_no_authority`, `test_x108_context_ingress_readonly_only` |
| Valeur | `test_gencoin_cannot_authorize`, `test_gencoin_tokenization_blocked`, `test_energy_cannot_authorize`, `test_timeverse_cannot_authorize` |
| Blockchain et clés | `test_no_private_key_access`, `test_no_wallet_connection`, `test_no_real_chain_tx`, `test_no_token_mint`, `test_no_smart_contract_deploy`, `test_transaction_simulator_never_broadcasts`, `test_signature_boundary_blocks_all_signing` |
| Action | `test_world_action_gateway_dry_run`, `test_world_action_no_real_act_v4`, `test_internal_demo_flows_no_real_act` |

## 3. La défense de Brody contre les messages

Tout se passe dans le [trajet de la cognition](TRAJETS.md#1-le-trajet-de-la-cognition--comment-brody-répond) :

| Menace | Défense | Où |
|---|---|---|
| **Fuite de secret** (clé API, clé privée, token, mot de passe) | filtre dès l'entrée (preflight), puis nettoyage du texte de réponse, puis nettoyage profond de toute la charge renvoyée, y compris paquets et traces | [`brody_secret_scrubber.py`](../apps/obsidia_api/brody_secret_scrubber.py) |
| **Tentative de contournement** : « bypass », « ignore X108 », « désactive X108 », « modifie le kernel », « écris en mémoire canonique », « agis comme si tu pouvais »… | détection adversariale dans le micro-core et le fastpath, avec réponse de refus structurée | [`brody_cognitive_micro_core.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_cognitive_micro_core.py) **(H)** |
| **Demande irréversible** : « supprime définitivement », « reset --hard », « drop table », « wipe memory »… | signal de réversibilité ; balance P0 = HOLD ; la couche *autorité* est toujours active | micro-core et [`brody_balance_engine.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_balance_engine.py) **(H)** |
| **Usurpation d'autorité** dans le texte : `admin:`, `root:`, `system:`, `kernel:`, `sudo:`, `override:` | marqueurs repérés au routage de langue | [`language_router.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/periphery/language/language_router.py) **(H)** |
| **Mots d'autorité glissés dans le contexte** : ALLOW, HOLD, BLOCK, ACT, DECIDE, VERDICT, EXECUTE, DEPLOY… | le ContextPacketV2 les détecte et les signale | [`context_packet_builder_v2.py`](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/periphery/context/context_packet_builder_v2.py) **(H)** |
| **Injection dans le savoir éducatif** | garde à deux niveaux (clés interdites + valeurs sentinelles), sinon BLOCK | [`brody_education_pack_v1_readonly_adapter.py`](../apps/obsidia_api/brody_education_pack_v1_readonly_adapter.py) |
| **Glissement de sens** entre compréhension et action | calibration C275, halo de sens final C277, validation du sens de l'action C278 | [`periphery/language/`](https://github.com/Eaubin08/obsidia-x108-proofs/tree/integration/harness-runtime-binder-v1/periphery/language) **(H)** |

## 4. La mémoire protégée

- **Pas d'écriture pendant une conversation** : la garde de promotion impose `memory_write`, `canon_promotion` et `memory_promotion` à `false`.
- **Pas d'auto-promotion** : un souvenir reste *candidat* jusqu'à une **validation humaine**, un essai à blanc, une porte de revue et une **écriture manuelle gardée** ([trajet du savoir](TRAJETS.md#2-le-trajet-du-savoir--comment-une-information-devient-mémoire)).
- **Mémoire locale** : l'index natif est lu sans réseau ni service externe, ce qui écarte toute fuite vers un tiers.
- **Apprendre sans être contaminé** : une attaque refusée devient une leçon `adversarial_rejection_lesson`, pas un souvenir. Les leçons passent par un filtre de secrets ([Entraînement, éducation, naissance § 8.3](EDUCATION.md)).

## 5. L'action bornée

- **Obsidure** peut inspecter, proposer un patch, tester en sandbox et produire une preuve, mais **jamais commit, push ni promotion automatique**.
- **OS Trad** ne produit que des propositions **à blanc** (`DRY_RUN_ONLY`) et refuse les intentions `ACTION`.
- **Les actions sur le monde** passent par une passerelle HOLD/BLOCK en **sandbox** et un bus d'action en **dry-run**. Aujourd'hui, aucune action réelle n'est émise par Brody.
- **Pas d'accès direct à internet** pour les agents ; pas de clés, de wallets, de transactions réelles ni de mint côté blockchain (voir § 2).

### 5.1 Irréversibilité, conséquence et receipt

Le Runtime Binder et X-108 doivent séparer trois choses :

```text
capacité détectée ≠ autorité accordée ≠ conséquence vérifiée
```

Une action irréversible exige au minimum : provenance, permissions, état des unknowns, contradictions, pré-exécution ou simulation, verdict `ACT/HOLD/BLOCK`, receipt, attestation, anti-replay, puis comparaison entre intention et conséquence. Sans ces éléments, le bon état est HOLD ou BLOCK, même si un organe sait techniquement quoi faire.

Dans l'état documenté au 2026-09-15, ce chemin reste majoritairement dry-run ou sandbox. Il ne faut donc pas présenter ACT comme production physique générale.

### 5.2 Classes de risque

Une demande n'a pas le même statut selon ce qu'elle peut casser :

| Classe | Exemple | Exigence minimale |
|---|---|---|
| consultatif | expliquer une couche, résumer un document | sources et statut clair |
| local réversible | modifier un brouillon, générer un rapport | diff, validation, rollback simple |
| local sensible | toucher un fichier de preuve, de sécurité ou de configuration | accord explicite, plan, tests, contrôle de portée |
| externe | envoyer un mail, appeler une API, publier | permission, preview, receipt |
| financier / blockchain | ordre, transfert, signature, mint | sandbox par défaut, preuve de non-broadcast, autorité humaine |
| physique | trajectoire, machine, capteur critique | fraîcheur, attestation, anti-replay, causalité, fail-closed |

### 5.3 Causalité de sécurité

Le schéma réel doit toujours rester lisible :

```text
entrée
-> règle ou calcul appliqué
-> statut obtenu
-> seuil ou interprétation
-> conséquence
```

Exemples :

| Entrée | Règle ou calcul | Statut | Conséquence |
|---|---|---|---|
| "ignore X108" | détection adversariale | contournement | BLOCK ou refus structuré |
| "supprime définitivement" | réversibilité P0 | irréversible | HOLD avant toute action |
| signal GPS ancien | freshness | donnée périmée | HOLD |
| deux sources se contredisent | Sigma / conflit | contradiction | HOLD, demande de preuve |
| preuve Lean hors périmètre | mapping preuve-runtime | preuve non applicable | ne pas promouvoir |
| clé privée dans l'entrée | scrubber secrets | secret détecté | blocage/nettoyage |

Le fail-closed n'est pas une panne : c'est une propriété. Si la provenance, la fraîcheur, la preuve, la causalité, la réversibilité ou l'autorité sont insuffisantes, le système doit s'arrêter avant le réel.

## 6. L'intégrité du code et des preuves

| Protection | Rôle | Où |
|---|---|---|
| **Portée protégée** | noyau, sceaux Merkle, ancres RFC3161, specs Lean et TLA+, fichiers gelés : aucune modification sans accord et plan de vérification | [`.claude/context/PROTECTED_SCOPE.md`](../.claude/context/PROTECTED_SCOPE.md) |
| **Gate de frontière du noyau** | signale tout chemin protégé modifié ou indexé (noyau, Sigma Core, Lean, sceaux, TLA+, runtime, apps) | [`obsidia_kernel_boundary_check.py`](../scripts/gates/obsidia_kernel_boundary_check.py) |
| **Sceaux et manifestes** | empreintes SHA-256 et racine Merkle : toute modification silencieuse devient détectable | [`MANIFEST_SHA256.json`](../MANIFEST_SHA256.json), [couche 25](couches/25_OS3_PROOF_REPLAY_ATTESTATION.md) |
| **Pont noyau scellé** | `server.kernel.sealed.cjs` est tamper-evident et ne doit jamais être modifié | [couche 16](couches/16_X108_AUTHORITY_KERNEL.md) |

## 7. La publication et la gouvernance du dépôt

| Protection | Rôle | Où |
|---|---|---|
| **Scan de secrets en CI** | TruffleHog et Gitleaks à chaque changement | [`.github/workflows/secret-scan.yml`](../.github/workflows/secret-scan.yml) |
| **Contenu interdit** | refuse les dépendances locales et les motifs de secrets (`private_key`, `seed_phrase`, `mnemonic`, `keystore`…) | [`check_forbidden_content.py`](../scripts/check_forbidden_content.py) |
| **Gate de publication** | vérification des preuves, du contenu interdit et de la rotation des secrets avant publication | [`PUBLICATION_SECURITY_GATE_CLEAN.md`](security/PUBLICATION_SECURITY_GATE_CLEAN.md) |
| **Rotation des secrets** | plan de rotation après P80 | [`POST_P80_SECRET_ROTATION_PLAN.md`](security/POST_P80_SECRET_ROTATION_PLAN.md) |
| **Protection des branches** | politique et audit de sécurité GitHub | [`BRANCH_PROTECTION_POLICY.md`](security/BRANCH_PROTECTION_POLICY.md), [`GITHUB_SECURITY_AUDIT.md`](security/GITHUB_SECURITY_AUDIT.md) |
| **Checklist avant publication** | liste de contrôle | [`PRE_PUBLICATION_SECURITY_CHECKLIST.md`](security/PRE_PUBLICATION_SECURITY_CHECKLIST.md) |
| **Conformité RSSI / RGPD** | spécifications de conformité et de gouvernance des données | [`runtime_contracts/rssi_rgpd_compliance_spec/`](../runtime_contracts/rssi_rgpd_compliance_spec/) |
| **Signalement de vulnérabilité** | canal privé, sans issue publique | [`SECURITY.md`](../SECURITY.md) |

## 8. La continuité identitaire *(doctrine, vision)*

Le kernel protège la décision présente, Lean protège des énoncés formels, les receipts protègent la traçabilité. Le principe d'**une seule naissance** ajoute une protection du **sens** :

> Une règle isolée peut être contournée ou réinterprétée. **Une identité qui connaît la généalogie de ses principes peut détecter la rupture de sens.**

Il empêche la multiplication anarchique des identités, la souveraineté concurrente des agents (*« des agents qui restent bêtes »*), la falsification silencieuse de l'histoire et l'assimilation d'une nouvelle doctrine à la doctrine originelle. Voir le § 10 d'[Entraînement, éducation, naissance](EDUCATION.md). *Oxygen n'est pas encore construit.*

---

## Ce que la sécurité ne prétend pas

- Les théorèmes Lean prouvent **le noyau et des propriétés bornées**, pas le runtime complet (README § 20).
- Plusieurs protections d'action sont aujourd'hui en **sandbox ou dry-run** : elles montrent la frontière, elles n'ont pas encore été éprouvées sur des actions réelles.
- Les détections par motifs (contournement, irréversibilité, secrets) couvrent ce qu'elles connaissent. C'est pour cela qu'elles sont **doublées** par l'isolement de l'autorité, qui ne dépend d'aucun motif.
