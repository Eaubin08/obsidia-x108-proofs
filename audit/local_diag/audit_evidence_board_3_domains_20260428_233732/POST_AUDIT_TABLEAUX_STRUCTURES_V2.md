# Post-audit structure V2 - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260428_233732
Date lecture : 2026-04-29 00:48:58

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
| bank | 988680FD35AD | 255A3225E2F6 | C791C23AF0EB | 111 | 5 | 7FE4F8770376 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading | A09D6DEE2AD5 | 360032506A16 | 8627C56A29A0 | 108 | 14 | 8FC122E711B3 | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation | 0E9835CD2BEB | 4A18D4FB0371 | 1F5A47612074 | 102 | 9 | 2D1D218981A1 | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 2929 | decision_runtime_metrics_flat.csv | Donnees extraites des decisions runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 28 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
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
| Tracabilite decisions | 28 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=968204A0365324E50E62C8FFF11E2E78EFC1222C60D40670439F75C53FD0A8CA | OK |
| Racine audit | AUDIT_ROOT_SHA256=96cc8f6648e4554a04729c4c04a4306e4bc35d235a09a88092847174b7396e69 | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 7. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542 | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | 968204A0365324E50E62C8FFF11E2E78EFC1222C60D40670439F75C53FD0A8CA | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | 96cc8f6648e4554a04729c4c04a4306e4bc35d235a09a88092847174b7396e69 | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | 62D75BEA7D573381D6310B9047C0AEB4AF5B80217B471C9672807FD519A4C6A9 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | F98708FD4217B3463F3CA7C74A857C10028614EB702B64A2A14EAA53AA33278D | server.stdout.log |
| SERVER_STDERR_SHA256 | FAC2CD72F1F74E85A80697AA83DFDF5D6954089435521583704DA5B95C6BAF84 | server.stderr.log |

## 8. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777412259624.json | 3468 |  |  |
| decision_bank_1777412269980.json | 3468 |  |  |
| decision_bank_1777412280268.json | 3468 |  |  |
| decision_bank_1777412290724.json | 3468 |  |  |
| decision_bank_1777412290904.json | 3720 |  |  |
| decision_gps_defense_aviation_1777412257489.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412261828.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412266181.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412270600.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412275006.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412279255.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412283512.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412288843.json | 3349 |  |  |
| decision_gps_defense_aviation_1777412291900.json | 3448 |  |  |
| decision_trading_1777412254119.json | 3520 |  |  |
| decision_trading_1777412256937.json | 3520 |  |  |
| decision_trading_1777412259565.json | 3520 |  |  |
| decision_trading_1777412262211.json | 3520 |  |  |
| decision_trading_1777412264956.json | 3520 |  |  |
| decision_trading_1777412267529.json | 3520 |  |  |
| decision_trading_1777412270219.json | 3520 |  |  |
| decision_trading_1777412273011.json | 3520 |  |  |
| decision_trading_1777412275623.json | 3520 |  |  |
| decision_trading_1777412278819.json | 3520 |  |  |
| decision_trading_1777412281586.json | 3520 |  |  |
| decision_trading_1777412284291.json | 3520 |  |  |
| decision_trading_1777412291542.json | 3461 |  |  |
| decision_trading_1777412292248.json | 3520 |  |  |

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
| .\merkle_seal.json | 317 | E264FA8A8D42E5A6F8070BBF79120BCF61CC9236DCFA397BE0962C0420BA4542 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 10. Index fichiers produits

| Fichier | KB | SHA12 | LastWrite |
| --- | --- | --- | --- |
| ALL_METRIC_CATEGORIES.csv | 2.68 | 341AE4D7F898 | 04/28/2026 23:38:50 |
| ALL_METRICS_FLAT.csv | 24.53 | 6FD72B4E3C07 | 04/28/2026 23:38:50 |
| ARTIFACT_HASH_MANIFEST.csv | 2.3 | 931990BB4628 | 04/28/2026 23:38:51 |
| audit_decision_summary.csv | 4.67 | FE504CFA788D | 04/28/2026 23:38:51 |
| audit_decision_summary.json | 6.08 | 890456C4DDD4 | 04/28/2026 23:38:51 |
| AUDIT_ROOT_SHA256.txt | 0.07 | EA7573C96843 | 04/28/2026 23:38:51 |
| decision_runtime_metrics_flat.csv | 413.15 | D9B6A1481277 | 04/28/2026 23:38:50 |
| decisions_after.csv | 2032.78 | E52F1AC63E06 | 04/28/2026 23:38:49 |
| decisions_before.csv | 2025.5 | C65EA052397B | 04/28/2026 23:38:03 |
| decisions_created_during_audit.csv | 6.72 | 7A25AECBCA2A | 04/28/2026 23:38:49 |
| EVIDENCE_BOARD_3_DOMAINES.md | 12.96 | 62D75BEA7D57 | 04/28/2026 23:38:51 |
| input_bank.json | 0.47 | 988680FD35AD | 04/28/2026 23:38:10 |
| input_gps_defense_aviation.json | 0.33 | 0E9835CD2BEB | 04/28/2026 23:38:11 |
| input_trading.json | 0.26 | A09D6DEE2AD5 | 04/28/2026 23:38:11 |
| merkle_seal_after.json | 0.31 | E264FA8A8D42 | 04/28/2026 23:37:21 |
| merkle_seal_before.json | 0.31 | E264FA8A8D42 | 04/28/2026 23:37:21 |
| metrics_categories_bank.csv | 0.78 | 7F3C0481BDE9 | 04/28/2026 23:38:11 |
| metrics_categories_gps_defense_aviation.csv | 1.17 | 92785B5DFA62 | 04/28/2026 23:38:11 |
| metrics_categories_trading.csv | 0.8 | 0DE9AC4F4E24 | 04/28/2026 23:38:11 |
| metrics_full_bank.csv | 7.93 | C791C23AF0EB | 04/28/2026 23:38:11 |
| metrics_full_bank.json | 20.37 | 4ED0415DAC27 | 04/28/2026 23:38:11 |
| metrics_full_gps_defense_aviation.csv | 8.73 | 1F5A47612074 | 04/28/2026 23:38:11 |
| metrics_full_gps_defense_aviation.json | 20.16 | D9204FFA716D | 04/28/2026 23:38:11 |
| metrics_full_trading.csv | 7.96 | 8627C56A29A0 | 04/28/2026 23:38:11 |
| metrics_full_trading.json | 20.07 | 48AB4AE1DCAD | 04/28/2026 23:38:11 |
| PROOF_CLAIMS_MATRIX.csv | 1.19 | 7DE2C27EDC76 | 04/28/2026 23:38:51 |
| REPORT_SHA256.txt | 0.07 | BCFD5F398120 | 04/28/2026 23:38:51 |
| response_bank.json | 6.8 | 255A3225E2F6 | 04/28/2026 23:38:10 |
| response_gps_defense_aviation.json | 6.19 | 4A18D4FB0371 | 04/28/2026 23:38:11 |
| response_trading.json | 6.55 | 360032506A16 | 04/28/2026 23:38:11 |
| runtime_file_hashes.csv | 1.31 | F8A8E4D23E91 | 04/28/2026 23:38:50 |
| server.stderr.log | 4.04 | FAC2CD72F1F7 | 04/28/2026 23:38:12 |
| server.stdout.log | 0.93 | F98708FD4217 | 04/28/2026 23:38:12 |
| TRACE_CHAINS_BY_DOMAIN.csv | 3.89 | 66A0A8B44AF1 | 04/28/2026 23:38:51 |
| TRACE_MANIFEST.json | 51.52 | 968204A03653 | 04/28/2026 23:38:51 |
| TRACE_STATS.json | 1.01 | 555CC0F1ECE0 | 04/28/2026 23:38:51 |
