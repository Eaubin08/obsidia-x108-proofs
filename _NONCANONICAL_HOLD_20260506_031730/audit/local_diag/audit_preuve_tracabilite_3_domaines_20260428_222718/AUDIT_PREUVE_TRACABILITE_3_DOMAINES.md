# Audit preuve / securite / tracabilite — Obsidia X-108

Date : 2026-04-28 22:29:41
Endpoint : `http://localhost:3001/kernel/ragnarok`
Audit ID : `audit_preuve_tracabilite_3_domaines_20260428_222718`
AUDIT_ROOT_SHA256 : `9d439d92b24fc524ad08a5fa6c1d243f68338189014471002a07ff6b3abe81bc`
TRACE_MANIFEST_SHA256 : `87DFD882054930DE02F0D46D590615A16EB5002732F45BBB2876DA6F7B1F6008`

## 1. Contexte Git

| Element | Valeur |
|---|---|
| Branche | `temp-reims` |
| Commit | `977bb2fa5a2ccccd60e8e509f59695dc463ec995` |
| Commit court | `977bb2f` |
| Tags sur HEAD | `NO_TAG_ON_HEAD` |
| Working tree | `CLEAN` |

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
| Decisions avant audit | 8457 |
| Decisions apres audit | 8467 |
| Decisions creees pendant audit | 10 |
| Fichiers runtime hashes | 14 |
| Merkle seal present | True |
| SHA serveur stdout | `NA` |
| SHA serveur stderr | `NA` |

## 4. Traces par domaine

| Domaine | Input SHA | Response SHA | Metrics SHA | Fichier input | Fichier response |
|---|---:|---:|---:|---|---|
| bank | `988680FD35AD` | `3ABC83763402` | `8AF5C65DB35C` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\input_bank.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\response_bank.json` |
| trading | `A09D6DEE2AD5` | `E11CAE9A5C34` | `52D0D88AA14E` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\input_trading.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\response_trading.json` |
| gps_defense_aviation | `0E9835CD2BEB` | `DA9F9FBB8203` | `481B33B1D77E` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\input_gps_defense_aviation.json` | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\response_gps_defense_aviation.json` |

## 5. Decisions runtime creees pendant audit

| Fichier | Taille | SHA256 |
|---|---:|---:|
| `decision_bank_1777408112603.json` | 3720 | `E65B33148D7DD07D174C7D5F8E2C411FFE85597D0989B4437E17C2D866426B10` |
| `decision_bank_1777408117840.json` | 3468 | `515F10FDF7CB01E4A7FEB507B864DD7F01C88963C3B9DC2F19D6BDD6EB4325B2` |
| `decision_gps_defense_aviation_1777408109527.json` | 3349 | `081AB8CA0848FFB89B90F42F0AFD5E0B80F2AD155E5D52E2CA6F8D0BA0D822A4` |
| `decision_gps_defense_aviation_1777408115215.json` | 3349 | `71DF0B3754495BD1229A19318E3B84427DB6B01DD68CB8C6F61D23681988C27F` |
| `decision_gps_defense_aviation_1777408115307.json` | 3448 | `9E6EA5FB0C4A12B76B2609424FE863A24AC28C7F2229E99ED375A9C4804DBD40` |
| `decision_trading_1777408109847.json` | 3520 | `7D6955A4E618F896107D153C3D6BF68DBA7DBD9ED57B843285A625F67CA4D2BA` |
| `decision_trading_1777408112627.json` | 3520 | `BC0F039AB6C226D1F626B670ABA8D7B6D45C322C633B4D3CCA3FE28643C362A4` |
| `decision_trading_1777408114633.json` | 3461 | `AC7ABD3D9D142031D596D1F3A6CD6371F03C39D13D63860FC20718A00583496F` |
| `decision_trading_1777408115536.json` | 3520 | `22F32187A243DE3961068E1782F3E79D55B6970CF1E816E57FF3065A94D64CFA` |
| `decision_trading_1777408118295.json` | 3520 | `37DBAD69768268B48490A3F3C26A38770798B7E7F199EFBD5D43632C37C464D6` |

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
| `.\merkle_seal.json` | True | `F5750BC62E0E84822B29E460A51FD2856FD9992790AC6B1185316227AA56A227` |
| `.\proofs\lean\lakefile.lean` | True | `89821C9CB272362F3443560D95612A00F3FEE4E66EA41DB2D9354FE832BB35FC` |
| `.\proofs\lean\lean-toolchain` | True | `26DF5F74B79AF0CD9E298B6583993699A54938D047BA1919428DA80D3AE80C6E` |

## 7. Merkle / Seal

| Element | Valeur |
|---|---|
| merkle_seal.json present | True |
| merkle_seal.json SHA256 | `F5750BC62E0E84822B29E460A51FD2856FD9992790AC6B1185316227AA56A227` |
| snapshot seal | `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\merkle_seal_snapshot.txt` |

## 8. Lecture securite

### bank

- Sens metier : Transaction bancaire risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte.
- Verdict metier : `ANALYZE`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Nombre de metriques retournees : 55
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\metrics_bank.csv`

### trading

- Sens metier : Ordre trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves.
- Verdict metier : `REVIEW`
- Gate X-108 : `HOLD`
- Severity : `S2`
- Reason : `RISK_FLAGS_REQUIRE_DELAY`
- Lecture securite : SECURITE TEMPORELLE — action retenue. X-108 impose une attente / coherence avant action.
- Nombre de metriques retournees : 55
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\metrics_trading.csv`

### gps_defense_aviation

- Sens metier : Navigation aviation/GPS degradee : signal faible, conflit source, spoofing, deviation, skew temporel.
- Verdict metier : `ABORT_TRAJECTORY`
- Gate X-108 : `BLOCK`
- Severity : `S4`
- Reason : `CONTRADICTION_THRESHOLD_REACHED`
- Lecture securite : SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante.
- Nombre de metriques retournees : 59
- Fichier metriques complet : `.\audit\local_diag\audit_preuve_tracabilite_3_domaines_20260428_222718\metrics_gps_defense_aviation.csv`

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

---

## 12. Clôture finale post-runtime

Cette section est ajoutée après arrêt du serveur afin de hasher les logs qui étaient verrouillés pendant l'exécution.

### Git

| Champ | Valeur |
|---|---|
| Branche | $Branch |
| Commit | $Commit |
| Tags HEAD | $Tags |
| Status | $Status |

### Hashes logs serveur

| Fichier | SHA256 |
|---|---|
| server.stdout.log | $StdoutHash |
| server.stderr.log | $StderrHash |

### Racine finale audit

| Élément | Valeur |
|---|---|
| Manifest final | ARTIFACT_HASH_MANIFEST_FINAL.csv |
| Racine finale | $RootHash |

### Lecture

La preuve contient maintenant :
- décisions métiers des 3 domaines ;
- gates X-108 ;
- métriques retournées ;
- inputs hashés ;
- outputs hashés ;
- fichiers metrics hashés ;
- décisions runtime créées pendant audit ;
- état Git ;
- tag Git ;
- logs serveur hashés après arrêt ;
- racine finale calculée sur les artefacts d'audit.

