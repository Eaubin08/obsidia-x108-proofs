# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-29 00:50:21
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260429_004904`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 1050 |
| Decisions avant audit | 7802 |
| Decisions apres audit | 7812 |
| Decisions creees pendant audit | 10 |
| Fichiers runtime hashes | 13 |
| Artefacts de preuve hashes | 23 |

## 2. Git / version

| Champ | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `fe801ddadf851b7e2ce5b2bb11612396999b5ef6` |
| Tags HEAD | `audit-evidence-board-v2-20260428-233523` |
| Status | ` M merkle_seal.json; ?? RUN_AUDIT_TABLEAU_POST_EVIDENCE.ps1` |

## 3. Tableau decisionnel

| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bank | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 |
| trading | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 |

## 4. Chaines de trace par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Decision count | Decision hashes |
|---|---:|---:|---:|---:|---|
| bank | `988680FD35AD` | `D72F99A184BD` | `8C2274F17E0C` | 1 | `05B5211E1050` |
| trading | `A09D6DEE2AD5` | `F91706A9E079` | `284E08F17C3B` | 5 | `3BE4B09F6D67; DA769ED78AD0; 0EF00EAA7617; 48591BDAC749; 72F9C77F1EEC` |
| gps_defense_aviation | `0E9835CD2BEB` | `8FF7C5374B9F` | `37D828E84354` | 4 | `07FCDBF91305; AA0832926B0F; 22D3329C5A3D; 6694CFCDBC8F` |

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
| `decision_bank_1777416582202.json` | 3720 | `05B5211E1050` |
| `decision_gps_defense_aviation_1777416573988.json` | 3349 | `07FCDBF91305` |
| `decision_gps_defense_aviation_1777416578429.json` | 3349 | `AA0832926B0F` |
| `decision_gps_defense_aviation_1777416582784.json` | 3349 | `22D3329C5A3D` |
| `decision_gps_defense_aviation_1777416583380.json` | 3448 | `6694CFCDBC8F` |
| `decision_trading_1777416574017.json` | 3520 | `3BE4B09F6D67` |
| `decision_trading_1777416576529.json` | 3520 | `DA769ED78AD0` |
| `decision_trading_1777416580796.json` | 3520 | `0EF00EAA7617` |
| `decision_trading_1777416582953.json` | 3461 | `48591BDAC749` |
| `decision_trading_1777416583523.json` | 3520 | `72F9C77F1EEC` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542` |
| Merkle after | `E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542` |
| Server stdout | `C1821A010EEE6F01A37414D923BD0E4C136071314D9C132741D3E641B6BC7CE8` |
| Server stderr | `0DB70D1A27E32F28C8A7905779207F8463F2C28345C56D11FACB18A40744ADF1` |
| Trace manifest | `BC85176DF2D978F3C8ECED87A70A046F716C5C0B80B7F841BF8B75F2489D3A72` |
| Audit root | `3bcd27cac02974dba6932bfc98c1f3ecddba45b3208afed350bf4bad6469dc11` |

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
| Tracabilite decisions | 10 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=BC85176DF2D978F3C8ECED87A70A046F716C5C0B80B7F841BF8B75F2489D3A72 | OK |
| Racine audit | AUDIT_ROOT_SHA256=3bcd27cac02974dba6932bfc98c1f3ecddba45b3208afed350bf4bad6469dc11 | OK |
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
| `response_bank.json` | 6966 | `D72F99A184BD` |
| `response_trading.json` | 6708 | `F91706A9E079` |
| `response_gps_defense_aviation.json` | 6341 | `8FF7C5374B9F` |
| `metrics_full_bank.csv` | 8121 | `8C2274F17E0C` |
| `metrics_full_trading.csv` | 8153 | `284E08F17C3B` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `37D828E84354` |
| `ALL_METRICS_FLAT.csv` | 25120 | `65EFB9E770C0` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 2073 | `7D7F7AE76DC4` |
| `TRACE_STATS.json` | 1034 | `5877C3A80EF5` |
| `TRACE_MANIFEST.json` | 41813 | `BC85176DF2D9` |
| `decisions_before.csv` | 2081563 | `E52F1AC63E06` |
| `decisions_after.csv` | 2084251 | `27B000627160` |
| `decisions_created_during_audit.csv` | 2508 | `985E00B1728E` |
| `decision_runtime_metrics_flat.csv` | 153997 | `D8AC5ECDC9A2` |
| `runtime_file_hashes.csv` | 1337 | `F8A8E4D23E91` |
| `server.stdout.log` | 955 | `C1821A010EEE` |
| `server.stderr.log` | 4617 | `0DB70D1A27E3` |
| `merkle_seal_before.json` | 317 | `E264FA8A8D42` |
| `merkle_seal_after.json` | 317 | `E264FA8A8D42` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
