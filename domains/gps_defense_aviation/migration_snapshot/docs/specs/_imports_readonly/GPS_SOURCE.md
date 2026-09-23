# GPS_SOURCE

Import Type: READONLY_SOURCE_IMPORT

Original Source Paths:
- `periphery/adapters/gps_adapter.py`
- `connectors/aviation_robo.py`
- `sigma/domains/gps_defense_aviation_agents.py`
- `docs/periphery/GPS_ADAPTER_MAPPING_V0.md`
- `docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md`

Imported Facts:
- `gps_adapter.py` : DEFAULT_GPS_STATE avec mission_id, flight_id, altitude, ground_speed, gps_status, satellites_count, signal_noise_ratio, trajectory_drift_score, source_conflict_score, time_skew_score, brownout_score, attestation_ready, rollback_possible
- `aviation_robo.py` : POST vers `http://127.0.0.1:8000/api/periphery/monitoring/adapters/gps` — local uniquement
- Intent : `trajectory_integrity_review`
- Verdicts possibles (dans sigma domain) : ABORT_TRAJECTORY, RECALC_TRAJECTORY, TRAJECTORY_VALID
- `GPS_ENDPOINT = "/api/periphery/monitoring/adapters/gps"` — endpoint local

What This Source Proves:
- Un adaptateur GPS complet avec métriques de confiance est implémenté en Python
- Le connector aviation POST en local uniquement
- Les verdicts GPS sont des proposed_verdict — pas des ACT réels

What This Source Does NOT Prove:
- Déploiement en production défense
- Certification sécurité externe
- Que les verdicts GPS déclenchent des actuateurs physiques

Boundary:
- DRY_RUN — POST local `127.0.0.1` — pas de défense réelle

Claim-Scope:
- "Obsidia implémente un adaptateur GPS avec scoring de confiance" — AUTORISÉ
- "Obsidia est utilisable en défense/aviation en production" — INTERDIT

Specs Depending On This Source:
- 09_CRITICAL_WORLDS/GPS_DEFENSE_AVIATION_BOUNDARY_SPEC.md
- 09_CRITICAL_WORLDS/GPS_TO_X108_INTENT_CONTRACT.md
- 09_CRITICAL_WORLDS/AVIATION_CONNECTOR_X108_GATE_SPEC.md

Runtime Status: RUNTIME_CODE + DRY_RUN

Do Not Move Original Source: true
Authority: KX108_ONLY
