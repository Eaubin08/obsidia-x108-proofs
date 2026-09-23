# UDIP Domain Pack Standard V0

## 1. Objet

Ce document définit la fiche standard d'un Domain Pack dans UDIP V0.

Le standard ne cherche pas à uniformiser les métiers. Il uniformise **la façon dont un domaine déclare son identité, ses sources, ses objets, ses signaux, ses frontières, ses preuves et ses manques**.

Un Domain Pack doit permettre à un lecteur de répondre rapidement à six questions :

```text
Quel monde est représenté ?
D'où viennent ses données et ses règles ?
Qu'est-ce qui lui appartient réellement ?
Comment se raccorde-t-il au canon Obsidia ?
Qu'a-t-il le droit de faire ?
Qu'est-ce qui reste non prouvé ou non implémenté ?
```

## 2. Structure standard

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
├── <DOMAIN>_MIGRATION_MANIFEST.md   [si migration]
└── migration_snapshot/             [si provenance nécessaire]
```

Les dossiers peuvent être vides dans un scaffold. Leur présence ne vaut pas implémentation.

## 3. Fiche obligatoire dans `README.md`

### A. Identité

- `domain_id` ;
- nom humain ;
- objectif du domaine ;
- frontière métier.

### B. Statut

Utiliser un statut explicite :

- `EXISTING_REFERENCE` : une architecture historique réelle existe et sert de référence ;
- `PARTIAL_REFERENCE` : certaines briques existent, mais le domaine n'est pas complet ;
- `NEW_DOMAIN_SCAFFOLD` : structure préparée sans architecture métier revendiquée.

Le champ `implementation_state` doit rester distinct. Dans l'état actuel de la branche, les Domain Packs déclarent `SCAFFOLD_ONLY`.

### C. Sources

Décrire :

- sources historiques ;
- sources externes ;
- fichiers canoniques connus ;
- éléments non audités ;
- provenance lorsqu'elle est pertinente.

Une source n'implique jamais la confiance : `SOURCE != TRUST`.

### D. Sémantique propre au domaine

Nommer les concepts qui doivent rester dans le Domain Pack.

Exemples :

- Trading : market data, portfolio, broker execution ;
- Bank : fraud, compliance, bank policy ;
- GPS : reality authenticity, sensor attestation, physical envelope ;
- Logistics : stock, suppliers, route, delivery.

Cette section est aussi une barrière contre la fuite de sémantique vers `udip/` ou le Core.

### E. Éléments provenant du canon Obsidia

Identifier ce qui est consommé mais non possédé par le domaine :

- `DomainSignal` ;
- `CanonicalDomainContract` ;
- `GovernancePayload` ;
- frontière `KX108` ;
- frontière Binder lorsqu'elle existe ;
- Receipt / Replay / Proof surfaces.

Le Domain Pack peut adapter ces éléments. Il ne les redéfinit pas pour créer sa propre constitution.

### F. Point de branchement

Décrire le trajet concret :

```text
source du domaine
→ adapter / observation
→ signal
→ canonicalisation
→ governance payload
→ KX108
→ Binder si nécessaire
→ exécution si nécessaire
→ receipt / replay / proof
```

Si un maillon n'existe pas, il doit être marqué `MISSING`, `PARTIAL`, `REFERENCE_ONLY` ou équivalent — jamais deviné.

### G. Gouvernance et droits

Écrire explicitement :

```text
DOMAIN != AUTHORITY
PROPOSAL != ACTION
KX108_ONLY
```

Puis documenter :

- ce que le domaine peut observer ;
- ce qu'il peut proposer ;
- ce qu'il peut simuler ;
- ce qu'il peut prouver ;
- ce qu'il ne peut jamais autoriser seul ;
- les éventuelles capacités d'exécution.

### H. Preuve, Receipt et Replay

Indiquer ce qui existe réellement :

- evidence refs ;
- receipts ;
- hash chain ;
- replay ;
- tests déterministes ;
- preuve physique ;
- attestation ;
- absence de preuve.

`RECEIPT != DECISION` et `REPLAY != EXECUTION` doivent rester vrais.

### I. Migration et provenance

Si le pack possède `migration_snapshot/`, expliquer pourquoi.

Le snapshot doit être classé comme :

- artefact domaine-spécifique ;
- divergence historique utile ;
- ancienne version nécessaire à la comparaison ;
- preuve / résultat ;
- référence devenue absente du canon ;
- autre raison explicitement documentée.

Un snapshot ne doit pas être conservé seulement parce qu'il existait dans la source.

### J. Manques / prochaine étape

Terminer par une liste courte de manques factuels : adapter absent, object map incomplet, source non auditée, tests manquants, Binder non raccordé, receipt partiel, runtime non migré ou authenticité physique non démontrée.

## 4. Contrat minimal de `domain_pack.yaml`

```yaml
domain_id: <stable_id>
domain_name: <human_name>
udip_version: V0
status: EXISTING_REFERENCE | PARTIAL_REFERENCE | NEW_DOMAIN_SCAFFOLD
source_type: <source classification>
legacy_sources:
  - <source references>
extensions:
  - <domain-specific extensions>
implementation_state: SCAFFOLD_ONLY
```

Ce fichier est un manifeste de Domain Pack, pas une autorisation d'exécution.

## 5. Contrat de `object_map.yaml`

`object_map.yaml` doit permettre de relier les objets métier à des références canoniques sans déplacer leur signification dans le Core.

Règles :

- l'identifiant canonique ne doit pas réécrire la sémantique métier ;
- un mapping n'est pas une décision ;
- un objet non mappable reste explicite plutôt que forcé ;
- les inconnues et ambiguïtés doivent survivre à la canonicalisation.

## 6. Contrat de `sources.yaml`

`sources.yaml` décrit l'origine, pas la vérité.

Quand le domaine dépend de données physiques ou hostiles, `SourceProvenance` peut devoir être complété par une extension de type `RealityAuthenticity`. Les deux notions ne doivent pas être fusionnées.

## 7. Contrat des dossiers

| Dossier | Rôle | Ne doit pas devenir |
|---|---|---|
| `contracts/` | contrats métier | constitution parallèle |
| `signals/` | observations / propositions | décision finale |
| `governance/` | contraintes traduites | autorité KX108 |
| `execution/` | capacités outbound | permission implicite |
| `extensions/` | besoins conditionnels | Core universel par défaut |
| `fixtures/` | cas de test | preuve de production |
| `proof/` | preuve / intégrité / références | autorité |
| `tests/` | vérification | garantie non bornée |
| `migration_snapshot/` | provenance bornée | miroir de `main` |

## 8. Matrice actuelle des Domain Packs

| Domain Pack | Statut | Source type | Extensions déclarées | Implémentation déclarée |
|---|---|---|---|---|
| `trading` | `EXISTING_REFERENCE` | `external_reference` | market_data, portfolio, broker_execution | `SCAFFOLD_ONLY` |
| `bank` | `EXISTING_REFERENCE` | `repo_reference` | fraud, compliance, bank_policy | `SCAFFOLD_ONLY` |
| `gps_defense_aviation` | `EXISTING_REFERENCE` | `repo_reference` | reality_authenticity, sensor_attestation, anti_replay, physical_envelope | `SCAFFOLD_ONLY` |
| `ecom` | `PARTIAL_REFERENCE` | `repo_partial_reference` | customer, order_intent, payment_provider, compensation_ref | `SCAFFOLD_ONLY` |
| `industry_maintenance` | `NEW_DOMAIN_SCAFFOLD` | `none` | machines, production, maintenance, sensors, operators | `SCAFFOLD_ONLY` |
| `btp_construction` | `NEW_DOMAIN_SCAFFOLD` | `none` | terrain, plans, documents, subcontractors, planning, exceptions | `SCAFFOLD_ONLY` |
| `logistics_supply_chain` | `NEW_DOMAIN_SCAFFOLD` | `none` | stock, warehouse, suppliers, transport, route, delivery | `SCAFFOLD_ONLY` |
| `cybersecurity` | `NEW_DOMAIN_SCAFFOLD` | `none` | detection, response, isolation_boundaries | `SCAFFOLD_ONLY` |
| `energy_critical_infrastructure` | `NEW_DOMAIN_SCAFFOLD` | `mixed_reference` | thermo_compute, energy_efficiency, thermo_debt, sigma_truth_mismatch, physical_infrastructure, fail_closed, real_world_execution_constraints | `SCAFFOLD_ONLY` |
| `insurance` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |
| `legal_compliance` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |
| `telecom` | `NEW_DOMAIN_SCAFFOLD` | `mixed_reference` | network_connectivity, network_egress, gateway_constraints, physical_signal_observation, signal_provenance, signal_coherence | `SCAFFOLD_ONLY` |
| `facility_management` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |
| `administration` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |
| `health` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |
| `hr` | `NEW_DOMAIN_SCAFFOLD` | `none` | aucune | `SCAFFOLD_ONLY` |

Cette matrice reflète les manifests actuels. Elle ne doit pas être extrapolée en maturité runtime.

## 9. Template de fiche Domain Pack

```markdown
# <Domain Name>

## Identité
<objectif et frontière métier>

## Statut
- UDIP status: <...>
- implementation_state: <...>

## Sources
- <source 1>
- <source 2>

## Sémantique propre
- <concept métier>

## Éléments canoniques consommés
- DomainSignal
- CanonicalDomainContract
- GovernancePayload
- KX108 boundary

## Point de branchement
<source -> signal -> canonical -> governance -> KX108 -> ...>

## Gouvernance et droits
- peut : <...>
- ne peut pas : décider / contourner KX108 / créer une autorité parallèle

## Preuve / Receipt / Replay
- <état réel>

## Migration / provenance
- <raison de conserver chaque snapshot si présent>

## Manques
- <manque factuel>
```

## 10. Gate de promotion d'un scaffold

Un Domain Pack ne doit quitter `SCAFFOLD_ONLY` que lorsque les éléments suivants sont démontrés ou explicitement bornés :

1. identité stable ;
2. sources auditables ;
3. object map réel ;
4. DomainSignal ou équivalent raccordé ;
5. canonicalisation sans fabrication de décision ;
6. `KX108_ONLY` vérifié ;
7. Binder séparé si exécution ;
8. adapter inbound/outbound distingué ;
9. receipt / replay / preuve proportionnés au domaine ;
10. tests de non-contournement ;
11. manques résiduels documentés ;
12. aucune sémantique métier promue abusivement dans le Core.

## 11. Règle finale

Le standard UDIP porte sur la **forme du raccordement**, jamais sur l'uniformisation du monde.

```text
Domain Pack = sens métier + traduction + contraintes + preuves
Core        = frontières universelles
KX108       = autorité
Binder      = permission d'exécution
Adapter     = capacité
Receipt     = trace
```