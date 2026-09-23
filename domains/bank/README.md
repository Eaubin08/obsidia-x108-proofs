# Bank

> Domain Pack de référence pour la banque, les paiements, la fraude, la conformité et les frontières d'audit.
>
> **UDIP status : `EXISTING_REFERENCE`**  
> **Source type : `repo_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Identité

Le domaine Bank représente des opérations financières gouvernées : paiements, transferts, détection de fraude, contraintes de conformité et politiques bancaires.

Il sert de référence pour tester une question centrale de UDIP : comment un domaine riche en règles métier peut-il traduire ses risques et contraintes vers Obsidia sans devenir lui-même l'autorité ?

```text
transaction / événement bancaire
→ analyse métier
→ signal / proposition
→ canonicalisation
→ gouvernance
→ KX108
→ Binder si exécution
→ capacité bancaire autorisée
→ outcome / receipt / replay
```

## 2. Statut réel

Le pack courant est un scaffold de migration et de normalisation.

`domain_pack.yaml` déclare :

- `status: EXISTING_REFERENCE` ;
- `source_type: repo_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

`object_map.yaml` reste `REFERENCE_ONLY` avec `objects: []`.

`sources.yaml` est également `REFERENCE_ONLY`.

Le domaine possède donc des sources historiques substantielles, mais **aucun object map UDIP natif ni runtime UDIP complet n'est encore revendiqué ici**.

## 3. Sources historiques

Les sources déclarées sont :

- `domain_packets/bank_decisional_form_v0.yaml` ;
- `domains/bank/` ;
- `sigma/domains/bank_agents.py` ;
- `examples/bank_normal.json` ;
- `examples/bank_suspicious.json`.

Le manifeste de migration historique recense aussi un ensemble plus large de code, pipelines, fixtures, tests, documents et preuves utilisés pour reconstruire la surface Bank.

Ces sources sont de la matière de référence. Elles ne donnent aucune autorité au Domain Pack.

## 4. Sémantique propre au domaine

Extensions déclarées :

- `fraud` ;
- `compliance` ;
- `bank_policy`.

Concepts à ne pas généraliser :

- fraude ;
- AML ;
- sanctions ;
- payment rails ;
- règles et limites bancaires.

Ces éléments restent dans Bank. Le Core ne doit connaître que la forme nécessaire à leur gouvernance.

## 5. Éléments canoniques consommés

Le Domain Pack doit se raccorder aux frontières universelles :

- `DomainSignal` ;
- `CanonicalDomainContract` ;
- `GovernancePayload` ;
- KX108 ;
- Binder lorsque l'action financière doit être autorisée ;
- Receipt / Replay / Proof surfaces.

Une règle bancaire peut produire un risque ou une contrainte. Elle ne produit pas la décision finale KX108.

## 6. Point de branchement cible

```text
bank source / transaction
→ Bank adapter / observation
→ agents / rules / fraud / compliance
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder permission
→ bank execution adapter
→ ExecutionOutcome
→ Receipt / Replay / Proof
```

Le pack actuel ne revendique pas encore ce trajet complet comme runtime UDIP migré.

## 7. Gouvernance et droits

Invariants :

```text
DOMAIN != AUTHORITY
RISK != DECISION
PROPOSAL != ACTION
KX108_ONLY
```

Bank peut :

- qualifier une transaction ;
- détecter des signaux de fraude ou de conformité ;
- exposer contradictions, inconnues, risques et evidence refs ;
- proposer une action ou un refus métier.

Bank ne peut pas :

- créer ACT ;
- contourner KX108 ;
- contourner Binder ;
- confondre politique bancaire et autorité globale ;
- traiter un résultat d'exécution comme une décision.

## 8. Preuve / Receipt / Replay

Le manifeste historique Bank contient des références à des scénarios, benchmarks, replay, fuzzing, sécurité et validations.

Mais le **scaffold UDIP courant** reste explicitement `SCAFFOLD_ONLY`.

`conformance.md` précise qu'aucun test UDIP n'est implémenté dans ce scaffold.

Les preuves historiques doivent donc être lues comme **sources de référence à intégrer ou mapper**, pas comme preuve automatique de conformance UDIP V0.

## 9. Migration / provenance

Le manifeste brut de migration Bank a enregistré **131 copies** réparties entre adapters, code, config, documentation, fixtures, legacy, pipelines, proof et tests, avec les originaux laissés inchangés.

Après la compaction UDIP V0, les copies byte-identiques au canon épinglé ont été retirées et leur provenance déplacée dans `udip/provenance/MIGRATION_REFERENCE_INDEX_V0.csv`.

Le `migration_snapshot/` restant ne doit donc être lu que comme **provenance résiduelle ou divergence historique**, jamais comme copie de production du domaine Bank.

## 10. Manques actuels

Manques déclarés :

- adaptation UDIP-native du Domain Pack ;
- object map Core-neutral réel ;
- migration runtime non réalisée ;
- tests UDIP propres au pack ;
- preuve explicite de la frontière Binder dans le trajet UDIP ;
- classification des artefacts historiques restants entre référence, divergence et matériel réellement domaine-spécifique.

## 11. Règle de promotion

Bank pourra quitter `SCAFFOLD_ONLY` quand la chaîne suivante sera démontrée sans réutiliser implicitement les snapshots comme runtime :

```text
source bancaire
→ sémantique Bank
→ signal canonique
→ KX108
→ Binder
→ exécution bornée
→ receipt / replay / preuve
```

La maturité historique Bank et la maturité du **Domain Pack UDIP** restent deux choses distinctes.
