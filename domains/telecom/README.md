# Telecom

> Domain Pack pour réseaux, connectivité et observation non souveraine des signaux physiques ambiants.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Source type : `mixed_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Telecom possède désormais un **périmètre documentaire V0 explicite**, sans prétendre à un runtime implémenté.

Le pack reste unique, mais il contient deux familles internes qui ne doivent pas être confondues :

```text
TELECOM
│
├── NETWORK / CONNECTIVITY
│   ├── network state
│   ├── connector identity
│   ├── egress capability
│   ├── availability / freshness
│   └── gateway / endpoint constraints
│
└── PHYSICAL SIGNAL OBSERVATION
    ├── Wi-Fi / RF / radio
    ├── satellite / GNSS
    ├── UWB / radar / SDR / Bluetooth
    ├── propagation changes
    ├── interference
    ├── physical coherence
    └── world-state candidates
```

Ces deux familles partagent provenance, temporalité, cohérence, réseau et signal, mais elles ne produisent pas le même sens métier.

## 2. Statut réel

Le pack reste :

- `status: NEW_DOMAIN_SCAFFOLD` ;
- `source_type: mixed_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

La synchronisation actuelle reconnaît des **sources de conception auditées**.

Elle ne signifie pas :

- runtime Telecom branché ;
- object map implémenté ;
- adapter Telecom actif ;
- preuve de terrain Telecom complète ;
- capacité d'exécution réseau ;
- surveillance d'individus ;
- autorité Telecom.

`object_map.yaml` reste volontairement vide.

## 3. Famille A — Network / Connectivity

Source repository principale :

- [P70 — Network Egress & Connectors Audit](../../docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md)

P70 distingue notamment :

- aucune sortie réseau ;
- localhost ;
- connecteur dry-run ;
- connecteur actif à revoir ;
- Graphiti / Neo4j ;
- sortie marché externe ;
- sortie bloquée.

Cette matière fournit une base pour représenter :

```text
network source
→ connector identity / class
→ egress capability
→ freshness / availability
→ policy / constraints
→ Telecom DomainSignal
→ KX108
→ Binder si conséquence
```

P70 reste un audit transversal. Il ne constitue pas, seul, une architecture opérateur télécom.

## 4. Famille B — Physical Signal Observation

Les sources conceptuelles internes du projet décrivent explicitement :

```text
Wi-Fi
RF
telecom
satellite
GNSS/GPS
radar
UWB
SDR
Bluetooth
```

comme instruments possibles d'observation physique indirecte.

Intuition historique :

```text
le monde déforme le signal
→ la déformation contient une trace
→ la trace peut produire une observation candidate du monde
```

Formulation historique :

```text
bruit télécom
→ trace physique
→ donnée monde potentielle
```

Le mot important est **potentielle**.

Le signal n'est ni la vérité, ni une identité, ni une décision.

## 5. Physical Signal Periphery

Une source interne plus récente place cette idée dans une couche `PHYSICAL_SIGNAL_PERIPHERY`.

Sorties candidates documentées :

- `PhysicalSignalReport` ;
- `PhysicalSignalEvent` ;
- `WorldStateCandidate` ;
- `PhysicalCoherenceScore` ;
- `SignalContradictionScore` ;
- `ReplayablePhysicalProofCandidate` ;
- `PhysicalRiskHint`.

Verrous de conception issus de cette source :

- la couche ne décide jamais ;
- elle ne donne jamais ACT ;
- elle ne doit pas devenir une couche de surveillance individuelle ;
- elle produit uniquement observations, indices, contradictions, alertes, preuves candidates et scores de cohérence.

Ces objets restent **candidats** : ils ne sont pas encore admis dans `object_map.yaml`.

## 6. Gateway, fraîcheur et anti-replay

Source repository :

- [C471 — gateway_before_endpoint_prefilter](../../specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml)

Pattern :

```text
Agent/API
→ TemporalGateway
→ KX108
→ WorldActionGateway
```

Invariants pertinents :

- `gateway_is_prefilter_not_decider` ;
- `KX108_ONLY` ;
- aucun signal externe n'émet ACT ;
- aucun signal externe ne mute le kernel ;
- une action exige une décision KX108 et de la preuve.

Pour Telecom, un gateway peut donc :

- mesurer la fraîcheur ;
- détecter stale/replay ;
- qualifier une identité de connecteur ;
- préfiltrer un candidat ;
- produire une evidence surface.

Il ne devient pas l'autorité finale.

## 7. Extensions déclarées V0

`domain_pack.yaml` reconnaît maintenant six extensions documentaires :

### Network / Connectivity

- `network_connectivity`
- `network_egress`
- `gateway_constraints`

### Physical Signal

- `physical_signal_observation`
- `signal_provenance`
- `signal_coherence`

Ces extensions définissent le **périmètre de conception** du pack.

Elles ne valent ni implémentation, ni object map, ni runtime.

## 8. Frontière avec GPS / Defense / Aviation

GPS et Telecom peuvent lire certains instruments communs, mais ils n'interprètent pas le même monde.

```text
GPS / Defense / Aviation
→ position
→ navigation
→ authenticité GNSS
→ trajectoire / enveloppe physique

Telecom
→ connectivité
→ propagation
→ réseau
→ disponibilité
→ signal ambiant
→ cohérence du champ
```

Une même observation RF peut alimenter plusieurs Domain Packs.

La canonicalisation doit conserver son origine et empêcher une sémantique Telecom d'être confondue avec une sémantique GPS.

## 9. Source model

Le pack utilise `source_type: mixed_reference` parce que deux classes de matière sont reconnues.

### REPO_SOURCE

Sources présentes dans ce dépôt et directement auditables :

- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

### INTERNAL_CONCEPT_SOURCE

Sources de conception internes consultées lors de l'audit, mais non importées dans ce dépôt :

- “Compte-rendu projet — Physical Signal World Model” ;
- “suite pepite implementé 02.7” ;
- “OBSIDIA_V5_Texte_Continu_Edition_Livre_2026-08-18”.

Ces documents peuvent justifier une direction de conception.

Ils ne deviennent pas des dépendances runtime.

## 10. Non-souveraineté

Invariants Telecom :

```text
NETWORK ACCESS != AUTHORITY
NETWORK STATE != DECISION
SIGNAL != TRUTH
SIGNAL PROVENANCE != REALITY AUTHENTICITY
GATEWAY != DECIDER
EGRESS CAPABILITY != EXECUTION PERMISSION
WORLD STATE CANDIDATE != WORLD FACT
DOMAIN != AUTHORITY
KX108_ONLY
```

## 11. Non-surveillance

Le Physical Signal World Model est documenté comme **non-identitaire**.

Le Domain Pack V0 ne revendique donc pas :

- identification d'une personne à partir d'un signal ;
- suivi individuel ;
- profilage individuel ;
- transformation d'une présence probable en identité certaine.

Une future extension qui toucherait à ces sujets demanderait une nouvelle frontière explicite, un audit légal/privacy et une admission séparée.

## 12. Point de branchement cible

### Network path

```text
network / connector source
→ connector identity
→ network observation
→ egress / freshness constraints
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ Binder si conséquence
→ execution adapter si autorisé
→ Receipt / Replay
```

### Physical signal path

```text
RF / Wi-Fi / satellite / UWB / radar / SDR
→ source provenance
→ signal observation
→ physical coherence / contradiction
→ WorldStateCandidate
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
```

Ces chemins sont des cibles architecturales.

Ils ne sont pas encore branchés par le Domain Pack.

## 13. Conformance

Le profil de conformance Telecom impose désormais, au niveau documentaire :

```text
SIGNAL != TRUTH
NETWORK ACCESS != AUTHORITY
GATEWAY != DECIDER
EGRESS CAPABILITY != PERMISSION
PHYSICAL OBSERVATION != IDENTITY
KX108_ONLY
```

Les tests correspondants restent à créer.

Voir [conformance.md](conformance.md).

## 14. Manques

Le pack reste incomplet sur :

- object map ;
- objets canoniques Telecom ;
- adapters inbound ;
- distinction formelle observation RF / authenticité ;
- modèle de topology/link/service state ;
- Binder path pour egress ;
- receipts spécifiques ;
- replay spécifique ;
- tests Telecom ;
- preuve de non-surveillance ;
- validation des sources internes comme artefacts canoniques si elles doivent être promues.

## 15. Prochaine étape

Le prochain geste n'est **pas** d'ajouter du runtime.

Il faut construire en READ_ONLY le candidat `object_map.yaml` à partir des deux familles maintenant figées, puis décider quels objets sont réellement domaine-spécifiques et lesquels restent seulement transverses.
