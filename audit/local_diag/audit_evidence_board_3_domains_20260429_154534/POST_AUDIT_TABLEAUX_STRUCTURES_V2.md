# Post-audit structure V2 - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260429_154534
Date lecture : 2026-04-29 15:47:22

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
| bank | 988680FD35AD | 128380709C77 | 28F472CF8A67 | 111 | 7 | 477896BD4420 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading | A09D6DEE2AD5 | 6FEDD66FCD5B | 78DA1F1A2234 | 108 | 20 | 32BDF6FA2AEE | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | 0E9835CD2BEB | DC1C168712D2 | 2815F96A255D | 102 | 14 | 042678A0E83A | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 4278 | decision_runtime_metrics_flat.csv | Donnees extraites des decisions runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 41 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
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
| Tracabilite decisions | 41 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=D1E3534711C0704AC270E7ACECBB022D21EAAA00FB9A8FB9F1B5509BE0092283 | OK |
| Racine audit | AUDIT_ROOT_SHA256=4502fa58bea3829b8c19d0daa00da904b5f4227e7022af8613eae3fa0391310e | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 7. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | F24ED74FD5E7B756395F9F63F104A19C18DB58C8411FD823B1ABF9254B0055F7 | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | 90E1414A8750DD969B0DECDBE01AB81584E702838484FF1D8EE7271BF657F6E2 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | D1E3534711C0704AC270E7ACECBB022D21EAAA00FB9A8FB9F1B5509BE0092283 | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | 4502fa58bea3829b8c19d0daa00da904b5f4227e7022af8613eae3fa0391310e | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | E92D8A3F9C80A563EF6C7F4A9297FBAD95D9753C5951868F7BA0042717E8D3E7 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | 9B71A764857C05AC52036549B6424A9D1E0904C5F5AD6A542D957DA6E533450D | server.stdout.log |
| SERVER_STDERR_SHA256 | EB2A1134376CA1462B0B88AAB838A09FCA6D5A7DE132CBB554E717410630D45A | server.stderr.log |

## 8. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777470339830.json | 3468 |  |  |
| decision_bank_1777470350459.json | 3468 |  |  |
| decision_bank_1777470361604.json | 3468 |  |  |
| decision_bank_1777470372238.json | 3468 |  |  |
| decision_bank_1777470382835.json | 3468 |  |  |
| decision_bank_1777470393240.json | 3468 |  |  |
| decision_bank_1777470398736.json | 3720 |  |  |
| decision_gps_defense_aviation_1777470340099.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470344664.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470349274.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470354191.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470358662.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470362984.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470367438.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470372043.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470377082.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470381650.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470388742.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470393147.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470398235.json | 3349 |  |  |
| decision_gps_defense_aviation_1777470400242.json | 3448 |  |  |
| decision_trading_1777470337899.json | 3520 |  |  |
| decision_trading_1777470341020.json | 3520 |  |  |
| decision_trading_1777470344369.json | 3520 |  |  |
| decision_trading_1777470348377.json | 3520 |  |  |
| decision_trading_1777470351569.json | 3520 |  |  |
| decision_trading_1777470356135.json | 3520 |  |  |
| decision_trading_1777470359157.json | 3520 |  |  |
| decision_trading_1777470362199.json | 3520 |  |  |
| decision_trading_1777470365496.json | 3520 |  |  |
| decision_trading_1777470369004.json | 3520 |  |  |
| decision_trading_1777470372202.json | 3520 |  |  |
| decision_trading_1777470375213.json | 3520 |  |  |
| decision_trading_1777470378235.json | 3520 |  |  |
| decision_trading_1777470381503.json | 3520 |  |  |
| decision_trading_1777470384373.json | 3520 |  |  |
| decision_trading_1777470389326.json | 3520 |  |  |
| decision_trading_1777470392714.json | 3520 |  |  |
| decision_trading_1777470397776.json | 3520 |  |  |
| decision_trading_1777470399702.json | 3461 |  |  |
| decision_trading_1777470400885.json | 3520 |  |  |

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
| .\merkle_seal.json | 317 | 90E1414A8750DD969B0DECDBE01AB81584E702838484FF1D8EE7271BF657F6E2 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 10. Index fichiers produits

| Fichier | KB | SHA12 | LastWrite |
| --- | --- | --- | --- |
| ALL_METRIC_CATEGORIES.csv | 2.68 | 341AE4D7F898 | 04/29/2026 15:47:19 |
| ALL_METRICS_FLAT.csv | 24.53 | 78DA71B15908 | 04/29/2026 15:47:19 |
| ARTIFACT_HASH_MANIFEST.csv | 2.3 | 79F6124D83D3 | 04/29/2026 15:47:19 |
| audit_decision_summary.csv | 4.67 | 4F4411AB8198 | 04/29/2026 15:47:19 |
| audit_decision_summary.json | 6.08 | 7ADF770CE3FB | 04/29/2026 15:47:19 |
| AUDIT_ROOT_SHA256.txt | 0.07 | CBC224D68E10 | 04/29/2026 15:47:19 |
| decision_runtime_metrics_flat.csv | 605.54 | 89D735485953 | 04/29/2026 15:47:19 |
| decisions_after.csv | 2199.21 | 51D2F44D4A9B | 04/29/2026 15:47:16 |
| decisions_before.csv | 2188.53 | 2FE15169D7AA | 04/29/2026 15:46:22 |
| decisions_created_during_audit.csv | 9.84 | 3A4F6800D717 | 04/29/2026 15:47:17 |
| EVIDENCE_BOARD_3_DOMAINES.md | 14.05 | E92D8A3F9C80 | 04/29/2026 15:47:19 |
| input_bank.json | 0.47 | 988680FD35AD | 04/29/2026 15:46:37 |
| input_gps_defense_aviation.json | 0.33 | 0E9835CD2BEB | 04/29/2026 15:46:39 |
| input_trading.json | 0.26 | A09D6DEE2AD5 | 04/29/2026 15:46:39 |
| merkle_seal_after.json | 0.31 | 90E1414A8750 | 04/29/2026 15:45:53 |
| merkle_seal_before.json | 0.31 | F24ED74FD5E7 | 04/29/2026 15:44:51 |
| metrics_categories_bank.csv | 0.78 | 7F3C0481BDE9 | 04/29/2026 15:46:39 |
| metrics_categories_gps_defense_aviation.csv | 1.17 | 92785B5DFA62 | 04/29/2026 15:46:40 |
| metrics_categories_trading.csv | 0.8 | 0DE9AC4F4E24 | 04/29/2026 15:46:39 |
| metrics_full_bank.csv | 7.93 | 28F472CF8A67 | 04/29/2026 15:46:39 |
| metrics_full_bank.json | 20.37 | 14298977F218 | 04/29/2026 15:46:39 |
| metrics_full_gps_defense_aviation.csv | 8.73 | 2815F96A255D | 04/29/2026 15:46:40 |
| metrics_full_gps_defense_aviation.json | 20.16 | 8BB52007EBC3 | 04/29/2026 15:46:40 |
| metrics_full_trading.csv | 7.96 | 78DA1F1A2234 | 04/29/2026 15:46:39 |
| metrics_full_trading.json | 20.07 | EFEBA93B696B | 04/29/2026 15:46:39 |
| PROOF_CLAIMS_MATRIX.csv | 1.19 | 62277BCB8B72 | 04/29/2026 15:47:19 |
| REPORT_SHA256.txt | 0.07 | DB50DE4FD816 | 04/29/2026 15:47:19 |
| response_bank.json | 6.8 | 128380709C77 | 04/29/2026 15:46:38 |
| response_gps_defense_aviation.json | 6.19 | DC1C168712D2 | 04/29/2026 15:46:40 |
| response_trading.json | 6.55 | 6FEDD66FCD5B | 04/29/2026 15:46:39 |
| runtime_file_hashes.csv | 1.31 | FECBEBBB9946 | 04/29/2026 15:47:19 |
| server.stderr.log | 4.44 | EB2A1134376C | 04/29/2026 15:46:40 |
| server.stdout.log | 0.93 | 9B71A764857C | 04/29/2026 15:46:40 |
| TRACE_CHAINS_BY_DOMAIN.csv | 5.25 | EA97A53090D2 | 04/29/2026 15:47:19 |
| TRACE_MANIFEST.json | 59.3 | D1E3534711C0 | 04/29/2026 15:47:19 |
| TRACE_STATS.json | 1.01 | C427FFB39617 | 04/29/2026 15:47:19 |
