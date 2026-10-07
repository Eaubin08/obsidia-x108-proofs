# F10 — Première mise au monde — double démonstration V0

F10 montre deux consommateurs radicalement différents traversant la même frontière gouvernée :

```
GPS enregistré réel -> MMonde -> UDIP GPS -> GuardX108 -> CanonicalDecisionEnvelope -> Proof
Brody/GMS cognitif  -> MMonde -> UDIP enterprise -> GuardX108 -> CanonicalDecisionEnvelope -> Proof
```

## Invariants

- MMonde représente ; il ne décide pas.
- Le domaine traduit ; il ne donne aucune permission.
- Brody/GMS propose/représente ; il n'obtient aucune autorité d'action.
- GuardX108 reste l'unique frontière de décision : `KX108_ONLY`.
- Le proof packet lie les références monde/domaine à l'enveloppe canonique mais n'autorise ni décision ni exécution.
- Les unknowns/contradictions ne sont pas complétés silencieusement.

## GPS

Le scénario F10 s'appuie sur le type `RecordedGpsEvidenceV0` déjà fermé en F5. Il accepte la provenance enregistrée réelle sans la promouvoir en authenticité physique/live. `BLOCKED_RECEIVER_CONFIGURATION` reste un blocker explicite et doit conduire à un résultat fail-closed.

L'artefact existant `artifacts/gps_rinex_noaa_ab02_2026_210_real_result.json` fournit la référence enregistrée réelle : RINEX NOAA AB02, 31 satellites uniques, `synthetic=false`, `proof_level=RECORDED_REAL_GNSS`. F10 ne transforme pas cette preuve enregistrée en claim LIVE.

## Brody / GMS

Le scénario cognitif introduit seulement une observation MMonde conservatrice (`CognitiveEvidenceV0`). Il conserve source, hash, evidence refs, unknowns et contradictions. Il ne prétend pas que le contenu cognitif est vrai.

Le vocabulaire canonique KX108 actuel n'exposant pas de domaine souverain `brody`, F10 utilise le domaine générique existant `enterprise` au lieu d'inventer un nouveau domaine kernel. Ce choix est volontaire et devra être revu si un contrat domaine Brody/GMS canonique est ajouté.

## Critère F10

F10 est vérifié lorsque les tests prouvent que les deux chemins :
1. produisent une vraie `CanonicalDecisionEnvelope` via `GuardX108`;
2. produisent un `GovernedWorldDecisionProofV0` vérifiable;
3. conservent `KX108_ONLY`;
4. n'accordent aucune autorité d'exécution;
5. restent fail-closed lorsque les unknowns/blockers l'exigent.

F10 ne ferme pas le GPS LIVE/hostile RF et ne remplace pas l'implémentation GMS/SENS différée après freeze stable.
