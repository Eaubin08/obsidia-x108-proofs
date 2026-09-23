# UDIP Branch Map

## 1. But de cette carte

Cette carte décrit la forme de la branche `codex/udip-domain-packs-v0` après la compaction des snapshots de migration.

Elle ne décrit pas un nouveau runtime. Elle explique où se trouvent les contrats universels, les Domain Packs, les éléments transverses, les sources de planification et les artefacts de provenance.

## 2. Vue d'ensemble

```text
obsidia-x108-proofs/
│
├── docs/
│   └── UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md
│
├── udip/
│   ├── README.md
│   ├── BRANCH_MAP.md
│   ├── DOMAIN_PACK_STANDARD.md
│   ├── SOURCE_TAXONOMY_V0.md
│   ├── domain_registry.yaml
│   └── provenance/
│       ├── MIGRATION_COMPACTION_V0.md
│       └── MIGRATION_REFERENCE_INDEX_V0.csv
│
├── domains/
│   ├── trading/
│   ├── bank/
│   ├── gps_defense_aviation/
│   ├── ecom/
│   ├── industry_maintenance/
│   ├── btp_construction/
│   ├── logistics_supply_chain/
│   ├── cybersecurity/
│   ├── energy_critical_infrastructure/
│   ├── insurance/
│   ├── legal_compliance/
│   ├── telecom/
│   ├── facility_management/
│   ├── administration/
│   ├── health/
│   └── hr/
│
├── cross_domain/
│   └── meta/
│
└── planning/
    ├── source_inventory.md
    └── do_not_generalize.md
```

Les autres dossiers du dépôt appartiennent au canon, à l'historique ou aux autres couches d'Obsidia. Leur présence dans la branche ne signifie pas qu'ils deviennent des composants UDIP.

## 3. `docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md`

Rôle : **contrat architectural source**.

Il définit :

- le périmètre de UDIP V0 ;
- les invariants universels ;
- la frontière Core / Domain Pack ;
- le trajet inbound ;
- le Canonical Domain Path ;
- la frontière KX108 ;
- la séparation KX108 / Binder ;
- l'exécution outbound ;
- Receipt / Replay / Proof ;
- les extensions physiques et humaines conditionnelles.

Statut actuel : `SPEC_ONLY`. Il ne faut pas lire cette spécification comme la preuve qu'un runtime universel est déjà implémenté.

## 4. `udip/`

Rôle : **couche de documentation et de registre du protocole**.

### `udip/README.md`

Point d'entrée narratif. Il explique pourquoi la branche existe, comment elle se lit et quelles frontières elle protège.

### `udip/domain_registry.yaml`

Inventaire des domaines connus par la couche UDIP. Ce registre est descriptif : il ne transporte aucune autorité.

### `udip/BRANCH_MAP.md`

Cette carte. Elle décrit la topologie de la branche.

### `udip/DOMAIN_PACK_STANDARD.md`

Contrat documentaire et structurel d'un Domain Pack.

### `udip/SOURCE_TAXONOMY_V0.md`

Taxonomie canonique de provenance : composition du source set, classe de chaque artefact, maturité de chaque source et rôle domaine.

### `udip/provenance/`

Couche de traçabilité de la migration et de la compaction. Elle permet de supprimer les copies physiques inutiles sans perdre la possibilité de retrouver le blob canonique ou le snapshot brut.

## 5. `domains/`

Rôle : **porter la sémantique et les extensions propres à chaque monde**.

Le répertoire commun observé est :

```text
domains/<domain_id>/
├── README.md
├── domain_pack.yaml
├── object_map.yaml
├── sources.yaml
├── conformance.md
├── contracts/
├── signals/
├── governance/
├── execution/
├── extensions/
├── fixtures/
├── proof/
├── tests/
├── <DOMAIN>_MIGRATION_MANIFEST.md   [présent selon le pack]
└── migration_snapshot/             [optionnel]
```

### `README.md`

Explique le domaine, son statut réel, ses sources, ses extensions et ses manques.

### `domain_pack.yaml`

Déclare l'identité du pack, la version UDIP, le statut, le type de source, les sources historiques, les extensions et l'état d'implémentation.

### `object_map.yaml`

Mappe les objets du domaine vers des références canoniques sans importer leur sens dans le Core.

### `sources.yaml`

Déclare les origines de données ou références connues. Une source déclarée n'est ni une preuve ni une garantie de réalité.

### `conformance.md`

Documente la conformité du pack aux frontières UDIP : absence d'autorité locale, absence de bypass, distinction proposition / décision / exécution.

### `contracts/`

Contrats spécifiques au domaine. Ils doivent rester bornés au Domain Pack.

### `signals/`

Signaux métier ou observations transformables en `DomainSignal`.

### `governance/`

Adaptation de contraintes métier vers la gouvernance. Ce dossier ne peut pas contenir une autorité concurrente de KX108.

### `execution/`

Capacités d'exécution propres au domaine lorsqu'elles existent. Une capacité n'est jamais une permission ni une décision.

### `extensions/`

Extensions conditionnelles : par exemple `reality_authenticity`, attestation capteur, anti-replay, compensation ou contraintes physiques.

### `fixtures/`

Cas d'exemple et données de test du domaine.

### `proof/`

Preuves, références de preuve ou surfaces d'intégrité propres au Domain Pack.

### `tests/`

Tests du pack, notamment les tests de frontière et de non-contournement.

### `migration_snapshot/`

Archive de migration bornée. Ce dossier n'est pas un miroir de `main` et ne doit pas devenir une dépendance runtime implicite.

## 6. `cross_domain/`

Rôle : **porter uniquement ce qui est explicitement transversal**.

Le dossier courant contient `cross_domain/meta/`.

Une règle est obligatoire : un concept ne devient pas cross-domain simplement parce qu'il apparaît dans plusieurs snapshots. Il doit démontrer qu'il appartient réellement à plusieurs domaines sans transporter de sémantique métier cachée.

Cross-domain ne signifie pas Core, et ne signifie pas autorité.

## 7. `planning/`

Rôle : **séparer l'inventaire et les limites de la spécification canonique**.

### `source_inventory.md`

Recense les sources historiques, les états de référence et les pièces manquantes des Domain Packs.

### `do_not_generalize.md`

Protège les concepts qui doivent rester métier. C'est une barrière contre la généralisation excessive.

## 8. Les trois niveaux de vérité à ne pas confondre

### Niveau A — canon courant

Le fichier existe dans `main` ou dans une couche canonique du dépôt. C'est la référence courante pour Obsidia.

### Niveau B — Domain Pack UDIP

Le fichier décrit comment un domaine s'identifie, se mappe, produit des signaux et se conforme à la constitution UDIP.

### Niveau C — migration / provenance

Le fichier existe pour expliquer une origine, une divergence historique, une ancienne version ou une preuve de migration. Il ne devient pas canonique parce qu'il est conservé.

Cette séparation est essentielle pour éviter que `migration_snapshot/` ne soit pris pour un runtime.

## 9. Le trajet d'un domaine dans la branche

```text
source métier
   ↓
sources.yaml
   ↓
observation / état métier
   ↓
signals/
   ↓
object_map.yaml
   ↓
CanonicalDomainContract
   ↓
GovernancePayload
   ↓
KX108
   ↓
ACT / HOLD / BLOCK
   ↓
Binder                   [si action gouvernée]
   ↓
execution/               [si capacité d'exécution]
   ↓
proof/ + receipt + replay
```

`contracts/`, `extensions/`, `fixtures/` et `tests/` entourent ce trajet sans changer la frontière d'autorité.

## 10. Carte des statuts actuels

```text
REFERENCE HISTORIQUE
├── trading
├── bank
└── gps_defense_aviation

REFERENCE PARTIELLE
└── ecom

SCAFFOLDS DE RESISTANCE
├── industry_maintenance
├── btp_construction
├── logistics_supply_chain
├── cybersecurity
├── energy_critical_infrastructure
├── insurance
├── legal_compliance
├── telecom
├── facility_management
├── administration
├── health
└── hr
```

Tous les `domain_pack.yaml` observés restent actuellement `implementation_state: SCAFFOLD_ONLY`.

## 11. Carte de l'autorité

```text
Domain Pack
   peut comprendre / traduire / proposer
                │
                ▼
Canonical Domain Contract
                │
                ▼
GovernancePayload
                │
                ▼
          KX108 ONLY
        ACT / HOLD / BLOCK
                │
                ▼
Binder Permission Boundary
                │
                ▼
Execution Adapter
```

Aucun dossier de `domains/`, `cross_domain/`, `planning/` ou `udip/` ne doit créer une seconde autorité.

## 12. Politique de provenance après compaction

Baseline brute : `a9ab7e4310098d9758258a7a09bad743c3eda1dd`.

Main utilisé pour la vérification de duplication : `553df13d7bc8746ba582649d08a07a7f1478d081`.

Compaction : `37a2621ab892d64353389939f709188e4cbe1a54`.

Résultat : `4346` copies exactes ont été retirées des snapshots et remplacées par une référence de provenance. Les éléments différents ont été conservés pour audit.

Le but n'est donc pas de minimiser la branche à tout prix. Le but est de conserver une branche lisible où chaque fichier physique restant a une raison explicable d'exister.

## 13. Règle de modification

Avant d'ajouter un élément à UDIP, répondre dans cet ordre :

1. est-ce une règle universelle ou une sémantique de domaine ?
2. si c'est métier, dans quel Domain Pack doit-elle vivre ?
3. si c'est transversal, est-ce réellement cross-domain ?
4. est-ce une dépendance courante ou seulement une provenance historique ?
5. l'élément propose-t-il, prouve-t-il, autorise-t-il ou exécute-t-il ?
6. peut-il contourner KX108 ou Binder ?

Si la réponse n'est pas claire, l'élément ne doit pas être promu vers le Core.