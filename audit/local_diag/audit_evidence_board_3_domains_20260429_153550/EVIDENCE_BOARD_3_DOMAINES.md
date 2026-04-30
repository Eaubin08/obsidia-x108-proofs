# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-29 15:37:10
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260429_153550`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 3023 |
| Decisions avant audit | 8187 |
| Decisions apres audit | 8216 |
| Decisions creees pendant audit | 29 |
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
| bank | `988680FD35AD` | `3F5BF5A58D6D` | `2E0F3001CD64` | 6 | `FE750BBCD022; FC81DCFDAE7B; 2C14E9891A2B; EFCE9918328D; 307792A2856D; 51CB0E588EB4` |
| trading | `A09D6DEE2AD5` | `717F72699F46` | `9F8C712477A8` | 13 | `09DE50B637FC; FA009C375380; AE9E067A1601; 8408223EEB00; 3396A6AB4B27; FE1247CD3A4A; 87CC16DA70D3; F8BDC54A1A21; 6912343A0542; BAD1E7B7A809; 193904D0E49A; AF45B4FF4213; EA3B84D0F7C8` |
| gps_defense_aviation | `0E9835CD2BEB` | `95B65E9635BB` | `9CEE4B2E72B5` | 10 | `25FDAA05F1D2; FAA07BB0B277; 99FAB050B932; 4B33D9368DF2; 4F83BDEB8EAE; D6BE2C1E33EA; 4D56E7EC593C; 591301A3253E; FE00676B9015; FB744D851530` |

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
| `decision_bank_1777469753236.json` | 3468 | `FE750BBCD022` |
| `decision_bank_1777469763706.json` | 3468 | `FC81DCFDAE7B` |
| `decision_bank_1777469774474.json` | 3468 | `2C14E9891A2B` |
| `decision_bank_1777469784829.json` | 3468 | `EFCE9918328D` |
| `decision_bank_1777469793586.json` | 3720 | `307792A2856D` |
| `decision_bank_1777469795260.json` | 3468 | `51CB0E588EB4` |
| `decision_gps_defense_aviation_1777469754510.json` | 3349 | `25FDAA05F1D2` |
| `decision_gps_defense_aviation_1777469758836.json` | 3349 | `FAA07BB0B277` |
| `decision_gps_defense_aviation_1777469763292.json` | 3349 | `99FAB050B932` |
| `decision_gps_defense_aviation_1777469767741.json` | 3349 | `4B33D9368DF2` |
| `decision_gps_defense_aviation_1777469772199.json` | 3349 | `4F83BDEB8EAE` |
| `decision_gps_defense_aviation_1777469777058.json` | 3349 | `D6BE2C1E33EA` |
| `decision_gps_defense_aviation_1777469781451.json` | 3349 | `4D56E7EC593C` |
| `decision_gps_defense_aviation_1777469785768.json` | 3349 | `591301A3253E` |
| `decision_gps_defense_aviation_1777469792317.json` | 3349 | `FE00676B9015` |
| `decision_gps_defense_aviation_1777469795165.json` | 3448 | `FB744D851530` |
| `decision_trading_1777469754705.json` | 3520 | `09DE50B637FC` |
| `decision_trading_1777469757935.json` | 3520 | `FA009C375380` |
| `decision_trading_1777469760987.json` | 3520 | `AE9E067A1601` |
| `decision_trading_1777469764324.json` | 3520 | `8408223EEB00` |
| `decision_trading_1777469767583.json` | 3520 | `3396A6AB4B27` |
| `decision_trading_1777469770507.json` | 3520 | `FE1247CD3A4A` |
| `decision_trading_1777469773288.json` | 3520 | `87CC16DA70D3` |
| `decision_trading_1777469776725.json` | 3520 | `F8BDC54A1A21` |
| `decision_trading_1777469779826.json` | 3520 | `6912343A0542` |
| `decision_trading_1777469783193.json` | 3520 | `BAD1E7B7A809` |
| `decision_trading_1777469786372.json` | 3520 | `193904D0E49A` |
| `decision_trading_1777469794571.json` | 3461 | `AF45B4FF4213` |
| `decision_trading_1777469794919.json` | 3520 | `EA3B84D0F7C8` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `238828A3E15E8F114308CFFC80F87C641A97F187E02199F5F435C565982BA1EE` |
| Merkle after | `D1C718EB73695934CFFCA9AA3F89C6639057273C1708D4A2C4C5E19F4E4600D0` |
| Server stdout | `114B6C4E2FCA01FC6D273E7794350281E90938558A93B4C48528DAF0943EA25D` |
| Server stderr | `0166E257B5E6C83F3B748A5756566E48B23CFA02CB381330B461D1F9EEFB7E95` |
| Trace manifest | `E8BCC7A472CE39D6CAFD76FF719A48A48A845EE3D7C700D127D9D522CA69F4C1` |
| Audit root | `802fcd3d7e56e257e9ada83de883cccd19e5488acccccc917efcb6846d41f916` |

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
| Tracabilite decisions | 29 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=E8BCC7A472CE39D6CAFD76FF719A48A48A845EE3D7C700D127D9D522CA69F4C1 | OK |
| Racine audit | AUDIT_ROOT_SHA256=802fcd3d7e56e257e9ada83de883cccd19e5488acccccc917efcb6846d41f916 | OK |
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
| `response_bank.json` | 6966 | `3F5BF5A58D6D` |
| `response_trading.json` | 6708 | `717F72699F46` |
| `response_gps_defense_aviation.json` | 6341 | `95B65E9635BB` |
| `metrics_full_bank.csv` | 8121 | `2E0F3001CD64` |
| `metrics_full_trading.csv` | 8153 | `9F8C712477A8` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `9CEE4B2E72B5` |
| `ALL_METRICS_FLAT.csv` | 25120 | `AA7BEB5A23EC` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 4095 | `D0601CA07675` |
| `TRACE_STATS.json` | 1034 | `3A923D14EFF9` |
| `TRACE_MANIFEST.json` | 53385 | `E8BCC7A472CE` |
| `decisions_before.csv` | 2184702 | `E18FC8D00755` |
| `decisions_after.csv` | 2192437 | `FAAAABEEB08C` |
| `decisions_created_during_audit.csv` | 7137 | `A92594D3B8A7` |
| `decision_runtime_metrics_flat.csv` | 437822 | `39FA81285486` |
| `runtime_file_hashes.csv` | 1337 | `16AA5D044A1C` |
| `server.stdout.log` | 949 | `114B6C4E2FCA` |
| `server.stderr.log` | 4517 | `0166E257B5E6` |
| `merkle_seal_before.json` | 317 | `238828A3E15E` |
| `merkle_seal_after.json` | 317 | `D1C718EB7369` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
