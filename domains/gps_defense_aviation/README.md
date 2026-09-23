# GPS / Defense / Aviation

> Domain Pack de référence pour les mondes physiques critiques, l'authenticité de la réalité, le fail-closed et les preuves terrain.
>
> **UDIP status : `EXISTING_REFERENCE`**  
> **Source type : `repo_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Identité

Ce Domain Pack représente un domaine où les entrées ne sont pas seulement logicielles : GNSS, RF, capteurs, trajectoires et autres observations physiques peuvent être erronés, rejoués, incohérents ou hostiles.

GPS / Defense / Aviation force donc UDIP à distinguer :

```text
provenance d'une source
≠
authenticité du monde physique
```

Il sert de référence pour les extensions de réalité et les comportements fail-closed.

## 2. Statut réel

`domain_pack.yaml` déclare :

- `status: EXISTING_REFERENCE` ;
- `source_type: repo_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

`object_map.yaml` reste `REFERENCE_ONLY` avec aucun objet UDIP natif implémenté.

`sources.yaml` mappe les sources historiques mais précise qu'aucun code n'est copié ou migré par ce fichier de mapping.

Le domaine historique est riche ; le **pack UDIP lui-même reste un scaffold**.

## 3. Sources historiques

Les références principales sont :

- `domain_packets/gps_defense_aviation_decisional_form_v0.yaml` ;
- `domains/gps/` ;
- `sigma/domains/gps_defense_aviation_agents.py`.

Le manifeste brut de migration a également recensé des artefacts physiques et de preuve : résultats RINEX, RF enregistré, configurations GNSS, pipelines, tests, proof surfaces et documents de Reality Authenticity.

Ces éléments alimentent la construction du Domain Pack mais ne doivent pas être confondus avec un runtime UDIP déjà finalisé.

## 4. Sémantique propre au domaine

Extensions déclarées :

- `reality_authenticity` ;
- `sensor_attestation` ;
- `anti_replay` ;
- `physical_envelope`.

Concepts qui doivent rester métier :

- GNSS ;
- RF ;
- RINEX ;
- aircraft ;
- seuils capteurs ;
- logique de navigation et d'enveloppe physique.

Le Core peut transporter leurs références, risques et preuves. Il ne doit pas absorber leur sémantique.

## 5. Extension physique conditionnelle

GPS démontre pourquoi certains domaines ont besoin d'une frontière supplémentaire :

```text
Physical / RF Source
→ SourceProvenance
→ RealityAuthenticity checks
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
```

`RealityAuthenticity` est une **extension conditionnelle de domaine**, pas une obligation universelle pour tous les Domain Packs.

Elle ne remplace pas KX108.

## 6. Point de branchement cible

```text
GNSS / RF / sensor source
→ physical adapter
→ provenance
→ authenticity / freshness / anti-replay / coherence
→ GPS observation
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder si action
→ outbound / physical executor
→ ExecutionOutcome
→ Receipt / Replay / Proof
```

Le scaffold courant n'implémente pas encore cette chaîne sous une forme UDIP-native complète.

## 7. Gouvernance et droits

Invariants :

```text
DOMAIN != AUTHORITY
PROVENANCE != REALITY
EVIDENCE != AUTHORITY
SIMULATION != REALITY
KX108_ONLY
```

Le domaine peut :

- qualifier la qualité et la cohérence d'une observation physique ;
- exposer des signaux de spoofing, incohérence ou anti-replay ;
- fournir des références de preuve terrain ;
- proposer HOLD/BLOCK comme conséquence métier à examiner.

Le domaine ne peut pas :

- produire lui-même l'autorité finale ;
- transformer une preuve physique en ACT ;
- contourner KX108 ;
- contourner Binder lorsqu'une action réelle est gouvernée.

## 8. Preuve / Receipt / Replay

Le manifeste historique GPS recense un ensemble important d'artefacts classés `PROOF`, `FIXTURE`, `TEST`, `CONFIG`, `ADAPTER` et `PIPELINE`.

Cela montre que le domaine historique possède une matière de preuve et de terrain substantielle.

Mais `conformance.md` du Domain Pack actuel indique toujours :

- `SCAFFOLD ONLY` ;
- aucun test UDIP implémenté dans ce scaffold.

La preuve historique ne doit donc pas être requalifiée automatiquement en conformance UDIP.

## 9. Migration / provenance

Le manifeste brut GPS / Defense / Aviation a enregistré **237 copies**, avec les originaux laissés inchangés.

La compaction UDIP V0 a ensuite retiré les copies exactes déjà présentes dans le canon épinglé, tout en conservant les éléments divergents ou sans équivalent direct.

Le `migration_snapshot/` restant est donc particulièrement important ici : il peut contenir des artefacts physiques, configurations, résultats et tests qui n'ont pas d'équivalent courant direct dans `main`.

Ces éléments doivent être classés avant toute suppression supplémentaire.

## 10. Manques actuels

Manques déclarés ou structurels :

- adaptation UDIP-native du Domain Pack ;
- mapping explicite des extensions physiques conditionnelles ;
- object map Core-neutral réel ;
- migration runtime UDIP non réalisée ;
- tests de conformance UDIP ;
- séparation formalisée entre provenance, authenticité, preuve et autorité dans le pack natif ;
- classification finale des snapshots physiques résiduels.

## 11. Règle de promotion

GPS / Defense / Aviation ne doit quitter `SCAFFOLD_ONLY` qu'après démonstration du chemin :

```text
source physique
→ authenticité
→ signal canonique
→ gouvernance
→ KX108
→ Binder si nécessaire
→ outcome
→ receipt / replay / preuve
```

La difficulté du domaine n'autorise aucune exception à `KX108_ONLY`.
