# Post-audit structure V2 - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260429_155300
Date lecture : 2026-04-29 21:54:33

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
| bank | 988680FD35AD | 9E5E66660599 | E830BFCA2EB4 | 111 | 6 | F4E7159EC996 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading | A09D6DEE2AD5 | 4AF6FFA12D70 | 0FEC938933C0 | 108 | 19 | 3959DDB8EE43 | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | 0E9835CD2BEB | 133B8B181B9E | AB66C0B57AEA | 102 | 13 | B89BDCF66027 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 3968 | decision_runtime_metrics_flat.csv | Donnees extraites des decisions runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 38 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
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
| Tracabilite decisions | 38 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=9EF88D52FACC0884AC3618C91E241631A2C3A08580CF2A1871D8FE88020F7C60 | OK |
| Racine audit | AUDIT_ROOT_SHA256=cf775295451df9588808cc0595d0202eb81e1ccecb8593aff049b6986f623c9c | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 7. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | F29B64CE40ACB6E03294F5A9C679BEB12911AB3F5EF197645F7D4D2971EEAC59 | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | AE7759DB46DF38C98A8B798C2320BE8190327F557A388E127F5176CE368D3EA9 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | 9EF88D52FACC0884AC3618C91E241631A2C3A08580CF2A1871D8FE88020F7C60 | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | cf775295451df9588808cc0595d0202eb81e1ccecb8593aff049b6986f623c9c | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | 7DD128AD89E72B193C7BF5B59AA04BCD3E62C4D5DA00E3D93E580EC197D11212 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | 8BF4E27ECCB7E8436EC7B8C80F33ADE198ACD8678CF6EFBC81625BEE1645483F | server.stdout.log |
| SERVER_STDERR_SHA256 | EEC9CA7AA1F6CC896972506462E401EFA97BFD69380121CFECF726CB39225D3D | server.stderr.log |

## 8. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777470790884.json | 3468 |  |  |
| decision_bank_1777470801464.json | 3468 |  |  |
| decision_bank_1777470811801.json | 3468 |  |  |
| decision_bank_1777470822298.json | 3468 |  |  |
| decision_bank_1777470834231.json | 3468 |  |  |
| decision_bank_1777470836201.json | 3720 |  |  |
| decision_gps_defense_aviation_1777470782756.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470787194.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470791648.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470796192.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470800728.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470805451.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470809859.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470814253.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470818705.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470823232.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470827734.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470834659.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470837539.json | 3448 |  |  |
| decision_trading_1777470783587.json | 3520 |  |  |
| decision_trading_1777470786664.json | 3520 |  |  |
| decision_trading_1777470789545.json | 3520 |  |  |
| decision_trading_1777470792665.json | 3520 |  |  |
| decision_trading_1777470796017.json | 3520 |  |  |
| decision_trading_1777470799095.json | 3520 |  |  |
| decision_trading_1777470802126.json | 3520 |  |  |
| decision_trading_1777470805458.json | 3520 |  |  |
| decision_trading_1777470808515.json | 3520 |  |  |
| decision_trading_1777470811314.json | 3520 |  |  |
| decision_trading_1777470814335.json | 3520 |  |  |
| decision_trading_1777470817240.json | 3520 |  |  |
| decision_trading_1777470820283.json | 3520 |  |  |
| decision_trading_1777470823212.json | 3520 |  |  |
| decision_trading_1777470826597.json | 3520 |  |  |
| decision_trading_1777470829761.json | 3520 |  |  |
| decision_trading_1777470834481.json | 3520 |  |  |
| decision_trading_1777470837170.json | 3461 |  |  |
| decision_trading_1777470837444.json | 3520 |  |  |

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
| .\merkle_seal.json | 317 | AE7759DB46DF38C98A8B798C2320BE8190327F557A388E127F5176CE368D3EA9 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 10. Index fichiers produits

| Fichier | KB | SHA12 | LastWrite |
| --- | --- | --- | --- |
| ALL_METRIC_CATEGORIES.csv | 2.68 | 341AE4D7F898 | 04/29/2026 15:54:30 |
| ALL_METRICS_FLAT.csv | 24.53 | 216EDFA48418 | 04/29/2026 15:54:30 |
| ARTIFACT_HASH_MANIFEST.csv | 2.3 | 1DC509E379FB | 04/29/2026 15:54:31 |
| audit_decision_summary.csv | 4.67 | 417FE5C5951A | 04/29/2026 15:54:31 |
| audit_decision_summary.json | 6.08 | 698F2B1AD901 | 04/29/2026 15:54:31 |
| AUDIT_ROOT_SHA256.txt | 0.07 | 201D0FFDE6B6 | 04/29/2026 15:54:31 |
| decision_runtime_metrics_flat.csv | 561.98 | 3A0898232043 | 04/29/2026 15:54:30 |
| decisions_after.csv | 2260.75 | F27780431D99 | 04/29/2026 15:54:30 |
| decisions_before.csv | 2250.85 | A9B73B207432 | 04/29/2026 15:53:48 |
| decisions_created_during_audit.csv | 9.13 | 0EBB67BC1A5C | 04/29/2026 15:54:30 |
| EVIDENCE_BOARD_3_DOMAINES.md | 13.81 | 7DD128AD89E7 | 04/29/2026 15:54:31 |
| input_bank.json | 0.47 | 988680FD35AD | 04/29/2026 15:53:55 |
| input_gps_defense_aviation.json | 0.33 | 0E9835CD2BEB | 04/29/2026 15:53:57 |
| input_trading.json | 0.26 | A09D6DEE2AD5 | 04/29/2026 15:53:56 |
| merkle_seal_after.json | 0.31 | AE7759DB46DF | 04/29/2026 15:53:02 |
| merkle_seal_before.json | 0.31 | F29B64CE40AC | 04/29/2026 15:52:02 |
| metrics_categories_bank.csv | 0.78 | 7F3C0481BDE9 | 04/29/2026 15:53:56 |
| metrics_categories_gps_defense_aviation.csv | 1.17 | 92785B5DFA62 | 04/29/2026 15:53:57 |
| metrics_categories_trading.csv | 0.8 | 0DE9AC4F4E24 | 04/29/2026 15:53:57 |
| metrics_full_bank.csv | 7.93 | E830BFCA2EB4 | 04/29/2026 15:53:56 |
| metrics_full_bank.json | 20.37 | 8A3DCD87C2CC | 04/29/2026 15:53:56 |
| metrics_full_gps_defense_aviation.csv | 8.73 | AB66C0B57AEA | 04/29/2026 15:53:57 |
| metrics_full_gps_defense_aviation.json | 20.16 | D0AA1DFAE3AB | 04/29/2026 15:53:57 |
| metrics_full_trading.csv | 7.96 | 0FEC938933C0 | 04/29/2026 15:53:57 |
| metrics_full_trading.json | 20.07 | 0F683953DF31 | 04/29/2026 15:53:57 |
| POST_AUDIT_TABLEAUX_STRUCTURES_V2.md | 13.89 | 14B28BA2522B | 04/29/2026 21:54:20 |
| PROOF_CLAIMS_MATRIX.csv | 1.19 | 5A120FEEA47B | 04/29/2026 15:54:31 |
| REPORT_SHA256.txt | 0.07 | 07FD34D46F46 | 04/29/2026 15:54:31 |
| response_bank.json | 6.8 | 9E5E66660599 | 04/29/2026 15:53:56 |
| response_gps_defense_aviation.json | 6.19 | 133B8B181B9E | 04/29/2026 15:53:57 |
| response_trading.json | 6.55 | 4AF6FFA12D70 | 04/29/2026 15:53:57 |
| runtime_file_hashes.csv | 1.31 | C8FCC0B40BB8 | 04/29/2026 15:54:30 |
| server.stderr.log | 4.79 | EEC9CA7AA1F6 | 04/29/2026 15:53:57 |
| server.stdout.log | 1.07 | 8BF4E27ECCB7 | 04/29/2026 15:53:57 |
| TRACE_CHAINS_BY_DOMAIN.csv | 4.94 | 05F81FCEC1EE | 04/29/2026 15:54:31 |
| TRACE_MANIFEST.json | 57.51 | 9EF88D52FACC | 04/29/2026 15:54:31 |
| TRACE_STATS.json | 1.01 | 1FED9E64703D | 04/29/2026 15:54:31 |
