# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-29 15:54:31
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260429_155300`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 3968 |
| Decisions avant audit | 8637 |
| Decisions apres audit | 8675 |
| Decisions creees pendant audit | 38 |
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
| bank | `988680FD35AD` | `9E5E66660599` | `E830BFCA2EB4` | 6 | `F4E7159EC996; 089DC31BD04F; 68F5E06DEBBA; 79030AECBA63; 49743A0B2F81; 089B673DF28A` |
| trading | `A09D6DEE2AD5` | `4AF6FFA12D70` | `0FEC938933C0` | 19 | `3959DDB8EE43; 4C2ABFE3FDD3; 22454EF4B1E6; 1486443BE520; A5639302AF22; 62E4DEDBA5F3; 67295A87F7C1; 5A9FCCE31BB0; 046D449D310D; 5749651B8212; B37422A7EAB5; F8C0651965E9; EEDAF7B605B1; BFAB99AA914A; 9077B03A06D8; B388E32ED1DC; 904FD94FBBC9; B5327AB0FD9D; 9C86A4146404` |
| gps_defense_aviation | `0E9835CD2BEB` | `133B8B181B9E` | `AB66C0B57AEA` | 13 | `B89BDCF66027; B51477DBB550; 5F7D54DC3CF1; 4135CB9CD8FB; FD046BCC116E; CBE3E491F6B9; D8B30F91A3C0; 50A3F3B6F1C7; 1332C2A47CF4; 515C9C3CAC76; B8AD1F3BC08E; 15E67AE171F6; A808A3A434FE` |

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
| `decision_bank_1777470790884.json` | 3468 | `F4E7159EC996` |
| `decision_bank_1777470801464.json` | 3468 | `089DC31BD04F` |
| `decision_bank_1777470811801.json` | 3468 | `68F5E06DEBBA` |
| `decision_bank_1777470822298.json` | 3468 | `79030AECBA63` |
| `decision_bank_1777470834231.json` | 3468 | `49743A0B2F81` |
| `decision_bank_1777470836201.json` | 3720 | `089B673DF28A` |
| `decision_gps_defense_aviation_1777470782756.json` | 3349 | `B89BDCF66027` |
| `decision_gps_defense_aviation_1777470787194.json` | 3349 | `B51477DBB550` |
| `decision_gps_defense_aviation_1777470791648.json` | 3349 | `5F7D54DC3CF1` |
| `decision_gps_defense_aviation_1777470796192.json` | 3349 | `4135CB9CD8FB` |
| `decision_gps_defense_aviation_1777470800728.json` | 3349 | `FD046BCC116E` |
| `decision_gps_defense_aviation_1777470805451.json` | 3349 | `CBE3E491F6B9` |
| `decision_gps_defense_aviation_1777470809859.json` | 3349 | `D8B30F91A3C0` |
| `decision_gps_defense_aviation_1777470814253.json` | 3349 | `50A3F3B6F1C7` |
| `decision_gps_defense_aviation_1777470818705.json` | 3349 | `1332C2A47CF4` |
| `decision_gps_defense_aviation_1777470823232.json` | 3349 | `515C9C3CAC76` |
| `decision_gps_defense_aviation_1777470827734.json` | 3349 | `B8AD1F3BC08E` |
| `decision_gps_defense_aviation_1777470834659.json` | 3349 | `15E67AE171F6` |
| `decision_gps_defense_aviation_1777470837539.json` | 3448 | `A808A3A434FE` |
| `decision_trading_1777470783587.json` | 3520 | `3959DDB8EE43` |
| `decision_trading_1777470786664.json` | 3520 | `4C2ABFE3FDD3` |
| `decision_trading_1777470789545.json` | 3520 | `22454EF4B1E6` |
| `decision_trading_1777470792665.json` | 3520 | `1486443BE520` |
| `decision_trading_1777470796017.json` | 3520 | `A5639302AF22` |
| `decision_trading_1777470799095.json` | 3520 | `62E4DEDBA5F3` |
| `decision_trading_1777470802126.json` | 3520 | `67295A87F7C1` |
| `decision_trading_1777470805458.json` | 3520 | `5A9FCCE31BB0` |
| `decision_trading_1777470808515.json` | 3520 | `046D449D310D` |
| `decision_trading_1777470811314.json` | 3520 | `5749651B8212` |
| `decision_trading_1777470814335.json` | 3520 | `B37422A7EAB5` |
| `decision_trading_1777470817240.json` | 3520 | `F8C0651965E9` |
| `decision_trading_1777470820283.json` | 3520 | `EEDAF7B605B1` |
| `decision_trading_1777470823212.json` | 3520 | `BFAB99AA914A` |
| `decision_trading_1777470826597.json` | 3520 | `9077B03A06D8` |
| `decision_trading_1777470829761.json` | 3520 | `B388E32ED1DC` |
| `decision_trading_1777470834481.json` | 3520 | `904FD94FBBC9` |
| `decision_trading_1777470837170.json` | 3461 | `B5327AB0FD9D` |
| `decision_trading_1777470837444.json` | 3520 | `9C86A4146404` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `F29B64CE40ACB6E03294F5A9C679BEB12911AB3F5EF197645F7D4D2971EEAC59` |
| Merkle after | `AE7759DB46DF38C98A8B798C2320BE8190327F557A388E127F5176CE368D3EA9` |
| Server stdout | `8BF4E27ECCB7E8436EC7B8C80F33ADE198ACD8678CF6EFBC81625BEE1645483F` |
| Server stderr | `EEC9CA7AA1F6CC896972506462E401EFA97BFD69380121CFECF726CB39225D3D` |
| Trace manifest | `9EF88D52FACC0884AC3618C91E241631A2C3A08580CF2A1871D8FE88020F7C60` |
| Audit root | `cf775295451df9588808cc0595d0202eb81e1ccecb8593aff049b6986f623c9c` |

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
| Tracabilite decisions | 38 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=9EF88D52FACC0884AC3618C91E241631A2C3A08580CF2A1871D8FE88020F7C60 | OK |
| Racine audit | AUDIT_ROOT_SHA256=cf775295451df9588808cc0595d0202eb81e1ccecb8593aff049b6986f623c9c | OK |
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
| `response_bank.json` | 6966 | `9E5E66660599` |
| `response_trading.json` | 6708 | `4AF6FFA12D70` |
| `response_gps_defense_aviation.json` | 6341 | `133B8B181B9E` |
| `metrics_full_bank.csv` | 8121 | `E830BFCA2EB4` |
| `metrics_full_trading.csv` | 8153 | `0FEC938933C0` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `AB66C0B57AEA` |
| `ALL_METRICS_FLAT.csv` | 25120 | `216EDFA48418` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 5061 | `05F81FCEC1EE` |
| `TRACE_STATS.json` | 1034 | `1FED9E64703D` |
| `TRACE_MANIFEST.json` | 58893 | `9EF88D52FACC` |
| `decisions_before.csv` | 2304868 | `A9B73B207432` |
| `decisions_after.csv` | 2315012 | `F27780431D99` |
| `decisions_created_during_audit.csv` | 9348 | `0EBB67BC1A5C` |
| `decision_runtime_metrics_flat.csv` | 575471 | `3A0898232043` |
| `runtime_file_hashes.csv` | 1337 | `C8FCC0B40BB8` |
| `server.stdout.log` | 1100 | `8BF4E27ECCB7` |
| `server.stderr.log` | 4910 | `EEC9CA7AA1F6` |
| `merkle_seal_before.json` | 317 | `F29B64CE40AC` |
| `merkle_seal_after.json` | 317 | `AE7759DB46DF` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
