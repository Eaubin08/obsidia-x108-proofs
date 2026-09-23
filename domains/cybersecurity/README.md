# Cybersecurity

> Domain Pack de sécurité défensive et de gouvernance des incidents.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Cybersecurity n'est pas conçu comme un “agent sécurité” qui détecterait une menace puis déciderait quoi faire.

La matière existante d'Obsidia pousse vers une architecture différente :

```text
signal / événement / violation
→ qualification de risque
→ evidence / threat context
→ isolation ou containment candidate
→ DomainSignal
→ gouvernance
→ KX108
→ permission séparée si action
→ incident receipt / replay / audit
```

Le domaine peut donc détecter, contextualiser, proposer un confinement ou une réponse, mais il ne devient jamais l'autorité qui exécute cette réponse.

## 2. Matière réelle déjà présente

La vision est soutenue par plusieurs couches existantes :

- [Security by Threat Obsolescence](../../docs/investor/SECURITY_BY_THREAT_OBSOLESCENCE_OBSIDIA_X108.md) : admission structurée, fail-closed, provenance, anti-replay, receipts ;
- [Sandbox Policy](../../periphery/specs/Spec_03__Sandbox_Policy_isolation_et_gouvernance_P21_P30.md) : environnement contraint, outils permis/interdits, trace des violations ;
- [Incident Response Protocol](../../periphery/specs/Spec_18__Incident_Response_Protocol_P150_P154_valider_V4.md) : cycle OPEN → CONTAINED → ANALYZED → RESOLVED → ARCHIVED ;
- [RSSI Evidence Only](../../runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md) : contrôles, risk assessment et threat model comme preuves advisory, jamais comme autorité ;
- [Network Egress & Connectors Audit](../../docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md) : classification des sorties réseau et connecteurs actifs.

Ces sources ne constituent pas encore un runtime Cybersecurity UDIP. Elles définissent toutefois un socle conceptuel beaucoup plus riche que le simple scaffold.

## 3. Périmètre déclaré

`domain_pack.yaml` déclare trois extensions :

- `detection` ;
- `response` ;
- `isolation_boundaries`.

Elles sont cohérentes avec le corpus existant.

## 4. Principe central

La sécurité ne doit pas dépendre d'un modèle qui “comprend” qu'une entrée est malveillante.

Une partie du corpus Obsidia inverse la charge :

```text
ancien modèle :
prouver que l'entrée est mauvaise

modèle gouverné :
l'entrée doit prouver qu'elle est admissible
```

Cette doctrine est particulièrement forte pour les systèmes critiques, mais elle reste une direction architecturale, pas une certification de sécurité universelle.

## 5. Threat model et evidence

Le Domain Pack doit distinguer :

```text
threat model
≠ protection effective

security evidence
≠ certification

risk score
≠ decision

incident candidate
≠ action
```

Le contrat `RSSI_EVIDENCE_ONLY` est un bon modèle : une preuve de sécurité peut enrichir un ticket, un ContextPacket ou un BoundaryContract, mais elle ne peut produire ALLOW/BLOCK par elle-même.

## 6. Isolation

La Sandbox Policy fournit une base transversale :

- `no_write` ;
- outils explicitement autorisés ;
- outils interdits ;
- réseau borné ;
- limites coût/durée/appels ;
- trace complète ;
- violation événementialisée.

Dans un futur Domain Pack Cybersecurity, l'isolation peut devenir une **capacité de réponse proposée**, jamais une autorité implicite.

## 7. Incident response

Le protocole historique décrit un cycle d'incident structuré :

```text
OPEN
→ CONTAINED
→ ANALYZED
→ RESOLVED
→ ARCHIVED
```

avec :

- timeline ;
- audit ;
- classification ;
- signatures ;
- impossibilité de réécrire la trace après coup.

Ce mécanisme est fortement pertinent pour le domaine, même si la spec source reste `FORMALISÉ_À_VALIDER`.

## 8. Point de branchement cible

```text
security source
→ detector / monitor
→ risk + evidence
→ Cybersecurity DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder si containment/action
→ execution capability
→ incident receipt
→ replay / audit
```

## 9. Non-souveraineté

Invariants :

```text
DOMAIN != AUTHORITY
THREAT_MODEL != VERDICT
EVIDENCE != AUTHORITY
DETECTION != RESPONSE_PERMISSION
KX108_ONLY
```

## 10. État réel du pack

Malgré ce corpus riche :

- `sources.yaml` reste `NOT_YET_DEFINED` ;
- `object_map.yaml` n'est pas implémenté ;
- `conformance.md` reste `SCAFFOLD ONLY` ;
- les fichiers de `migration_snapshot/` contiennent beaucoup de matière transverse/générique.

Il serait donc faux de présenter Cybersecurity comme déjà intégré.

## 11. Sources

Voir aussi :

- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)
- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)
- [Domain Pack Standard](../../udip/DOMAIN_PACK_STANDARD.md)

## 12. Prochaine étape

Construire un vrai object map autour d'objets tels que :

```text
security_event
risk_finding
threat_evidence
incident
containment_candidate
security_boundary
```

puis démontrer que ces objets peuvent être gouvernés sans donner d'autorité au domaine.
