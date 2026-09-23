# Ecom

> Domain Pack de référence partielle pour commandes, clients, paiement, compensation et fulfillment.
>
> **UDIP status : `PARTIAL_REFERENCE`**  
> **Source type : `repo_partial_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Identité

Ecom représente un domaine transactionnel où l'intention d'achat, le client, le paiement, le remboursement, le stock et le fulfillment peuvent être liés mais ne doivent pas être fusionnés dans une action unique implicite.

Il est volontairement classé **référence partielle** : certaines sources et tests existent, mais le domaine complet n'est pas implémenté.

## 2. Statut réel

`domain_pack.yaml` déclare :

- `status: PARTIAL_REFERENCE` ;
- `source_type: repo_partial_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

`object_map.yaml` reste `REFERENCE_ONLY` avec `objects: []`.

`sources.yaml` ne revendique qu'une cartographie de sources, sans migration de code via le scaffold.

## 3. Sources historiques

Sources déclarées :

- `sigma/domains/ecom_agents.py` ;
- `examples/ecom_normal.json` ;
- `tests Ecom if present`.

Le manifeste brut de migration a identifié **9 éléments** réellement associés à Ecom :

- 1 fichier de code ;
- 3 tests ;
- 3 documents ;
- 2 fixtures.

Aucun adapter, pipeline ou proof pack propre à Ecom n'était identifié dans ce snapshot brut.

## 4. Sémantique propre au domaine

Extensions déclarées :

- `customer` ;
- `order_intent` ;
- `payment_provider` ;
- `compensation_ref`.

Concepts qui doivent rester domaine-spécifiques :

- cart ;
- checkout ;
- refund ;
- shipment ;
- fulfillment ;
- paiement ;
- cycle de commande.

Le Universal Core ne doit pas transformer ces concepts en primitives universelles.

## 5. Éléments canoniques consommés

Le Domain Pack cible les frontières communes :

- `DomainSignal` ;
- `CanonicalDomainContract` ;
- `GovernancePayload` ;
- KX108 ;
- Binder pour toute exécution gouvernée ;
- Receipt / Replay / Proof lorsque disponibles.

La présence d'une intention de commande ou de paiement ne vaut jamais autorisation d'exécution.

## 6. Point de branchement cible

```text
customer / order / external service
→ observation / Ecom agents
→ order intent / domain signal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder permission
→ payment / fulfillment adapter
→ ExecutionOutcome
→ Receipt / compensation ref / replay
```

Ce trajet reste partiel : plusieurs maillons sont explicitement absents.

## 7. Gouvernance et droits

Invariants :

```text
DOMAIN != AUTHORITY
ORDER INTENT != PAYMENT
PAYMENT CAPABILITY != PERMISSION
COMPENSATION != ROLLBACK
KX108_ONLY
```

Ecom peut :

- produire des signaux liés à une commande ;
- exposer contexte client ou intention si disponible ;
- qualifier des risques ou incohérences ;
- proposer une action métier.

Ecom ne peut pas :

- déclencher implicitement un paiement ;
- confondre checkout avec ACT ;
- contourner KX108 ;
- contourner Binder ;
- inventer un mécanisme de compensation absent.

## 8. Ce qui manque explicitement

Le manifeste de migration liste comme **EXPECTED_BUT_NOT_FOUND** :

- compensation mechanism ;
- customer identity model ;
- execution result ;
- order lifecycle ;
- payment adapter ;
- refund mechanism ;
- shipment / fulfillment adapter.

Ces absences sont structurantes.

Elles expliquent pourquoi le domaine reste `PARTIAL_REFERENCE` et `SCAFFOLD_ONLY`.

## 9. Preuve / Receipt / Replay

Le snapshot Ecom historique ne contenait aucun artefact classé `PROOF`.

Il contenait des tests et fixtures, mais cela ne suffit pas à établir :

- un receipt universel ;
- un replay complet ;
- une preuve d'exécution ;
- une compensation réellement implémentée.

`conformance.md` indique par ailleurs qu'aucun test UDIP n'est implémenté dans le scaffold courant.

## 10. Migration / provenance

Le manifeste brut a copié 9 sources en conservant les originaux inchangés.

La compaction UDIP V0 a retiré les copies exactes déjà présentes dans le canon et conservé leur mapping dans la provenance globale.

Ecom illustre donc bien la nouvelle doctrine :

```text
ne pas conserver une copie physique
si une référence Git stable suffit
```

Le Domain Pack doit conserver le **sens de la migration**, pas dupliquer le dépôt.

## 11. Manques actuels

Les manques principaux sont :

- Domain Pack complet ;
- customer identity model ;
- cycle de commande canonique ;
- payment adapter ;
- refund mechanism ;
- shipment / fulfillment adapter ;
- compensation mechanism ;
- execution result model ;
- object map réel ;
- tests UDIP ;
- preuve / receipt / replay adaptés au domaine.

## 12. Règle de promotion

Ecom ne doit quitter `PARTIAL_REFERENCE / SCAFFOLD_ONLY` qu'après séparation explicite de :

```text
intention de commande
≠
autorisation de paiement
≠
capacité provider
≠
succès d'exécution
≠
compensation
```

Puis démonstration de leur passage gouverné par KX108 et Binder.
