# Evidence Board - Obsidia X-108 - 3 domaines

Date : 2026-04-29 21:56:46
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit dir : `.\audit\local_diag\audit_evidence_board_3_domains_20260429_215445`

## 1. Synthese courte

| Element | Valeur |
|---|---:|
| Domaines testes | 3 |
| Metriques response totales | 321 |
| Metriques runtime decisions | 4386 |
| Decisions avant audit | 10251 |
| Decisions apres audit | 10293 |
| Decisions creees pendant audit | 42 |
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
| bank | `988680FD35AD` | `D157D5FBC3E9` | `906453CB4FD3` | 7 | `118C019185B5; FDAEBA78F9CF; ED12FA35BB35; 61033FBE7FCE; A0D397A78F70; 739F29EB6C66; 233136417EE0` |
| trading | `A09D6DEE2AD5` | `A4FAB62D399A` | `9F30DD34E5DE` | 21 | `E87C4EE29A09; 7498A2D32BE6; 4E30E261670A; 6B743E22E8B1; 6B02CACB06D3; 3B6539A9BD05; F9534BA3E306; 7BD25232D777; 958F94C6D852; FDDD0E7F87F2; FA3FAF36C3D4; D92DD1B3910E; 12591C865675; B92C7F028A1F; 079B46368973; 65E169EB47AA; 42492012AEBC; 88443E56DBF7; 9F204B54FC96; 2248A414DB80; 754EBE755F20` |
| gps_defense_aviation | `0E9835CD2BEB` | `73BD31468C4D` | `091229A99C7E` | 14 | `99306D0C6A87; EBE29217FB45; 3762FD7B30B8; 3C4FE7B31060; C2B335075373; 1D2BE548A171; 63B03BECC382; E616BF5BCC83; F9C310591F90; FB6DD1045224; 9101F94BF400; F6896207D3C7; 1D9CA0D1EC4E; 5995A9DC1248` |

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
| `decision_bank_1777492495888.json` | 3468 | `118C019185B5` |
| `decision_bank_1777492506178.json` | 3468 | `FDAEBA78F9CF` |
| `decision_bank_1777492517202.json` | 3468 | `ED12FA35BB35` |
| `decision_bank_1777492527598.json` | 3468 | `61033FBE7FCE` |
| `decision_bank_1777492538108.json` | 3468 | `A0D397A78F70` |
| `decision_bank_1777492548559.json` | 3468 | `739F29EB6C66` |
| `decision_bank_1777492549900.json` | 3720 | `233136417EE0` |
| `decision_gps_defense_aviation_1777492489663.json` | 3349 | `99306D0C6A87` |
| `decision_gps_defense_aviation_1777492494434.json` | 3349 | `EBE29217FB45` |
| `decision_gps_defense_aviation_1777492499183.json` | 3349 | `3762FD7B30B8` |
| `decision_gps_defense_aviation_1777492503624.json` | 3349 | `3C4FE7B31060` |
| `decision_gps_defense_aviation_1777492507935.json` | 3349 | `C2B335075373` |
| `decision_gps_defense_aviation_1777492512330.json` | 3349 | `1D2BE548A171` |
| `decision_gps_defense_aviation_1777492517321.json` | 3349 | `63B03BECC382` |
| `decision_gps_defense_aviation_1777492521686.json` | 3349 | `E616BF5BCC83` |
| `decision_gps_defense_aviation_1777492526142.json` | 3349 | `F9C310591F90` |
| `decision_gps_defense_aviation_1777492531073.json` | 3349 | `FB6DD1045224` |
| `decision_gps_defense_aviation_1777492535495.json` | 3349 | `9101F94BF400` |
| `decision_gps_defense_aviation_1777492540461.json` | 3349 | `F6896207D3C7` |
| `decision_gps_defense_aviation_1777492549230.json` | 3349 | `1D9CA0D1EC4E` |
| `decision_gps_defense_aviation_1777492551152.json` | 3448 | `5995A9DC1248` |
| `decision_trading_1777492491375.json` | 3520 | `E87C4EE29A09` |
| `decision_trading_1777492494366.json` | 3520 | `7498A2D32BE6` |
| `decision_trading_1777492497412.json` | 3520 | `4E30E261670A` |
| `decision_trading_1777492500650.json` | 3520 | `6B743E22E8B1` |
| `decision_trading_1777492503306.json` | 3520 | `6B02CACB06D3` |
| `decision_trading_1777492505833.json` | 3520 | `3B6539A9BD05` |
| `decision_trading_1777492508344.json` | 3520 | `F9534BA3E306` |
| `decision_trading_1777492510930.json` | 3520 | `7BD25232D777` |
| `decision_trading_1777492513662.json` | 3520 | `958F94C6D852` |
| `decision_trading_1777492517172.json` | 3520 | `FDDD0E7F87F2` |
| `decision_trading_1777492519796.json` | 3520 | `FA3FAF36C3D4` |
| `decision_trading_1777492522505.json` | 3520 | `D92DD1B3910E` |
| `decision_trading_1777492525210.json` | 3520 | `12591C865675` |
| `decision_trading_1777492527878.json` | 3520 | `B92C7F028A1F` |
| `decision_trading_1777492531214.json` | 3520 | `079B46368973` |
| `decision_trading_1777492534058.json` | 3520 | `65E169EB47AA` |
| `decision_trading_1777492536780.json` | 3520 | `42492012AEBC` |
| `decision_trading_1777492539450.json` | 3520 | `88443E56DBF7` |
| `decision_trading_1777492542099.json` | 3520 | `9F204B54FC96` |
| `decision_trading_1777492550485.json` | 3520 | `2248A414DB80` |
| `decision_trading_1777492550708.json` | 3461 | `754EBE755F20` |

## 7. Scellage / racines

| Element | SHA256 |
|---|---|
| Merkle before | `8FBECF80DBD2A2940171A2D637D1B2AB790A3E448882DD5C74A6BD88BC81E6F4` |
| Merkle after | `C0BAF87761049368442F8427BABDACD89047E6F0AE4076D2163EB69684A04016` |
| Server stdout | `DBE4436CA6DD14539A42E539E3E2AAC5D92A4FDF45E874348A706E2DA22873C0` |
| Server stderr | `6C4A2621FBABD96FC3AE31EBE49603BF31D38122C32105C94819224F190544CC` |
| Trace manifest | `C12AD7FEB84C9EA02216983FE5133D5121C54A3B2106F5312E329B03D857D734` |
| Audit root | `84536afa4ee72365775a381c7726034c68aa13c0ce4c382876045ca7b327cdcc` |

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
| Tracabilite decisions | 42 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=C12AD7FEB84C9EA02216983FE5133D5121C54A3B2106F5312E329B03D857D734 | OK |
| Racine audit | AUDIT_ROOT_SHA256=84536afa4ee72365775a381c7726034c68aa13c0ce4c382876045ca7b327cdcc | OK |
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
| `response_bank.json` | 6966 | `D157D5FBC3E9` |
| `response_trading.json` | 6708 | `A4FAB62D399A` |
| `response_gps_defense_aviation.json` | 6341 | `73BD31468C4D` |
| `metrics_full_bank.csv` | 8121 | `906453CB4FD3` |
| `metrics_full_trading.csv` | 8153 | `9F30DD34E5DE` |
| `metrics_full_gps_defense_aviation.csv` | 8938 | `091229A99C7E` |
| `ALL_METRICS_FLAT.csv` | 25120 | `22688F834758` |
| `ALL_METRIC_CATEGORIES.csv` | 2743 | `341AE4D7F898` |
| `TRACE_CHAINS_BY_DOMAIN.csv` | 5483 | `FA91DBCFA187` |
| `TRACE_STATS.json` | 1036 | `0ED59E1ACD66` |
| `TRACE_MANIFEST.json` | 61321 | `C12AD7FEB84C` |
| `decisions_before.csv` | 2736188 | `4FB986D0878F` |
| `decisions_after.csv` | 2747388 | `A91A1F31B423` |
| `decisions_created_during_audit.csv` | 10316 | `150F126D9A3F` |
| `decision_runtime_metrics_flat.csv` | 634997 | `634C510EC7F1` |
| `runtime_file_hashes.csv` | 1337 | `CA7BB3B09CFA` |
| `server.stdout.log` | 949 | `DBE4436CA6DD` |
| `server.stderr.log` | 4310 | `6C4A2621FBAB` |
| `merkle_seal_before.json` | 318 | `8FBECF80DBD2` |
| `merkle_seal_after.json` | 318 | `C0BAF8776104` |

## 11. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines.
