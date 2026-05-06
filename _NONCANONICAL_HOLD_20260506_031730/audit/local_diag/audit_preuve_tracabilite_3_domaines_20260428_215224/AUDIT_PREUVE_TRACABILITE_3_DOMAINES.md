# Audit preuve / securite / tracabilite — Obsidia X-108

Date : 2026-04-28 21:55:12
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit ID : `audit_preuve_tracabilite_3_domaines_20260428_215224`
AUDIT_ROOT_SHA256 : `028fe5c349460aade882621272248873a029a4466e316aa7a43ccab1de3507e7`
TRACE_MANIFEST_SHA256 : `FFF78032FC51523CB6DAB78995494A403EC1B9ED271335105977F61D259E53D4`

## 1. Contexte Git

| Element | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `d3a2a99cf4d05084876537de883b0eb95961d23c` |
| Commit court | `d3a2a99` |
| Tags sur HEAD | `node-bridge-terrain-server-fix-2026-04-28` |
| Working tree | ` M merkle_seal.json  M sigma/utils/__pycache__/__init__.cpython-313.pyc  M sigma/utils/__pycache__/indicators.cpython-313.pyc ?? RUN_AUDIT_PREUVE_TRACABILITE_3_DOMAINES.ps1 ?? RUN_AUDIT_VISUEL_3_DOMAINES.ps1` |

## 2. Tableau decisionnel

| Domaine | Verdict | Gate X-108 | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| bank | ANALYZE | BLOCK | 0.5 | 0.95 | 0.66 | 0.7033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 55 |
| trading | REVIEW | HOLD | 0.5 | 0.75 | 0.6 | 0.6167 | S2 | RISK_FLAGS_REQUIRE_DELAY | 55 |
| gps_defense_aviation | ABORT_TRAJECTORY | BLOCK | 0.35 | 0.95 | 0.51 | 0.6033 | S4 | CONTRADICTION_THRESHOLD_REACHED | 59 |

## 3. Compteurs de tracabilite

| Preuve | Nombre / Etat |
|---|---:|
| Domaines testes | 3 |
| Inputs JSON generes | 3 |
| Reponses JSON generees | 3 |
| Fichiers metriques generes | 3 |
| Decisions avant audit | 8398 |
| Decisions apres audit | 8409 |
| Decisions creees pendant audit | 11 |
| Fichiers runtime hashes | 14 |
| Merkle seal present | True |
| SHA serveur stdout | `NA` |
| SHA serveur stderr | `NA` |

## 4. Traces par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Fichier input | Fichier response |
|---|---:|---:|---:|---|---|
| bank | `988680FD35AD` | `0D7A43B3506D` | `61DEFBAC0E23` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\input_bank.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\response_bank.json` |
| trading | `A09D6DEE2AD5` | `5E69556FD774` | `BB0CFC62DAD5` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\input_trading.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\response_trading.json` |
| gps_defense_aviation | `0E9835CD2BEB` | `71616C7F6563` | `7EB761F95A19` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\input_gps_defense_aviation.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\response_gps_defense_aviation.json` |

## 5. Decisions runtime creees pendant audit

| Fichier | Taille | SHA256 |
|---|---:|---:|
| `decision_bank_1777406033658.json` | 3720 | `E26509B41ECEC312DAF90C5374662296110218E78C5692AE590553048A3D8422` |
| `decision_bank_1777406033997.json` | 3468 | `A1098DBE41707049713A6CA436E7AB189DCB7E83471A74D150FD5931913F8F95` |
| `decision_gps_defense_aviation_1777406030615.json` | 3349 | `E1B6E33283546E059265791962BFDD9BD73AD52C6E8B0CAC6F1570C676F0621B` |
| `decision_gps_defense_aviation_1777406034791.json` | 3448 | `D878F592ED614FA88F2D7E312730F357D20768680726311F6403CE5AC017EB65` |
| `decision_gps_defense_aviation_1777406035056.json` | 3349 | `01B19DB793AABC90CB1CD6ABD44E7963D71E58A361A8E0CD87E153F7301A524C` |
| `decision_gps_defense_aviation_1777406039507.json` | 3349 | `F75A7DD676524A47DFBACD6C0439B79538A56129EBBFFEA898590A570E11428F` |
| `decision_trading_1777406032390.json` | 3520 | `590C91846586B2FB8DE4D97C0DADA844ED57470B3110DCD3D2AA65CF3307AA86` |
| `decision_trading_1777406034278.json` | 3461 | `947C0B4EA2B98F3F3AA3B09CA2090A6CA9EC508003AFB97C02835A38524B5392` |
| `decision_trading_1777406035176.json` | 3520 | `41DC8EB6FD2538366E81BE35CA59360385D601393C89CC998F7E1B34EEF00406` |
| `decision_trading_1777406038282.json` | 3520 | `865D835199FC9FA961E3E9CA84967F406A92E163D96F21A804209ED492187CB4` |
| `decision_trading_1777406041140.json` | 3520 | `9510514C9B2C9B576A0094145ACA5D768698623B778395EBD72E7F5ACBDE5164` |

## 6. Hashes fichiers runtime critiques

| Fichier | Present | SHA256 |
|---|---:|---:|
| `.\package.json` | True | `5D1BE1EEF297C6FD72842450585EEF969F08AEC6A7DA52C99D4A415D48E2E646` |
| `.\package-lock.json` | True | `B461284B681814D76BBFA38676AD75E866F4276F1B2D0E3EE50A4805631985F7` |
| `.\MonProjet\server.kernel.sealed.cjs` | True | `DA2904C5D4604684B19CF557F602E7F65EC46E8B183C59F78CF9B3606F16FA78` |
| `.\sigma\contracts.py` | True | `6FA4646032A2C2E82FC08C3563403A5FA86E41D2B312E170A960AF80FB995178` |
| `.\sigma\aggregation.py` | True | `3F5EFD090286212E5B837AFEA9FCDB35E0456DF431E90A52B3986938EADC8A49` |
| `.\sigma\guard.py` | True | `5B19A0CBBF78555EFF0F2CC96F8FD21867A2BFC2212A830E319678A7FFF08C18` |
| `.\sigma\protocols.py` | True | `9FD36D072C4E3DEC3A500D52E67DDC5AF011D16DB92AFFE3871523CCD70204DF` |
| `.\sigma\run_pipeline.py` | True | `3415EF9B448B83E73BFF4E298D7D9BD44C2B903A1C6A8B2F2A4013076E54C540` |
| `.\sigma\registry.py` | True | `AC46F0FDA906EEB289C8C1007FAA6B0C0DAD59DD071D465A2BFE3E73A431E510` |
| `.\sigma\obsidia_sigma_v130.py` | True | `5D6E71983F3974DB4853ECE436126FF7B4511524EF69535D2B3668521AD0B314` |
| `.\audit_merkle.py` | True | `C84D014DEE0A8DF44035A17619EF35A122085D2C0796FFE8E70A89E5091CF481` |
| `.\merkle_seal.json` | True | `02BF214E2C2B1203DF5A7B89BA3068F6C9B821CEA9ECA48EA14987D9558A5B77` |
| `.\proofs\lean\lakefile.lean` | True | `89821C9CB272362F3443560D95612A00F3FEE4E66EA41DB2D9354FE832BB35FC` |
| `.\proofs\lean\lean-toolchain` | True | `26DF5F74B79AF0CD9E298B6583993699A54938D047BA1919428DA80D3AE80C6E` |

## 7. Merkle / Seal

| Element | Valeur |
|---|---|
| merkle_seal.json present | True |
| merkle_seal.json SHA256 | `02BF214E2C2B1203DF5A7B89BA3068F6C9B821CEA9ECA48EA14987D9558A5B77` |
| snapshot seal | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\merkle_seal_snapshot.txt` |

## 8. Lecture securite

### bank

- Sens metier : Transaction bancaire risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict metier : `ANALYZE`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Nombre de metriques retournees : 55
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\metrics_bank.csv`

### trading

- Sens metier : Ordre trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict metier : `REVIEW`
- Gate X-108 : `HOLD`
- Severity : `S2`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Lecture securite : SECURITE TEMPORELLE — action retenue. X-108 impose une attente / coherence avant action.
- Nombre de metriques retournees : 55
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\metrics_trading.csv`

### gps_defense_aviation

- Sens metier : Navigation aviation/GPS degradee : signal faible, conflit source, spoofing, deviation, skew temporel.
- Verdict metier : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Nombre de metriques retournees : 59
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_215224\metrics_gps_defense_aviation.csv`

## 9. Ce que cet audit prouve

| Axe | Preuve visible | Statut |
|---|---|---:|
| Routage domaine | 3 domaines appellent le meme endpoint /kernel/ragnarok | OK |
| Gouvernance X-108 | Chaque domaine retourne un gate X-108 | OK |
| Securite avant action | Les cas risques sont bloques ou controles avant execution | OK |
| Tracabilite input | Chaque payload envoye est sauvegarde et hashe | OK |
| Tracabilite output | Chaque reponse est sauvegardee et hashee | OK |
| Tracabilite decision | Les decision_*.json sont comptees avant/apres et hashees | OK |
| Tracabilite runtime | Les fichiers critiques moteur sont hashes | OK |
| Scellage | merkle_seal.json est snapshot + SHA256 | OK |
| Racine audit | AUDIT_ROOT_SHA256 calcule sur les preuves | OK |
| Manifest preuve | TRACE_MANIFEST.json + SHA256 | OK |

## 10. Limites

- Ne prouve pas une connexion bancaire reelle.
- Ne prouve pas une connexion avion reelle.
- Ne prouve pas une execution trading reelle.
- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe et rend auditable des decisions simulees multi-domaines.

## 11. Fichiers principaux

- `AUDIT_PREUVE_TRACABILITE_3_DOMAINES.md`
- `TRACE_MANIFEST.json`
- `AUDIT_ROOT_SHA256.txt`
- `artifact_hash_manifest.csv`
- `runtime_file_hashes.csv`
- `decisions_before.csv`
- `decisions_after.csv`
- `decisions_created.csv`
- `audit_preuve_tracabilite_3_domaines.csv`
- `audit_preuve_tracabilite_3_domaines.json`
