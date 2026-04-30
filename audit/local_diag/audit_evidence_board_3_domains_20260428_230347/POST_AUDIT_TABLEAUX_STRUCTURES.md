# Post-audit structure - Evidence Board 3 domaines

Audit source : C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\audit\local_diag\audit_evidence_board_3_domains_20260428_230347
Date lecture : 2026-04-28 23:31:58

## 1. Lecture executive

Cet audit demontre une chaine complete : payload domaine -> endpoint Node -> pipeline Sigma/Python -> verdict metier -> gate X-108 -> decision runtime -> fichiers traces -> hashes -> manifest -> racine audit.

## 2. Tableau decisionnel

| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | MetricCount | Lecture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bank | ANALYZE | BLOCK | 0,5 | 0,95 | 0,66 | 0,7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 111 | REFUS AVANT ACTION |
| trading | REVIEW | HOLD | 0,5 | 0,75 | 0,6 | 0,6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 108 | TEMPORISATION X-108 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0,35 | 0,95 | 0,51 | 0,6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 102 | REFUS AVANT ACTION |

## 3. Chaine de trace par domaine

| Domaine | InputSHA | ResponseSHA | MetricsSHA | MetricCount | DecisionCount | DecisionSHA | Gate | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bank |  |  |  | 111 | 1 | 1406AFE116EC | BLOCK | CONTRADICTION_THRESHOLD_REACHED |
| trading |  |  |  | 108 | 1 | EE188F39B94D | HOLD | RISK_FLAGS_REQUIRE_DELAY |
| gps_defense_aviation |  |  |  | 102 | 1 | 71BA837BEEDD | BLOCK | CONTRADICTION_THRESHOLD_REACHED |

## 4. Ce qui est compte

| Bloc | Nombre | Fichier | Sens |
| --- | --- | --- | --- |
| Domaines testes | 3 | audit_decision_summary.csv | Nombre de domaines passes dans le moteur |
| Metriques flattenees | 321 | ALL_METRICS_FLAT.csv | Toutes les donnees retournees par le moteur mises a plat |
| Metriques runtime decisions | 321 | decision_runtime_metrics_flat.csv | Donnees extraites des decision runtime |
| Categories metriques | 81 | ALL_METRIC_CATEGORIES.csv | Regroupement des metriques par familles |
| Decisions creees | 3 | decisions_created_during_audit.csv | Nouveaux fichiers decision JSON produits pendant audit |
| Fichiers runtime hashes | 13 | runtime_file_hashes.csv | Fichiers moteur critiques hashes |
| Claims preuve | 16 | PROOF_CLAIMS_MATRIX.csv | Axes de preuve declares OK |

## 5. Compteurs de tracabilite

| Cle | Valeur |
| --- | --- |
| domains_tested | 3 |
| total_response_metrics | 321 |
| total_decision_runtime_metrics | 321 |
| input_files_generated | 3 |
| response_files_generated | 3 |
| metrics_files_generated | 3 |
| decisions_before | 7237 |
| decisions_after | 7240 |
| decisions_created_during_audit | 3 |
| runtime_files_hashed | 13 |
| merkle_seal_present | True |
| merkle_before_sha256 | 9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256 |
| merkle_after_sha256 | 9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256 |
| server_stdout_sha256 | 74C812B801DE82DCC62B034180443945A746A9E3C1BD563C9F96110487DA8B39 |
| server_stderr_sha256 | DF85E52BF12DD3D79257261CE69B4BE1601E28FCE76549221B5B573DEBF02136 |
| git_branch | temp-reims |
| git_commit | 977bb2fa5a2ccccd60e8e509f59695dc463ec995 |
| git_tags | audit-traceability-3-domains-20260428-223139 |
| git_status |  M merkle_seal.json; ?? RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1; ?? RUN_AUDIT_TOTAL_METRICS_PROOF.ps1 |

## 6. Categories de metriques

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

## 7. Matrice de preuves

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
| Tracabilite decisions | 3 decision_*.json creees pendant audit | OK |
| Scellage Merkle | merkle before/after snapshot + hash | OK |
| Runtime hash | 13 fichiers runtime hashes | OK |
| Logs serveur | stdout/stderr hashes apres arret serveur | OK |
| Manifest preuve | TRACE_MANIFEST.json hash=D58F839256D1E4D7D8856D19167B36486E392407A068071869FC2F32984D42D1 | OK |
| Racine audit | AUDIT_ROOT_SHA256=13fbbfdaab4e4997ec86e064613c2e2871d5e5f987f61ac84ffece6da6bbc583 | OK |
| Reproductibilite Git | branch/commit/tag/status captures | OK |

## 8. Hashes majeurs

| Element | SHA256 | Source |
| --- | --- | --- |
| MERKLE_BEFORE_SHA256 | 9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256 | merkle_seal_before.json |
| MERKLE_AFTER_SHA256 | 9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256 | merkle_seal_after.json |
| TRACE_MANIFEST_SHA256 | D58F839256D1E4D7D8856D19167B36486E392407A068071869FC2F32984D42D1 | TRACE_MANIFEST.json |
| AUDIT_ROOT_SHA256 | 13fbbfdaab4e4997ec86e064613c2e2871d5e5f987f61ac84ffece6da6bbc583 | AUDIT_ROOT_SHA256.txt |
| REPORT_SHA256 | CDDBC09E15B76BE99A360314B3AAC46E8F8EBFA09DBD4C04C614A3A6D642DC19 | REPORT_SHA256.txt |
| SERVER_STDOUT_SHA256 | 74C812B801DE82DCC62B034180443945A746A9E3C1BD563C9F96110487DA8B39 | server.stdout.log |
| SERVER_STDERR_SHA256 | DF85E52BF12DD3D79257261CE69B4BE1601E28FCE76549221B5B573DEBF02136 | server.stderr.log |

## 9. Decisions creees pendant audit

| name | bytes | sha | FullName |
| --- | --- | --- | --- |
| decision_bank_1777410262369.json | 3720 |  |  |
| decision_gps_defense_aviation_1777410263804.json | 3448 |  |  |
| decision_trading_1777410263227.json | 3461 |  |  |

## 10. Fichiers runtime hashes

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
| .\merkle_seal.json | 317 | 9D1D9AAEDCF8520A4171448F17B21782986060FAE680F714EBF8CAA03FCE8256 |
| .\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1 | 27280 | FDB420E78231BCCA59798DD66C64D47630A7AFB54E77F1693330270F27167A4F |

## 11. Lecture froide

- Le moteur ne sort pas seulement un verdict.
- Il retourne des metriques exploitables.
- Il garde les inputs.
- Il garde les outputs.
- Il genere des decisions runtime.
- Il hashe les artefacts.
- Il produit un manifest.
- Il calcule une racine audit.
- Il rattache la preuve a Git : branche, commit, tag, status.

Conclusion : audit multi-domaines reproductible, trace, hashe, lisible, avec preuve de decision avant action.
