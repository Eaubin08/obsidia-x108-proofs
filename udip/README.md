# UDIP — Universal Domain Integration Protocol

> Branche de recherche, de normalisation et d'intégration des domaines Obsidia.
>
> **Statut du protocole : `SPEC_ONLY`**  
> **Impact runtime du protocole V0 : `NONE`**  
> **Autorité : `KX108_ONLY`**

## 1. Pourquoi cette branche existe

UDIP répond à une question précise : comment raccorder des mondes métier très différents à Obsidia sans reconstruire le Core, sans importer leur sémantique dans le noyau et sans leur donner une autorité d'action ?

`main` porte le canon courant d'Obsidia. La branche UDIP ne cherche pas à devenir un second `main`, ni une copie générale du dépôt. Elle isole le travail nécessaire pour rendre l'intégration des domaines explicite, répétable, traçable et comparable.

Le domaine historique de référence est **Trading**. Le protocole est ensuite confronté à d'autres mondes — Bank, GPS / Defense / Aviation, Ecom, puis des Domain Packs de résistance comme Cybersecurity, Energy, Telecom, Health ou HR — afin de séparer ce qui est réellement universel de ce qui doit rester métier.

Le principe directeur est simple :

```text
le domaine comprend son monde
        ↓
il traduit ce monde vers une forme gouvernable
        ↓
KX108 garde l'autorité
        ↓
Binder garde la frontière de permission
        ↓
l'exécution éventuelle reste bornée et traçable
```

## 2. Ce que UDIP est — et ce qu'il n'est pas

UDIP est :

- un contrat architectural d'intégration de domaines ;
- une couche de construction de Domain Packs ;
- un espace de comparaison entre domaines ;
- une discipline de séparation entre sémantique métier, gouvernance, permission, exécution et preuve ;
- une surface de provenance pour comprendre d'où vient un Domain Pack et comment il se raccorde au canon.

UDIP n'est pas :

- un nouveau kernel ;
- une autorité parallèle ;
- un orchestrateur autonome ;
- un moteur métier universel ;
- un fork runtime de `main` ;
- une raison de déplacer BUY, SELL, GNSS, fraude, paiement, stock, RF ou d'autres concepts métier dans le Core.

Le protocole canonique reste documenté dans [`docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md`](../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md).

## 3. La frontière fondamentale

Le Core fournit les frontières. Le Domain Pack fournit le sens métier.

Les invariants structurants de UDIP V0 sont notamment :

```text
DOMAIN != AUTHORITY
DOMAIN SIGNAL != DECISION
PROPOSAL != ACTION
KX108 DECISION != BINDER PERMISSION
BINDER PERMISSION != EXECUTION CAPABILITY
EXECUTION CAPABILITY != EXECUTION SUCCESS
SOURCE != TRUST
SOURCE PROVENANCE != REALITY AUTHENTICITY
SIMULATION != REALITY
REPLAY != EXECUTION
RECEIPT != DECISION
```

Le domaine peut observer, interpréter, produire des signaux, des propositions, des inconnues, des contradictions, des risques et des références de preuve. Il ne transforme jamais lui-même ces éléments en autorité.

## 4. Le trajet universel

```text
Domain Sources
  ↓
Source Provenance
  ↓
Domain Observation / State
  ↓
Domain Cognition / Agents / Rules
  ↓
Domain Signal / Proposal
  ↓
Canonical Domain Contract
  ↓
Governance Payload
  ↓
KX108 Authority Boundary
  ↓
ACT / HOLD / BLOCK
  ↓
Binder Permission Boundary
  ↓
Outbound Execution Adapter   [si exécution]
  ↓
Execution Outcome
  ↓
Receipt
  ↓
Replay / Proof
```

Tous les domaines ne vont pas jusqu'à l'exécution. Un domaine d'observation peut s'arrêter avant Binder. Un domaine physique peut ajouter une extension `RealityAuthenticityGate`. Un domaine externe peut avoir un `ExternalInputAdapter`. Ces extensions ne changent pas l'autorité centrale.

## 5. Organisation de la branche

```text
docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md
    contrat architectural universel

udip/
    documentation, registre, provenance

domains/<domain_id>/
    Domain Packs : sens métier, mapping, sources, conformance, extensions

cross_domain/
    éléments explicitement transverses, sans autorité

planning/
    inventaire de sources, limites et éléments à ne pas généraliser
```

La carte détaillée est dans [`BRANCH_MAP.md`](BRANCH_MAP.md).

## 6. Anatomie d'un Domain Pack

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
└── migration_snapshot/      [optionnel / provenance bornée]
```

Cette homogénéité ne signifie pas que les domaines deviennent identiques. Elle signifie seulement qu'ils déclarent leurs différences dans des emplacements comparables.

Le standard détaillé d'une fiche Domain Pack est dans [`DOMAIN_PACK_STANDARD.md`](DOMAIN_PACK_STANDARD.md).

La taxonomie canonique des sources est dans [`SOURCE_TAXONOMY_V0.md`](SOURCE_TAXONOMY_V0.md).

## 7. État actuel des Domain Packs

| Domaine | Statut déclaré | Source | Extensions déclarées |
|---|---|---|---|
| Trading | `EXISTING_REFERENCE` | référence externe + repo | market_data, portfolio, broker_execution |
| Bank | `EXISTING_REFERENCE` | repo | fraud, compliance, bank_policy |
| GPS / Defense / Aviation | `EXISTING_REFERENCE` | repo | reality_authenticity, sensor_attestation, anti_replay, physical_envelope |
| Ecom | `PARTIAL_REFERENCE` | référence repo partielle | customer, order_intent, payment_provider, compensation_ref |
| Industry / Maintenance | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | machines, production, maintenance, sensors, operators |
| BTP / Construction | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | terrain, plans, documents, subcontractors, planning, exceptions |
| Logistics / Supply Chain | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | stock, warehouse, suppliers, transport, route, delivery |
| Cybersecurity | `NEW_DOMAIN_SCAFFOLD` | repo audité | detection, threat_evidence, security_evidence_advisory, response, incident_response, isolation_boundaries |
| Energy / Critical Infrastructure | `NEW_DOMAIN_SCAFFOLD` | repo + sources conceptuelles internes | thermo_compute, energy_efficiency, thermo_debt, sigma_truth_mismatch, physical_infrastructure, fail_closed, real_world_execution_constraints |
| Insurance | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | aucune |
| Legal / Compliance | `NEW_DOMAIN_SCAFFOLD` | repo audité | compliance_scope, privacy_readiness, claim_scope, data_governance_advisory, processing_risk, retention_access_privacy_risk, human_legal_review_gate, regulatory_mapping, legal_audit_export |
| Telecom | `NEW_DOMAIN_SCAFFOLD` | repo + sources conceptuelles internes | network_connectivity, network_egress, gateway_constraints, physical_signal_observation, signal_provenance, signal_coherence |
| Facility Management | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | aucune |
| Administration | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | aucune |
| Health | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | aucune |
| HR | `NEW_DOMAIN_SCAFFOLD` | aucune source auditée | aucune |

Important : les `domain_pack.yaml` actuels déclarent encore `implementation_state: SCAFFOLD_ONLY`. Le fait qu'un domaine possède des sources historiques ou des snapshots ne signifie donc pas qu'il est déjà migré vers un runtime UDIP natif.

## 8. Références structurantes

- **Trading** : référence historique d'intégration externe, proposition, gouvernance, exécution et receipt ;
- **Bank** : contraintes fraude, conformité, limites et action financière ;
- **GPS / Defense / Aviation** : séparation provenance / authenticité physique, Reality Gate et attestation ;
- **Ecom** : référence partielle où paiement, compensation et fulfillment ne doivent pas être inventés par le Core.

Les autres Domain Packs servent de tests de résistance à la généralisation.

## 9. Politique de `migration_snapshot/`

`migration_snapshot/` n'est plus une copie de `main`.

Après la compaction V0 :

- le snapshot brut reste récupérable au commit `a9ab7e4310098d9758258a7a09bad743c3eda1dd` ;
- `4346` copies byte-identiques au `main` épinglé ont été retirées ;
- leur provenance est conservée dans [`provenance/MIGRATION_REFERENCE_INDEX_V0.csv`](provenance/MIGRATION_REFERENCE_INDEX_V0.csv) ;
- la compaction est figée par le commit `37a2621ab892d64353389939f709188e4cbe1a54` ;
- les éléments différents ou sans équivalent direct sont conservés pour audit.

La règle future est : un snapshot n'est conservé physiquement que s'il apporte une divergence historique utile, un artefact domaine-spécifique, une preuve, un résultat, ou une provenance qui ne peut pas être remplacée par une référence Git stable.

## 10. Ce qui ne doit pas être généralisé

`planning/do_not_generalize.md` protège les concepts qui doivent rester métier.

- Trading : BUY, SELL, broker, Alpaca, portfolio ;
- Bank : fraud, AML, sanctions, payment rails ;
- GPS : GNSS, RF, RINEX, aircraft, sensor thresholds ;
- Ecom : cart, checkout, refund, shipment, fulfillment.

UDIP peut standardiser **la manière de déclarer, transporter, gouverner et prouver** ces concepts. Il ne standardise pas leur sens métier.

## 11. Comment lire la branche

1. lire ce README ;
2. lire [`BRANCH_MAP.md`](BRANCH_MAP.md) ;
3. lire `docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md` ;
4. prendre Trading comme référence historique ;
5. comparer Bank puis GPS / Defense / Aviation ;
6. lire Ecom comme référence partielle ;
7. utiliser les autres Domain Packs comme tests de résistance ;
8. consulter `migration_snapshot/` seulement pour une question de provenance ou de divergence historique.

## 12. Règle de promotion

Un Domain Pack ne devient pas intégré parce que son dossier existe.

```text
identité du domaine
+ sources explicites
+ object map borné
+ signal canonique
+ aucune autorité locale
+ passage gouverné vers KX108
+ frontière Binder si exécution
+ receipt / replay / preuve adaptés
+ tests de non-contournement
```

Tant que ces éléments ne sont pas démontrés, le statut `SCAFFOLD_ONLY`, `PARTIAL` ou `REFERENCE` doit rester visible.

## 13. Résumé

UDIP n'essaie pas de rendre tous les métiers identiques. Il rend leur **raccordement à Obsidia comparable et gouvernable**.

```text
plusieurs mondes
→ plusieurs sémantiques
→ une forme d'intégration commune
→ une autorité unique
→ des preuves traçables
```

Le Domain Pack comprend son monde. Le Core conserve ses frontières. KX108 reste l'autorité.