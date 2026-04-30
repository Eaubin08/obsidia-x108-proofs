# Post-audit structure V2 - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260429_215445
Date lecture : 2026-04-29 21:58:23

## 1. Lecture executive

Chaine prouvee : payload domaine -> endpoint Node -> pipeline Sigma/Python -> verdict metier -> gate X-108 -> decision runtime -> fichiers traces -> hashes -> manifest -> racine audit.

## 2. Tableau decisionnel

| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | MetricCount | Lecture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bank | ANALYZE | BLOCK | 0,5 | 0,95 | 0,66 | 0,7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 | REFUS AVANT ACTION |
| trading | REVIEW | HOLD | 0,5 | 0,75 | 0,6 | 0,6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 | TEMPORISATION X-108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0,35 | 0,95 | 0,51 | 0,6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 | REFUS AVANT ACTION |

## 3. Chaine de trace par domaine

| Domaine | InputSHA | ResponseSHA | MetricsSHA | MetricCount | DecisionCount | DecisionSHA | Gate | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bank | 988680FD35AD | D157D5FBC3E9 | 906453CB4FD3 | 111 | 7 | 118C019185B5 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading | A09D6DEE2AD5 | A4FAB62D399A | 9F30DD34E5DE | 108 | 21 | E87C4EE29A09 | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | 0E9835CD2BEB | 73BD31468C4D | 091229A99C7E | 102 | 14 | 99306D0C6A87 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 4386 | decision_runtime_metrics_flat.csv | Donnees extraites des decisions runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 42 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
| Fichiers runtime hashes | 13 | runtime_file_hashes.csv | Fichiers moteur critiques hashes |
| Claims preuve | 16 | PROOF_CLAIMS_MATRIX.csv | Axes de preuve declares OK |

## 5. Categories de metriques

| domain | category | metric_count |
| --- | --- | --- |
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

## 6. Matrice de preuves

| axe | preuve | statut |
| --- | --- | --- |
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

## 7. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | 8FBECF80DBD2A2940171A2D637D1B2AB790A3E448882DD5C74A6BD88BC81E6F4 | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | C0BAF87761049368442F8427BABDACD89047E6F0AE4076D2163EB69684A04016 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | C12AD7FEB84C9EA02216983FE5133D5121C54A3B2106F5312E329B03D857D734 | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | 84536afa4ee72365775a381c7726034c68aa13c0ce4c382876045ca7b327cdcc | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | CD05D427F3922DB1E1032494EC146A5F7EDA03C43D864E3FC4E9B2A1531F8B63 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | DBE4436CA6DD14539A42E539E3E2AAC5D92A4FDF45E874348A706E2DA22873C0 | server.stdout.log |
| SERVER_STDERR_SHA256 | 6C4A2621FBABD96FC3AE31EBE49603BF31D38122C32105C94819224F190544CC | server.stderr.log |

## 8. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777492495888.json | 3468 |  |  |
| decision_bank_1777492506178.json | 3468 |  |  |
| decision_bank_1777492517202.json | 3468 |  |  |
| decision_bank_1777492527598.json | 3468 |  |  |
| decision_bank_1777492538108.json | 3468 |  |  |
| decision_bank_1777492548559.json | 3468 |  |  |
| decision_bank_1777492549900.json | 3720 |  |  |
| decision_gps_defense_aviation_1777492489663.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492494434.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492499183.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492503624.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492507935.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492512330.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492517321.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492521686.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492526142.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492531073.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492535495.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492540461.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492549230.json | 3349 |  |  |
| decision_gps_defense_aviation_1777492551152.json | 3448 |  |  |
| decision_trading_1777492491375.json | 3520 |  |  |
| decision_trading_1777492494366.json | 3520 |  |  |
| decision_trading_1777492497412.json | 3520 |  |  |
| decision_trading_1777492500650.json | 3520 |  |  |
| decision_trading_1777492503306.json | 3520 |  |  |
| decision_trading_1777492505833.json | 3520 |  |  |
| decision_trading_1777492508344.json | 3520 |  |  |
| decision_trading_1777492510930.json | 3520 |  |  |
| decision_trading_1777492513662.json | 3520 |  |  |
| decision_trading_1777492517172.json | 3520 |  |  |
| decision_trading_1777492519796.json | 3520 |  |  |
| decision_trading_1777492522505.json | 3520 |  |  |
| decision_trading_1777492525210.json | 3520 |  |  |
| decision_trading_1777492527878.json | 3520 |  |  |
| decision_trading_1777492531214.json | 3520 |  |  |
| decision_trading_1777492534058.json | 3520 |  |  |
| decision_trading_1777492536780.json | 3520 |  |  |
| decision_trading_1777492539450.json | 3520 |  |  |
| decision_trading_1777492542099.json | 3520 |  |  |
| decision_trading_1777492550485.json | 3520 |  |  |
| decision_trading_1777492550708.json | 3461 |  |  |

## 9. Fichiers runtime hashes

| file | bytes | sha256 |
| --- | --- | --- |
| .\package.json | 429 | 5D1BE1EEF297C6FD72842450585EEF969F08AEC6A7DA52C99D4A415D48E2E646 |
| .\package-lock.json | 29833 | B461284B681814D76BBFA38676AD75E866F4276F1B2D0E3EE50A4805631985F7 |
| .\MonProjet\server.kernel.sealed.cjs | 3655 | DA2904C5D4604684B19CF557F602E7F65EC46E8B183C59F78CF9B3606F16FA78 |
| .\sigma\contracts.py | 16302 | 6FA4646032A2C2E82FC08C3563403A5FA86E41D2B312E170A960AF80FB995178 |
| .\sigma\aggregation.py | 6001 | 3F5EFD090286212E5B837AFEA9FCDB35E0456DF431E90A52B3986938EADC8A49 |
| .\sigma\guard.py | 3030 | 5B19A0CBBF78555EFF0F2CC96F8FD21867A2BFC2212A830E319678A7FFF08C18 |
| .\sigma\protocols.py | 2194 | 9FD36D072C4E3DEC3A500D52E67DDC5AF011D16DB92AFFE3871523CCD70204DF |
| .\sigma\run_pipeline.py | 4400 | 3415EF9B448B83E73BFF4E298D7D9BD44C2B903A1C6A8B2F2A4013076E54C540 |
| .\sigma\registry.py | 450 | AC46F0FDA906EEB289C8C1007FAA6B0C0DAD59DD071D465A2BFE3E73A431E510 |
| .\sigma\obsidia_sigma_v130.py | 11294 | 5D6E71983F3974DB4853ECE436126FF7B4511524EF69535D2B3668521AD0B314 |
| .\audit_merkle.py | 2147 | C84D014DEE0A8DF44035A17619EF35A122085D2C0796FFE8E70A89E5091CF481 |
| .\merkle_seal.json | 318 | C0BAF87761049368442F8427BABDACD89047E6F0AE4076D2163EB69684A04016 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 10. Index fichiers produits

| Fichier | KB | SHA12 | LastWrite |
| --- | --- | --- | --- |
| ALL_METRIC_CATEGORIES.csv | 2.68 | 341AE4D7F898 | 04/29/2026 21:56:45 |
| ALL_METRICS_FLAT.csv | 24.53 | 22688F834758 | 04/29/2026 21:56:45 |
| ARTIFACT_HASH_MANIFEST.csv | 2.3 | 8929C5E013DC | 04/29/2026 21:56:46 |
| audit_decision_summary.csv | 4.67 | 20C24E73134A | 04/29/2026 21:56:45 |
| audit_decision_summary.json | 6.08 | B3E984E6E967 | 04/29/2026 21:56:45 |
| AUDIT_ROOT_SHA256.txt | 0.07 | A064E14B73A5 | 04/29/2026 21:56:46 |
| decision_runtime_metrics_flat.csv | 620.11 | 634C510EC7F1 | 04/29/2026 21:56:45 |
| decisions_after.csv | 2683 | A91A1F31B423 | 04/29/2026 21:56:43 |
| decisions_before.csv | 2672.06 | 4FB986D0878F | 04/29/2026 21:55:40 |
| decisions_created_during_audit.csv | 10.07 | 150F126D9A3F | 04/29/2026 21:56:43 |
| EVIDENCE_BOARD_3_DOMAINES.md | 14.13 | CD05D427F392 | 04/29/2026 21:56:46 |
| input_bank.json | 0.47 | 988680FD35AD | 04/29/2026 21:55:49 |
| input_gps_defense_aviation.json | 0.33 | 0E9835CD2BEB | 04/29/2026 21:55:50 |
| input_trading.json | 0.26 | A09D6DEE2AD5 | 04/29/2026 21:55:50 |
| merkle_seal_after.json | 0.31 | C0BAF8776104 | 04/29/2026 21:55:49 |
| merkle_seal_before.json | 0.31 | 8FBECF80DBD2 | 04/29/2026 21:53:56 |
| metrics_categories_bank.csv | 0.78 | 7F3C0481BDE9 | 04/29/2026 21:55:50 |
| metrics_categories_gps_defense_aviation.csv | 1.17 | 92785B5DFA62 | 04/29/2026 21:55:51 |
| metrics_categories_trading.csv | 0.8 | 0DE9AC4F4E24 | 04/29/2026 21:55:50 |
| metrics_full_bank.csv | 7.93 | 906453CB4FD3 | 04/29/2026 21:55:50 |
| metrics_full_bank.json | 20.37 | 10ADA8F8C515 | 04/29/2026 21:55:50 |
| metrics_full_gps_defense_aviation.csv | 8.73 | 091229A99C7E | 04/29/2026 21:55:51 |
| metrics_full_gps_defense_aviation.json | 20.16 | E43C3BE260D5 | 04/29/2026 21:55:51 |
| metrics_full_trading.csv | 7.96 | 9F30DD34E5DE | 04/29/2026 21:55:50 |
| metrics_full_trading.json | 20.07 | F6696E14350F | 04/29/2026 21:55:50 |
| PROOF_CLAIMS_MATRIX.csv | 1.19 | 0B4A113E9698 | 04/29/2026 21:56:46 |
| REPORT_SHA256.txt | 0.07 | 9728AA3D88AE | 04/29/2026 21:56:46 |
| response_bank.json | 6.8 | D157D5FBC3E9 | 04/29/2026 21:55:50 |
| response_gps_defense_aviation.json | 6.19 | 73BD31468C4D | 04/29/2026 21:55:51 |
| response_trading.json | 6.55 | A4FAB62D399A | 04/29/2026 21:55:50 |
| runtime_file_hashes.csv | 1.31 | CA7BB3B09CFA | 04/29/2026 21:56:45 |
| server.stderr.log | 4.21 | 6C4A2621FBAB | 04/29/2026 21:55:51 |
| server.stdout.log | 0.93 | DBE4436CA6DD | 04/29/2026 21:55:51 |
| TRACE_CHAINS_BY_DOMAIN.csv | 5.35 | FA91DBCFA187 | 04/29/2026 21:56:45 |
| TRACE_MANIFEST.json | 59.88 | C12AD7FEB84C | 04/29/2026 21:56:45 |
| TRACE_STATS.json | 1.01 | 0ED59E1ACD66 | 04/29/2026 21:56:45 |
