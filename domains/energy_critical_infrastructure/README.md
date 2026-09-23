# Energy / Critical Infrastructure

> Domain Pack pour thermodynamique computationnelle, signaux d'efficacité énergétique et contraintes d'infrastructure physique critique.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Source type : `mixed_reference`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Energy est conservé comme **un seul Domain Pack**, mais avec deux sous-contrats explicitement séparés :

```text
ENERGY / CRITICAL INFRASTRUCTURE
│
├── A. THERMO / COMPUTE ENERGY
│   ├── energy efficiency
│   ├── thermo debt
│   ├── compute / attention / recovery cost
│   ├── useful work
│   └── Sigma / truth mismatch
│
└── B. PHYSICAL CRITICAL INFRASTRUCTURE
    ├── physical infrastructure state
    ├── fail-closed constraints
    ├── real-world execution constraints
    ├── physical risk
    └── consequence / execution boundary
```

La famille A possède déjà du code périphérique réel.

La famille B reste essentiellement une **direction architecturale à construire**.

Les deux familles ne doivent pas être confondues.

## 2. Statut réel

Le pack reste :

- `status: NEW_DOMAIN_SCAFFOLD` ;
- `source_type: mixed_reference` ;
- `implementation_state: SCAFFOLD_ONLY`.

Cette synchronisation reconnaît une matière de conception et du code existant.

Elle ne signifie pas :

- runtime Energy UDIP branché ;
- object map implémenté ;
- infrastructure physique pilotable ;
- Binder Energy raccordé ;
- conformance Energy démontrée ;
- test de non-souveraineté suffisant.

`object_map.yaml` reste volontairement vide.

## 3. Famille A — Thermo / Compute Energy

Sources repository principales :

- [ENERGY_THERMO_GOVERNOR_V0](../../docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md)
- [energy_thermo.py](../../periphery/energy_thermo.py)
- [energy_thermo_agent.py](../../periphery/agents/energy_thermo_agent.py)

Le code `run_energy_thermo` calcule réellement :

- `pin` ;
- `pout` ;
- `energy_efficiency` ;
- `thermo_debt` ;
- `truth_score` ;
- `sigma_score` ;
- `sigma_truth_mismatch`.

La dette thermodynamique est construite à partir de :

```text
energy_cost
+ compute_cost
+ attention_cost
+ recovery_cost
- useful_work
```

Le module peut produire des signaux comme :

- `ENERGY_INEFFICIENT` ;
- `THERMO_DEBT_HIGH` ;
- `SIGMA_TRUTH_MISMATCH` ;
- `COLLAPSE_DISGUISED_HIGH_SIGMA`.

Il peut recommander :

- `HOLD` ;
- `BLOCK_CANDIDATE`.

Il ne retourne pas une décision KX108.

## 4. Agent non souverain

`periphery/agents/energy_thermo_agent.py` déclare :

```text
agent_id = ENERGY_THERMO_AGENT
layer = ENERGY
description = wrapper non souverain
```

Le rôle actuel est donc clairement périphérique :

```text
ActionCandidate
→ Energy Thermo Agent
→ PeripheralSignalPacket / AgentResult
→ contexte / risque / contradiction
→ gouvernance ultérieure
```

L'agent n'est pas l'autorité de décision.

## 5. Famille B — Physical Critical Infrastructure

Le manifeste historique déclarait déjà :

- `physical_infrastructure` ;
- `fail_closed` ;
- `real_world_execution_constraints`.

Cette famille vise un monde différent du simple coût computationnel.

Trajet cible :

```text
physical source / infrastructure state
→ provenance / authenticity / constraints
→ Energy DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ ACT / HOLD / BLOCK
→ Binder
→ physical execution capability
→ ExecutionOutcome
→ Receipt / Replay / Proof
```

Ce trajet n'est **pas** aujourd'hui implémenté comme runtime Energy UDIP complet.

## 6. Fail-closed

Source :

- [FAIL_CLOSED_PRIORITY_SPEC](../../specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md)

La règle documentée est :

```text
BLOCK > HOLD > ALLOW
```

et l'absence de conditions suffisantes ne doit jamais produire ALLOW par défaut.

Cette règle est essentielle pour un domaine d'infrastructure critique.

Mais elle appartient à la gouvernance KX108, pas au Domain Pack Energy.

Energy peut produire des éléments qui conduisent KX108 à considérer HOLD/BLOCK.

Energy ne possède pas cette autorité.

## 7. Source conceptuelle interne

Les notes de projet auditées décrivent aussi une future `THERMO_COMPUTE_LAYER` mesurant notamment :

- temps ;
- énergie ;
- latence ;
- friction ;
- coût de chemin ;
- coût d'action / inaction ;
- coût d'inférence ;
- coût de preuve.

Elles mentionnent également d'anciens packs Energy sandbox / freeze / stress.

Ces références sont classées comme **sources conceptuelles internes**.

Elles soutiennent une direction de conception, mais ne sont pas déclarées comme dépendances runtime du Domain Pack.

## 8. Extensions déclarées V0

Le manifeste reconnaît maintenant deux familles.

### Thermo / Compute

- `thermo_compute`
- `energy_efficiency`
- `thermo_debt`
- `sigma_truth_mismatch`

### Physical Critical Infrastructure

- `physical_infrastructure`
- `fail_closed`
- `real_world_execution_constraints`

Ces extensions décrivent le **périmètre du Domain Pack**.

Elles ne valent ni object map, ni runtime, ni preuve.

## 9. Non-souveraineté

Invariants Energy :

```text
ENERGY METRIC != DECISION
ENERGY EFFICIENCY != AUTHORITY
THERMO DEBT != BLOCK AUTHORITY
SIGMA/TRUTH MISMATCH != FINAL VERDICT
BLOCK_CANDIDATE != BLOCK
PHYSICAL RISK != EXECUTION RIGHT
FAIL_CLOSED POLICY != DOMAIN AUTHORITY
DOMAIN != AUTHORITY
KX108_ONLY
```

## 10. Limite importante sur les tests actuels

Le repository contient :

- [test_energy_cannot_authorize.py](../../tests/non_sovereignty/test_energy_cannot_authorize.py)

Mais son contenu actuel est seulement :

```python
def test_non_sovereign():
    assert True
```

Ce fichier prouve uniquement qu'un **placeholder de test existe**.

Il ne démontre pas réellement que l'agent Energy ne peut pas autoriser.

Le README, le manifest et le profil de conformance ne doivent donc pas présenter ce test comme une preuve de non-souveraineté.

## 11. Source model

Le pack utilise `source_type: mixed_reference`.

### REPO_CODE_SOURCE

- `periphery/energy_thermo.py`
- `periphery/agents/energy_thermo_agent.py`

### REPO_SPEC_SOURCE

- `docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md`
- `specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md`

### REPO_TEST_PLACEHOLDER

- `tests/non_sovereignty/test_energy_cannot_authorize.py`

### INTERNAL_CONCEPT_SOURCE

- `internal://THERMO_COMPUTE_LAYER`
- `internal://Energy sandbox/freeze/stress history`

## 12. Point de branchement cible

### Thermo path

```text
ActionCandidate
→ Energy Thermo measurement
→ PeripheralSignalPacket
→ risk / contradiction / metrics
→ DomainSignal candidate
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
```

### Critical infrastructure path

```text
physical infrastructure source
→ state / provenance / authenticity
→ physical risk / constraints
→ DomainSignal
→ CanonicalDomainContract
→ GovernancePayload
→ KX108
→ Binder si conséquence
→ execution capability
→ Receipt / Replay
```

## 13. Conformance

Le profil Energy impose désormais au niveau documentaire :

```text
ENERGY METRIC != DECISION
THERMO DEBT != BLOCK AUTHORITY
BLOCK_CANDIDATE != BLOCK
PHYSICAL RISK != EXECUTION RIGHT
KX108_ONLY
```

Les vrais tests correspondants restent à implémenter.

Voir [conformance.md](conformance.md).

## 14. Manques

Le pack reste incomplet sur :

- object map ;
- classification exacte des objets Thermo vs Critical Infrastructure ;
- DomainSignal Energy natif ;
- adapter physique ;
- provenance/authenticity pour infrastructure réelle ;
- Binder path ;
- receipts/replay spécifiques ;
- tests de non-souveraineté réels ;
- tests fail-closed domaine ;
- démonstration de séparation entre advisory Thermo et action physique.

## 15. Object-model candidate audit

L'audit READ_ONLY des candidats est maintenant documenté dans [OBJECT_MODEL_CANDIDATES_V0.md](OBJECT_MODEL_CANDIDATES_V0.md).

Verdict :

```text
objets prêts à promouvoir = 0
```

Les métriques Energy/Thermo restent des métriques, et les objets Physical Critical Infrastructure restent sous-définis.

Le `object_map.yaml` reste volontairement vide.