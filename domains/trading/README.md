# Trading

> Domain Pack de référence historique pour les marchés financiers.
>
> **UDIP status : `EXISTING_REFERENCE`**  
> **Source type : `external_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Identité

Le domaine Trading représente un monde où des signaux de marché, des positions, un portefeuille et des capacités d'exécution peuvent produire des propositions d'action.

Dans UDIP, Trading sert de **référence historique de construction** : il aide à identifier ce qui est réellement universel dans un Domain Pack et ce qui doit rester strictement financier.

Le domaine Trading ne possède aucune autorité finale.

```text
marché
→ observation
→ cognition / agents
→ proposition
→ canonicalisation
→ gouvernance
→ KX108
→ Binder si exécution
→ broker / adapter si autorisé
→ outcome / receipt / replay
```

## 2. Statut réel

Le pack courant est un **scaffold UDIP**, pas un runtime Trading migré.

`domain_pack.yaml` déclare :

- `status: EXISTING_REFERENCE` ;
- `source_type: external_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

`object_map.yaml` est `REFERENCE_ONLY` et ne contient encore aucun objet UDIP implémenté.

`sources.yaml` est également `REFERENCE_ONLY` et précise qu'aucun code n'a été copié ou migré dans ce scaffold.

## 3. Sources historiques

Les références déclarées sont :

- `external://OBSIDIA_TRADING` ;
- `domains/trading/` ;
- `domain_packets/trading_decisional_form_v0.yaml` ;
- `sigma/domains/trading_agents.py`.

Ces sources servent d'évidence architecturale et de matière de comparaison. Elles ne deviennent pas automatiquement des composants du Core UDIP.

## 4. Sémantique propre au domaine

Les extensions déclarées sont :

- `market_data` ;
- `portfolio` ;
- `broker_execution`.

Les notions suivantes restent explicitement métier et ne doivent pas être généralisées dans `udip/` ou dans le Core :

- BUY / SELL ;
- broker ;
- Alpaca ;
- portfolio ;
- logique spécifique aux marchés.

UDIP peut normaliser la **forme du raccordement** de ces notions. Il ne doit pas absorber leur sens.

## 5. Éléments canoniques consommés

Le chemin cible doit utiliser les frontières universelles UDIP :

- `DomainSignal` ;
- `CanonicalDomainContract` ;
- `GovernancePayload` ;
- frontière d'autorité KX108 ;
- frontière Binder lorsqu'une exécution est envisagée ;
- Receipt / Replay / Proof surfaces.

Ces éléments appartiennent au contrat universel. Trading les consomme ; il ne les redéfinit pas comme une constitution locale.

## 6. Point de branchement cible

Le branchement attendu est :

```text
market / external stack
→ ExternalInputAdapter
→ Trading observation
→ agents / rules
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder permission
→ OutboundExecutionAdapter
→ broker / external executor
→ ExecutionOutcome
→ Receipt / Replay / Proof
```

Ce trajet est une **cible UDIP**. Le scaffold actuel ne l'implémente pas intégralement.

## 7. Gouvernance et droits

Invariants obligatoires :

```text
DOMAIN != AUTHORITY
DOMAIN SIGNAL != DECISION
PROPOSAL != ACTION
KX108_ONLY
```

Le domaine peut :

- observer des données de marché ;
- produire des signaux ou propositions ;
- exposer inconnues, contradictions, risques et références de preuve ;
- préparer une intention d'exécution.

Le domaine ne peut pas :

- transformer une proposition en ACT ;
- contourner KX108 ;
- contourner Binder pour une exécution gouvernée ;
- confondre capacité broker et permission d'exécution ;
- promouvoir sa sémantique dans le Universal Core.

## 8. Preuve / Receipt / Replay

Trading est la référence historique ayant motivé plusieurs distinctions UDIP autour de l'exécution, du receipt et du replay.

Mais le **scaffold présent dans ce dossier ne revendique pas ces preuves comme implémentées localement**.

`conformance.md` indique :

- statut `SCAFFOLD ONLY` ;
- aucun test UDIP implémenté dans ce scaffold ;
- conformance future à démontrer.

Toute preuve provenant du projet Trading historique doit donc rester explicitement référencée comme source externe ou historique.

## 9. Migration / provenance

Le pack actuel utilise une **référence externe** plutôt qu'une copie complète du projet Trading.

`sources.yaml` précise :

> Source mapping only. No code copied or migrated.

Cette séparation est volontaire : UDIP doit extraire le contrat universel sans fusionner le repository Trading dans le Core Obsidia.

## 10. Manques actuels

Les manques déclarés restent :

- adaptation UDIP-native du Domain Pack ;
- object map Core-neutral réel ;
- wrapper autour des surfaces historiques d'exécution ;
- tests de conformance UDIP ;
- démonstration explicite du trajet complet jusqu'à KX108 / Binder dans ce scaffold.

## 11. Règle de promotion

Trading ne doit quitter `SCAFFOLD_ONLY` que lorsque le raccordement UDIP est démontré sans ambiguïté :

```text
source externe
→ signal canonique
→ gouvernance
→ KX108
→ Binder
→ exécution bornée
→ receipt / replay
```

La présence d'un historique Trading mature ne suffit pas à déclarer le **pack UDIP** mature.
