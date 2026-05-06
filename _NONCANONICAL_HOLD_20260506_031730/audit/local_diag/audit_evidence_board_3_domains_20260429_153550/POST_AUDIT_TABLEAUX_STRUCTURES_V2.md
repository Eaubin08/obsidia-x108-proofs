# Post-audit structure V2 - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260429_153550
Date lecture : 2026-04-29 15:37:15

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
| bank | 988680FD35AD | 3F5BF5A58D6D | 2E0F3001CD64 | 111 | 6 | FE750BBCD022 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading | A09D6DEE2AD5 | 717F72699F46 | 9F8C712477A8 | 108 | 13 | 09DE50B637FC | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | 0E9835CD2BEB | 95B65E9635BB | 9CEE4B2E72B5 | 102 | 10 | 25FDAA05F1D2 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 3023 | decision_runtime_metrics_flat.csv | Donnees extraites des decisions runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 29 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
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
| Tracabilite decisions | 29 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=E8BCC7A472CE39D6CAFD76FF719A48A48A845EE3D7C700D127D9D522CA69F4C1 | OK |
| Racine audit | AUDIT_ROOT_SHA256=802fcd3d7e56e257e9ada83de883cccd19e5488acccccc917efcb6846d41f916 | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 7. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | 238828A3E15E8F114308CFFC80F87C641A97F187E02199F5F435C565982BA1EE | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | D1C718EB73695934CFFCA9AA3F89C6639057273C1708D4A2C4C5E19F4E4600D0 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | E8BCC7A472CE39D6CAFD76FF719A48A48A845EE3D7C700D127D9D522CA69F4C1 | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | 802fcd3d7e56e257e9ada83de883cccd19e5488acccccc917efcb6846d41f916 | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | DD754ABB67EB67BD5723802A82DF797A43FF8895551E3BE8594CB7FA1DA80702 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | 114B6C4E2FCA01FC6D273E7794350281E90938558A93B4C48528DAF0943EA25D | server.stdout.log |
| SERVER_STDERR_SHA256 | 0166E257B5E6C83F3B748A5756566E48B23CFA02CB381330B461D1F9EEFB7E95 | server.stderr.log |

## 8. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777469753236.json | 3468 |  |  |
| decision_bank_1777469763706.json | 3468 |  |  |
| decision_bank_1777469774474.json | 3468 |  |  |
| decision_bank_1777469784829.json | 3468 |  |  |
| decision_bank_1777469793586.json | 3720 |  |  |
| decision_bank_1777469795260.json | 3468 |  |  |
| decision_gps_defense_aviation_1777469754510.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469758836.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469763292.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469767741.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469772199.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469777058.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469781451.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469785768.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469792317.json | 3349 |  |  |
| decision_gps_defense_aviation_1777469795165.json | 3448 |  |  |
| decision_trading_1777469754705.json | 3520 |  |  |
| decision_trading_1777469757935.json | 3520 |  |  |
| decision_trading_1777469760987.json | 3520 |  |  |
| decision_trading_1777469764324.json | 3520 |  |  |
| decision_trading_1777469767583.json | 3520 |  |  |
| decision_trading_1777469770507.json | 3520 |  |  |
| decision_trading_1777469773288.json | 3520 |  |  |
| decision_trading_1777469776725.json | 3520 |  |  |
| decision_trading_1777469779826.json | 3520 |  |  |
| decision_trading_1777469783193.json | 3520 |  |  |
| decision_trading_1777469786372.json | 3520 |  |  |
| decision_trading_1777469794571.json | 3461 |  |  |
| decision_trading_1777469794919.json | 3520 |  |  |

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
| .\merkle_seal.json | 317 | D1C718EB73695934CFFCA9AA3F89C6639057273C1708D4A2C4C5E19F4E4600D0 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 10. Index fichiers produits

| Fichier | KB | SHA12 | LastWrite |
| --- | --- | --- | --- |
| ALL_METRIC_CATEGORIES.csv | 2.68 | 341AE4D7F898 | 04/29/2026 15:37:10 |
| ALL_METRICS_FLAT.csv | 24.53 | AA7BEB5A23EC | 04/29/2026 15:37:10 |
| ARTIFACT_HASH_MANIFEST.csv | 2.3 | AC045C42E6E2 | 04/29/2026 15:37:10 |
| audit_decision_summary.csv | 4.67 | DE6A28E7B284 | 04/29/2026 15:37:10 |
| audit_decision_summary.json | 6.08 | FD82A14E8BA3 | 04/29/2026 15:37:10 |
| AUDIT_ROOT_SHA256.txt | 0.07 | 39BD7B436CBD | 04/29/2026 15:37:10 |
| decision_runtime_metrics_flat.csv | 427.56 | 39FA81285486 | 04/29/2026 15:37:09 |
| decisions_after.csv | 2141.05 | FAAAABEEB08C | 04/29/2026 15:37:08 |
| decisions_before.csv | 2133.5 | E18FC8D00755 | 04/29/2026 15:36:25 |
| decisions_created_during_audit.csv | 6.97 | A92594D3B8A7 | 04/29/2026 15:37:08 |
| EVIDENCE_BOARD_3_DOMAINES.md | 13.05 | DD754ABB67EB | 04/29/2026 15:37:11 |
| input_bank.json | 0.47 | 988680FD35AD | 04/29/2026 15:36:33 |
| input_gps_defense_aviation.json | 0.33 | 0E9835CD2BEB | 04/29/2026 15:36:34 |
| input_trading.json | 0.26 | A09D6DEE2AD5 | 04/29/2026 15:36:34 |
| merkle_seal_after.json | 0.31 | D1C718EB7369 | 04/29/2026 15:36:15 |
| merkle_seal_before.json | 0.31 | 238828A3E15E | 04/29/2026 15:35:16 |
| metrics_categories_bank.csv | 0.78 | 7F3C0481BDE9 | 04/29/2026 15:36:33 |
| metrics_categories_gps_defense_aviation.csv | 1.17 | 92785B5DFA62 | 04/29/2026 15:36:35 |
| metrics_categories_trading.csv | 0.8 | 0DE9AC4F4E24 | 04/29/2026 15:36:34 |
| metrics_full_bank.csv | 7.93 | 2E0F3001CD64 | 04/29/2026 15:36:33 |
| metrics_full_bank.json | 20.37 | 57BD1E253A9A | 04/29/2026 15:36:33 |
| metrics_full_gps_defense_aviation.csv | 8.73 | 9CEE4B2E72B5 | 04/29/2026 15:36:35 |
| metrics_full_gps_defense_aviation.json | 20.16 | E0EABE4D1830 | 04/29/2026 15:36:35 |
| metrics_full_trading.csv | 7.96 | 9F8C712477A8 | 04/29/2026 15:36:34 |
| metrics_full_trading.json | 20.07 | BE55BBC859D4 | 04/29/2026 15:36:34 |
| PROOF_CLAIMS_MATRIX.csv | 1.19 | 37BA3508D9F4 | 04/29/2026 15:37:10 |
| REPORT_SHA256.txt | 0.07 | C196D363C1AD | 04/29/2026 15:37:11 |
| response_bank.json | 6.8 | 3F5BF5A58D6D | 04/29/2026 15:36:33 |
| response_gps_defense_aviation.json | 6.19 | 95B65E9635BB | 04/29/2026 15:36:35 |
| response_trading.json | 6.55 | 717F72699F46 | 04/29/2026 15:36:34 |
| runtime_file_hashes.csv | 1.31 | 16AA5D044A1C | 04/29/2026 15:37:10 |
| server.stderr.log | 4.41 | 0166E257B5E6 | 04/29/2026 15:36:35 |
| server.stdout.log | 0.93 | 114B6C4E2FCA | 04/29/2026 15:36:35 |
| TRACE_CHAINS_BY_DOMAIN.csv | 4 | D0601CA07675 | 04/29/2026 15:37:10 |
| TRACE_MANIFEST.json | 52.13 | E8BCC7A472CE | 04/29/2026 15:37:10 |
| TRACE_STATS.json | 1.01 | 3A923D14EFF9 | 04/29/2026 15:37:10 |
