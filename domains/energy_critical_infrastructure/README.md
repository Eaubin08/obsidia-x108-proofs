# Energy / Critical Infrastructure

> Domain Pack pour énergie, thermodynamique computationnelle et contraintes d'infrastructure critique.
>
> **UDIP status : `NEW_DOMAIN_SCAFFOLD`**  
> **Implementation state : `SCAFFOLD_ONLY`**  
> **Authority : `KX108_ONLY`**

## 1. Vision

Energy possède déjà plus qu'un simple mot dans un registre.

Deux axes conceptuels existent :

1. **Thermo / compute energy** : mesurer coût, efficacité, dette thermodynamique, friction et mismatch ;
2. **Critical infrastructure** : traiter les actions physiques avec fail-closed et frontières d'exécution du monde réel.

Ces axes ne doivent pas être fusionnés trop vite.

## 2. Matière réelle existante

Sources fortes :

- [Energy Thermo Governor](../../docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md) ;
- [Energy Thermo implementation](../../periphery/energy_thermo.py) ;
- [Energy Thermo Agent](../../periphery/agents/energy_thermo_agent.py) ;
- [Fail Closed Priority](../../specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md) ;
- [Energy cannot authorize](../../tests/non_sovereignty/test_energy_cannot_authorize.py).

Le module `run_energy_thermo` calcule déjà notamment :

- `energy_efficiency` ;
- `thermo_debt` ;
- `truth_score` ;
- `sigma_score` ;
- `sigma_truth_mismatch`.

Il peut produire des risques comme :

- `ENERGY_INEFFICIENT` ;
- `THERMO_DEBT_HIGH` ;
- `SIGMA_TRUTH_MISMATCH` ;

et des recommandations `HOLD` / `BLOCK_CANDIDATE`.

Important : il produit un `PeripheralSignalPacket`, pas une décision.

## 3. Source conceptuelle interne

Les notes projet historiques décrivent aussi une future `THERMO_COMPUTE_LAYER` chargée de mesurer :

- temps ;
- énergie ;
- latence ;
- friction ;
- coût de chemin ;
- coût d'action / inaction ;
- coût d'inférence ;
- coût de preuve.

Elles citent également plusieurs anciens packs sandbox/freeze/stress Energy.

Ces références soutiennent la vision, mais ne doivent pas être transformées en état runtime sans audit des artefacts correspondants.

## 4. Périmètre déclaré

`domain_pack.yaml` déclare :

- `physical_infrastructure` ;
- `fail_closed` ;
- `real_world_execution_constraints`.

Ce périmètre élargit Energy au-delà du seul coût computationnel.

## 5. Séparation des deux niveaux

### A. Energy / Thermo advisory

```text
action candidate
→ energy/thermo measurement
→ PeripheralSignalPacket
→ risk / contradiction
→ governed context
→ KX108
```

### B. Critical infrastructure

```text
physical source/state
→ authenticity / constraints
→ critical-infrastructure DomainSignal
→ KX108
→ Binder
→ physical executor
→ outcome / receipt / replay
```

Le niveau B n'est pas encore implémenté comme Domain Pack complet.

## 6. Fail-closed

La spec `FAIL_CLOSED_PRIORITY_SPEC` verrouille :

```text
BLOCK > HOLD > ALLOW
```

et interdit ALLOW par défaut en cas d'incertitude critique.

Cette règle est particulièrement pertinente pour l'énergie et les infrastructures critiques, mais elle reste une règle d'autorité KX108, pas une règle possédée par le domaine.

## 7. Non-souveraineté

```text
ENERGY METRIC != DECISION
THERMO DEBT != BLOCK AUTHORITY
PHYSICAL RISK != EXECUTION RIGHT
DOMAIN != AUTHORITY
KX108_ONLY
```

## 8. État réel du pack

Le Domain Pack lui-même reste :

- `source_type: none` ;
- `sources.yaml: NOT_YET_DEFINED` ;
- `object_map` non implémenté ;
- `SCAFFOLD_ONLY`.

La présence d'un agent Energy Thermo réel dans `periphery/` ne signifie donc pas encore “Energy UDIP intégré”.

## 9. Sources

- [Domain Concept Source Audit](../../planning/DOMAIN_CONCEPT_SOURCE_AUDIT_V0.md)
- [Energy Thermo Governor](../../docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md)
- [Fail Closed Priority](../../specs/01_X108_AUTHORITY/FAIL_CLOSED_PRIORITY_SPEC.md)
- [UDIP V0](../../docs/UNIVERSAL_DOMAIN_INTEGRATION_PROTOCOL_V0.md)

## 10. Prochaine étape

Le prochain vrai travail n'est pas d'ajouter plus de métriques.

Il faut décider explicitement si le Domain Pack Energy V0 couvre :

```text
A. compute / thermo energy
B. physical energy infrastructure
C. les deux avec deux sous-contrats séparés
```

puis créer l'object map correspondant sans déplacer l'autorité hors de KX108.
