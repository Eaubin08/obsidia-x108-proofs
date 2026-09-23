# Telecom

> Domain Pack futur pour réseaux, connectivité et signaux physiques ambiants.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Telecom est actuellement un scaffold vide côté manifeste, mais l'historique du projet contient une vision beaucoup plus forte que ce que le dossier laisse voir.

Cette vision possède deux axes :

1. **network / connector governance** : comprendre et borner les sorties réseau, les connecteurs, les gateways et les endpoints ;
2. **Physical Signal World Model** : utiliser les perturbations des signaux déjà présents dans le monde comme observations physiques indirectes.

## 2. Axe réseau / connecteurs

Source principale :

- [P70 — Network Egress & Connectors Audit](../../docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md)

P70 distingue notamment :

- aucune sortie réseau ;
- localhost ;
- connecteur dry-run ;
- connecteur actif à revoir ;
- Graphiti/Neo4j ;
- sortie marché externe ;
- sortie bloquée.

Cette classification fournit une base pour un futur modèle Telecom de :

```text
network source
→ connector class
→ egress capability
→ risk / policy
→ DomainSignal
→ KX108
→ permission
```

Elle ne constitue pas encore une sémantique opérateur télécom.

## 3. Axe Physical Signal World Model

Des notes internes du projet décrivent explicitement :

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

comme capteurs physiques indirects.

Intuition :

```text
le monde déforme le signal
→ la déformation contient de l'information
→ cette information peut produire une observation du monde
```

La formulation historique est :

```text
bruit télécom
→ trace physique
→ donnée monde potentielle
```

Le but n'est pas de prétendre que le signal donne “la vérité du monde”, mais de produire des phénomènes probables accompagnés de provenance et de limites.

## 4. Peripheral Mesh

Une source interne plus récente place cette idée dans `PHYSICAL_SIGNAL_PERIPHERY`.

Sorties candidates décrites :

- `PhysicalSignalReport` ;
- `PhysicalSignalEvent` ;
- `WorldStateCandidate` ;
- `PhysicalCoherenceScore` ;
- `SignalContradictionScore` ;
- `ReplayablePhysicalProofCandidate` ;
- `PhysicalRiskHint`.

Verrou explicite de cette source :

- la couche ne décide jamais ;
- elle ne donne jamais ACT ;
- elle ne doit pas devenir une couche de surveillance individuelle ;
- elle ne produit que des indices, contradictions, alertes, preuves candidates et scores.

## 5. Gateway et temporalité

Le composant :

- [C471 gateway_before_endpoint_prefilter](../../specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml)

décrit un pattern :

```text
Agent/API
→ TemporalGateway
→ KX108
→ WorldActionGateway
```

avec `gateway_is_prefilter_not_decider`.

Ce pattern est directement pertinent pour Telecom : un réseau ou gateway peut filtrer, authentifier, mesurer fraîcheur et anti-replay sans devenir l'autorité finale.

## 6. Ce que Telecom pourrait posséder

**Vision candidate — non implémentée :**

- topology / network segment ;
- link state ;
- signal observation ;
- egress capability ;
- connector identity ;
- radio / RF observation ;
- freshness ;
- interference ;
- availability ;
- physical-signal provenance.

Ces objets ne sont pas encore dans `domain_pack.yaml`.

## 7. Frontière avec GPS

GPS et Telecom peuvent partager des sources RF, mais leur sens diffère.

```text
GPS:
navigation / position / authenticité GNSS

Telecom:
connectivité / propagation / réseau / signal ambiant
```

Une même mesure RF peut alimenter plusieurs Domain Packs sans que ceux-ci fusionnent.

## 8. Non-souveraineté

```text
NETWORK ACCESS != AUTHORITY
SIGNAL != TRUTH
GATEWAY != DECIDER
EGRESS CAPABILITY != EXECUTION PERMISSION
DOMAIN != AUTHORITY
KX108_ONLY
```

## 9. État réel

Le pack reste officiellement :

- `source_type: none` ;
- `extensions: []` ;
- `sources.yaml: NOT_YET_DEFINED` ;
- `SCAFFOLD_ONLY`.

La vision Physical Signal est donc **une source de conception à intégrer**, pas une implémentation déclarée.

## 10. Sources

Repository :

- [P70 Network Egress Audit](../../docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md)
- [C471 Gateway Before Endpoint](../../specs/external_signals/component_specs/C471_gateway_before_endpoint_prefilter.yaml)
- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)

Sources internes consultées, non importées dans ce dépôt :

- “Compte-rendu projet — Physical Signal World Model” ;
- “suite pepite implementé 02.7” ;
- “OBSIDIA_V5_Texte_Continu_Edition_Livre_2026-08-18”.

## 11. Prochaine étape

Avant tout runtime Telecom :

1. figer le périmètre entre réseau logique et signal physique ;
2. déclarer les extensions dans `domain_pack.yaml` ;
3. construire un object map ;
4. séparer observation RF, authenticité, identité réseau et autorité ;
5. écrire les tests de non-surveillance et de non-souveraineté.
