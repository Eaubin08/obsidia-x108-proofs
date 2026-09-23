# Cybersecurity

> Domain Pack de sécurité défensive, preuve de sécurité et gouvernance des incidents.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Source type : `repo_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Cybersecurity n'est pas conçu comme un agent de sécurité souverain qui détecte une menace puis décide seul de la réponse.

Le corpus existant pousse vers une architecture de ce type :

```text
signal / événement / violation
→ qualification de risque
→ threat / evidence context
→ containment / response candidate
→ Cybersecurity DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder si conséquence
→ capacité de réponse autorisée
→ incident receipt / replay / audit
```

Le domaine peut détecter, classifier, enrichir, proposer et documenter.

Il ne possède ni l'autorité finale, ni une permission implicite d'isoler, d'écrire ou d'agir.

## 2. Statut réel

Le pack reste :

- `status: NEW_DOMAIN_SCAFFOLD` ;
- `source_type: repo_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

Cette synchronisation reconnaît un **corpus repository audité**.

Elle ne signifie pas :

- runtime Cybersecurity UDIP branché ;
- détection active universelle ;
- incident response automatisé ;
- certification sécurité ;
- object map implémenté ;
- tests de conformance Cybersecurity démontrés.

`object_map.yaml` reste volontairement vide.

## 3. Sources auditées

### Architecture / doctrine

- [Security by Threat Obsolescence](../../docs/investor/SECURITY_BY_THREAT_OBSOLESCENCE_OBSIDIA_X108.md)

Cette note formalise notamment :

```text
non-canonical input
→ no execution authority
```

avec :

- provenance ;
- fraîcheur ;
- anti-replay ;
- cohérence ;
- fail-closed ;
- receipts / replay ;
- séparation domaine / autorité.

Elle contient aussi des claims industriels qui restent soumis à son propre claim boundary.

### Isolation / Sandbox

- [Sandbox Policy](../../periphery/specs/Spec_03__Sandbox_Policy_isolation_et_gouvernance_P21_P30.md)

La spec définit une exécution contrainte avec notamment :

- `no_write` ;
- outils autorisés ;
- outils interdits ;
- réseau borné ;
- limites coût / durée / appels ;
- trace complète ;
- événements de violation.

### Incident Response

- [Incident Response Protocol](../../periphery/specs/Spec_18__Incident_Response_Protocol_P150_P154_valider_V4.md)

Cycle documenté :

```text
OPEN
→ CONTAINED
→ ANALYZED
→ RESOLVED
→ ARCHIVED
```

La source est `FORMALISÉ_À_VALIDER`.

Elle fournit donc une direction structurée, pas une garantie de runtime actif.

### Evidence-only security boundary

- [RSSI Evidence Only](../../runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md)

Ce contrat est `CONTRACT_SKELETON_ONLY`.

Il impose notamment :

```text
security control
!= automatic correction

threat model
!= effective protection

security evidence
!= certification

RSSI evidence
!= decision authority
```

### Network / connector audit

- [P70 Network Egress & Connectors Audit](../../docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md)

P70 classe les surfaces réseau et les connecteurs, dont :

- no egress ;
- readonly/dry-run ;
- localhost review ;
- active connector review ;
- external market egress ;
- blocked/proof-only.

P70 est un **audit transversal** utile à Cybersecurity.

Il ne devient pas un modèle d'objets Cybersecurity.

## 4. Périmètre V0

Le Domain Pack reconnaît maintenant six extensions documentaires :

### Detection / Evidence

- `detection`
- `threat_evidence`
- `security_evidence_advisory`

### Response / Containment

- `response`
- `incident_response`
- `isolation_boundaries`

Ces extensions décrivent le périmètre de conception.

Elles ne valent ni runtime, ni permission d'action, ni certification.

## 5. Security by admission

Une partie importante du corpus inverse le problème classique :

```text
ancien modèle :
le système doit prouver que l'entrée est malveillante

modèle gouverné :
l'entrée doit prouver qu'elle est admissible
```

Le pack Cybersecurity doit préserver cette distinction sans sur-promettre.

Cela ne signifie pas que toutes les attaques disparaissent.

Cela signifie qu'une entrée non admissible ne doit pas acquérir d'autorité simplement parce qu'elle existe ou qu'un modèle la comprend.

## 6. Detection

Une future couche Detection peut produire :

- événement de sécurité ;
- anomalie ;
- violation candidate ;
- risk flags ;
- contradictions ;
- evidence refs ;
- threat context.

Elle ne peut pas produire une décision finale.

```text
DETECTION != AUTHORITY
```

## 7. Threat model / evidence

Les sources imposent :

```text
THREAT_MODEL != PROTECTION_PROOF
SECURITY_CASE != EXECUTED_TEST
CONTROLS_MAP != GUARANTEED_COVERAGE
SECURITY_EVIDENCE != CERTIFICATION
EVIDENCE != AUTHORITY
```

Les preuves de sécurité peuvent enrichir :

- `OS3EvidenceTicket` ;
- `BoundaryContract` ;
- `ContextPacket` ;
- reason codes ;
- audit surfaces.

Elles ne doivent pas générer ALLOW/BLOCK à elles seules.

## 8. Isolation

La Sandbox Policy fournit une base de confinement :

```text
sandbox policy
→ explicit allowed capabilities
→ violation trace
→ evidence / ticket consequence
→ governed response
```

Une sandbox peut limiter une capacité.

Elle ne devient pas pour autant l'autorité générale du système.

Dans le Domain Pack Cybersecurity, `isolation_boundaries` signifie donc :

- expliciter ce qui peut être isolé ;
- documenter les capacités ;
- produire une conséquence traçable ;
- ne jamais confondre capacité d'isolation et permission d'isoler.

## 9. Incident Response

La source historique définit :

```text
OPEN
CONTAINED
ANALYZED
RESOLVED
ARCHIVED
```

avec :

- timeline ;
- classification ;
- audit ;
- signatures ;
- impossibilité de réécrire la trace ;
- séparation actions humaines / automatiques.

Cette structure est suffisamment forte pour justifier l'extension `incident_response`.

Mais le Domain Pack ne revendique pas encore l'implémentation de cette machine d'état.

## 10. Network / connector security

P70 fournit des catégories de risque et de contrôle réseau.

Ces catégories peuvent alimenter Cybersecurity sous forme de :

- evidence ;
- risk flags ;
- connector posture ;
- egress exposure ;
- review requirements.

Elles ne doivent pas devenir des objets Cybersecurity canoniques sans audit supplémentaire.

## 11. Point de branchement cible

```text
security source
→ detector / monitor / audit source
→ evidence + risk + contradiction
→ Cybersecurity DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder si conséquence
→ containment / response capability
→ ExecutionOutcome
→ Incident Receipt
→ Replay / Audit
```

## 12. Non-souveraineté

Invariants Cybersecurity :

```text
DOMAIN != AUTHORITY
DETECTION != AUTHORITY
THREAT_MODEL != PROTECTION_PROOF
SECURITY_EVIDENCE != CERTIFICATION
EVIDENCE != AUTHORITY
INCIDENT != EXECUTION_PERMISSION
CONTAINMENT_CAPABILITY != PERMISSION
ISOLATION != DECISION
RESPONSE_CANDIDATE != ACTION
KX108_ONLY
```

## 13. Source model

Le pack utilise `source_type: repo_reference`.

### REPO_ARCHITECTURE_SOURCE

- `docs/investor/SECURITY_BY_THREAT_OBSOLESCENCE_OBSIDIA_X108.md`

### REPO_SPEC_SOURCE

- `periphery/specs/Spec_03__Sandbox_Policy_isolation_et_gouvernance_P21_P30.md`
- `periphery/specs/Spec_18__Incident_Response_Protocol_P150_P154_valider_V4.md`

### REPO_CONTRACT_SOURCE

- `runtime_contracts/boundaries/RSSI_EVIDENCE_ONLY.md`

### REPO_AUDIT_SOURCE

- `docs/core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.md`
- `planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md`

### Maturité des sources

La nature et la maturité sont désormais séparées selon [SOURCE_TAXONOMY_V0](../../udip/SOURCE_TAXONOMY_V0.md).

Exemples Cybersecurity :

- Sandbox Policy → `REPO_SPEC_SOURCE` + `VALIDATED_SPEC` ;
- Incident Response → `REPO_SPEC_SOURCE` + `TO_VALIDATE` ;
- RSSI boundary → `REPO_CONTRACT_SOURCE` + `CONTRACT_SKELETON_ONLY`.

## 14. Conformance

Le profil Cybersecurity impose désormais au niveau documentaire :

```text
DETECTION != AUTHORITY
THREAT_MODEL != PROTECTION_PROOF
SECURITY_EVIDENCE != CERTIFICATION
INCIDENT_RESPONSE != EXECUTION_PERMISSION
ISOLATION_CAPABILITY != PERMISSION
KX108_ONLY
```

Les tests correspondants restent à créer.

Voir [conformance.md](conformance.md).

## 15. Manques

Le pack reste incomplet sur :

- object map ;
- objets Cybersecurity canoniques ;
- DomainSignal Cybersecurity natif ;
- detector/monitor adapter ;
- containment adapter ;
- Binder path ;
- Incident Receipt concret ;
- replay domaine ;
- tests Cybersecurity ;
- démonstration de non-contournement ;
- séparation finale entre sécurité transverse Obsidia et sémantique réellement propre au Domain Pack.

## 16. Object-model candidate audit

L'audit READ_ONLY des objets candidats est maintenant documenté dans [OBJECT_MODEL_CANDIDATES_V0.md](OBJECT_MODEL_CANDIDATES_V0.md).

Verdict :

```text
objets prêts à promouvoir = 0
```

Les candidats les plus solides sont `Incident` et `ViolationEvent`, mais leur ownership et leur schéma ne sont pas encore assez figés pour `object_map.yaml`.

Le map reste volontairement vide.