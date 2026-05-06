# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-28 22:55:06
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260428_225358`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 321 |
| Decisions avant audit | 7234 |
| Decisions apres audit | 7237 |
| Decisions creees pendant audit | 3 |
| Fichiers runtime hashes | 13 |
| Artefacts de preuve hashes | 23 |

## 2. Git / version

| Champ | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `977bb2fa5a2ccccd60e8e509f59695dc463ec995` |
| Tags HEAD | `audit-traceability-3-domains-20260428-223139` |
| Status | ` M merkle_seal.json; ?? RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1; ?? RUN_AUDIT_TOTAL_METRICS_PROOF.ps1` |

## 3. Tableau decisionnel

| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bank | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 |
| trading | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 |

## 4. Chaines de trace par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Decision count | Decision hashes |
|---|---:|---:|---:|---:|---|
| bank | `988680FD35AD` | `768BFFE28568` | `17668378077E` | 1 | `AB0D40F3CC36` |
| trading | `A09D6DEE2AD5` | `45D8C6E72BA3` | `40C5E0668816` | 1 | `37B891B92628` |
| gps_defense_aviation | `0E9835CD2BEB` | `DA5303E8B7DF` | `4CEBE97C4FE8` | 1 | `D6CD1C6510F6` |

## 5. Categories de metriques

| Domaine | Categorie | Nombre |
|---|---|---:|
| trading | evidence_refs | 27 |
| bank | evidence_refs | 22 |
| bank | sigma_report | 21 |
| trading | sigma_report | 21 |
| gps_defense_aviation | sigma_report | 21 |
| trading | raw_engine | 19 |
| gps_defense_aviation | evidence_refs | 16 |
| bank | raw_engine | 14 |
| gps_defense_aviation | unknowns | 13 |
| bank | unknowns | 9 |
| gps_defense_aviation | metrics | 9 |
| bank | sigma_step | 8 |
| gps_defense_aviation | sigma_step | 8 |
| bank | contradictions | 8 |
| trading | sigma_step | 8 |
| gps_defense_aviation | raw_engine | 8 |
| bank | metrics | 5 |
| trading | array_empty | 5 |
| trading | metrics | 5 |
| gps_defense_aviation | contradictions | 4 |
| trading | risk_flags | 4 |
| gps_defense_aviation | array_empty | 4 |
| bank | array_empty | 3 |
| bank | risk_flags | 2 |
| gps_defense_aviation | null | 1 |
| trading | source | 1 |
| gps_defense_aviation | domain | 1 |
| gps_defense_aviation | confidence | 1 |
| gps_defense_aviation | market_verdict | 1 |
| trading | sigma_override | 1 |
| gps_defense_aviation | sigma_override | 1 |
| bank | domain | 1 |
| gps_defense_aviation | source | 1 |
| gps_defense_aviation | attestation_ref | 1 |
| gps_defense_aviation | decision_id | 1 |
| gps_defense_aviation | trace_id | 1 |
| gps_defense_aviation | ticket_required | 1 |
| gps_defense_aviation | x108_gate | 1 |
| gps_defense_aviation | reason_code | 1 |
| gps_defense_aviation | severity | 1 |
| gps_defense_aviation | confidence_readiness | 1 |
| gps_defense_aviation | confidence_governance | 1 |
| gps_defense_aviation | confidence_integrity | 1 |
| gps_defense_aviation | readiness_scope | 1 |
| gps_defense_aviation | governance_scope | 1 |
| gps_defense_aviation | confidence_scope | 1 |
| trading | attestation_ref | 1 |
| bank | decision_id | 1 |
| bank | trace_id | 1 |
| bank | reason_code | 1 |
| bank | severity | 1 |
| bank | attestation_ref | 1 |
| bank | source | 1 |
| bank | ticket_required | 1 |
| bank | null | 1 |
| bank | x108_gate | 1 |
| bank | confidence_integrity | 1 |
| bank | confidence_governance | 1 |
| bank | market_verdict | 1 |
| bank | confidence | 1 |
| bank | governance_scope | 1 |
| bank | readiness_scope | 1 |
| bank | confidence_readiness | 1 |
| bank | confidence_scope | 1 |
| trading | reason_code | 1 |
| trading | severity | 1 |
| trading | readiness_scope | 1 |
| trading | x108_gate | 1 |
| trading | ticket_required | 1 |
| trading | null | 1 |
| trading | decision_id | 1 |
| trading | trace_id | 1 |
| trading | governance_scope | 1 |
| trading | market_verdict | 1 |
| trading | confidence | 1 |
| bank | sigma_override | 1 |
| trading | domain | 1 |
| trading | confidence_readiness | 1 |
| trading | confidence_scope | 1 |
| trading | confidence_integrity | 1 |
| trading | confidence_governance | 1 |

## 6. Decisions runtime creees pendant audit

| Fichier | Taille | SHA256 court |
|---|---:|---:|
| `decision_bank_1777409674870.json` | 3720 | `AB0D40F3CC36` |
| `decision_gps_defense_aviation_1777409675897.json` | 3448 | `D6CD1C6510F6` |
| `decision_trading_1777409675567.json` | 3461 | `37B891B92628` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256` |
| Merkle after | `9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256` |
| Server stdout | `32B18FD654F2C6FD7C511617B79FEF86F5D70A498B506468B913E3C1A6B58F18` |
| Server stderr | `FE0A8BB0265FF1E4C0C52C679996E4D0BB399CB2991CDADE5B61BC05BA3D5CC7` |
| Trace manifest | `1D979B77F86B9C94D3315CF7F56CDD6ED0675971ABD2F3F963467497495BD605` |
| Audit root | `898787b5743cf6845229de158e20d44373dfe2ae67d1347818fc1789505397be` |

## 8. Matrice de preuves

| Axe | Preuve visible | Statut |
|---|---|---:|
| Routage multi-domaine | 3 domaines appellent le meme endpoint /kernel/ragnarok | OK |
| Decision avant action | Chaque domaine retourne verdict + gate X-108 avant execution | OK |
| Securite bank | bank retourne BLOCK sur transaction risquee | OK |
| Securite trading | trading retourne HOLD sur ordre risque | OK |
| Securite aviation | gps_defense_aviation retourne BLOCK sur navigation degradee | OK |
| Metrisation | 321 metriques response flattenees | OK |
| Tracabilite input | 3 payloads input sauvegardes + hashes | OK |
| Tracabilite output | 3 responses sauvegardees + hashes | OK |
| Tracabilite metrics | metrics_full_*.csv + ALL_METRICS_FLAT.csv | OK |
| Tracabilite decisions | 3 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=1D979B77F86B9C94D3315CF7F56CDD6ED0675971ABD2F3F963467497495BD605 | OK |
| Racine audit | AUDIT_ROOT_SHA256=898787b5743cf6845229de158e20d44373dfe2ae67d1347818fc1789505397be | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 9. Lecture securite

### bank

- Sens : Transaction bancaire mobile risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict : `ANALYZE`
- Gate X-108 : `BLOCK`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Severity : `S4`
- Lecture : REFUS AVANT EXECUTION : le moteur bloque l'action avant qu'elle ne puisse produire un effet.
- Metriques retournees : `111`
- Categories : `evidence_refs=22; sigma_report=21; raw_engine=14; unknowns=9; contradictions=8; sigma_step=8; metrics=5; array_empty=3; risk_flags=2; ticket_required=1; trace_id=1; null=1; attestation_ref=1; sigma_override=1; domain=1; source=1; confidence_governance=1; confidence_readiness=1; confidence_scope=1; market_verdict=1; confidence=1; confidence_integrity=1; reason_code=1; severity=1; decision_id=1; governance_scope=1; readiness_scope=1; x108_gate=1`

### trading

- Sens : Ordre de trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict : `REVIEW`
- Gate X-108 : `HOLD`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Severity : `S2`
- Lecture : TEMPORISATION X-108 : le moteur retient l'action et impose une attente/coherence supplementaire.
- Metriques retournees : `108`
- Categories : `evidence_refs=27; sigma_report=21; raw_engine=19; sigma_step=8; array_empty=5; metrics=5; risk_flags=4; trace_id=1; ticket_required=1; null=1; domain=1; sigma_override=1; attestation_ref=1; source=1; decision_id=1; confidence_governance=1; confidence_readiness=1; confidence_integrity=1; market_verdict=1; confidence=1; confidence_scope=1; reason_code=1; severity=1; x108_gate=1; governance_scope=1; readiness_scope=1`

### gps_defense_aviation

- Sens : Navigation aviation/GPS degradee : faible qualite signal, conflit source, risque spoofing, deviation et skew temporel.
- Verdict : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Severity : `S4`
- Lecture : REFUS AVANT EXECUTION : le moteur bloque l'action avant qu'elle ne puisse produire un effet.
- Metriques retournees : `102`
- Categories : `sigma_report=21; evidence_refs=16; unknowns=13; metrics=9; sigma_step=8; raw_engine=8; contradictions=4; array_empty=4; ticket_required=1; trace_id=1; null=1; sigma_override=1; domain=1; attestation_ref=1; source=1; decision_id=1; confidence_governance=1; confidence_readiness=1; confidence_integrity=1; market_verdict=1; confidence=1; confidence_scope=1; reason_code=1; severity=1; x108_gate=1; governance_scope=1; readiness_scope=1`

## 10. Tous les fichiers de preuve

| Fichier | Taille | SHA256 court |
|---|---:|---:|
| `input_bank.json` | 486 | `988680FD35AD` |
| `input_trading.json` | 263 | `A09D6DEE2AD5` |
| `input_gps_defense_aviation.json` | 335 | `0E9835CD2BEB` |
| `response_bank.json` | 6966 | `768BFFE28568` |
| `response_trading.json` | 6708 | `45D8C6E72BA3` |
| `response_gps_defense_aviation.json` | 6341 | `DA5303E8B7DF` |
| `metrics_full_bank.csv` | 8121 | `17668378077E` |
| `metrics_full_trading.csv` | 8153 | `40C5E0668816` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `4CEBE97C4FE8` |
| `ALL_METRICS_FLAT.csv` | 25120 | `13A5211D04F7` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 1313 | `9D19A0F0A98C` |
| `TRACE_STATS.json` | 1079 | `E0C1977C5C87` |
| `TRACE_MANIFEST.json` | 37595 | `1D979B77F86B` |
| `decisions_before.csv` | 1930029 | `F1A398E91E52` |
| `decisions_after.csv` | 1930826 | `4B80576096DA` |
| `decisions_created_during_audit.csv` | 771 | `B5AEECD539BA` |
| `decision_runtime_metrics_flat.csv` | 46192 | `955966AFDFFC` |
| `runtime_file_hashes.csv` | 1337 | `5B05BAC589E3` |
| `server.stdout.log` | 578 | `32B18FD654F2` |
| `server.stderr.log` | 2131 | `FE0A8BB0265F` |
| `merkle_seal_before.json` | 317 | `9D1D9AAEDCF8` |
| `merkle_seal_after.json` | 317 | `9D1D9AAEDCF8` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
