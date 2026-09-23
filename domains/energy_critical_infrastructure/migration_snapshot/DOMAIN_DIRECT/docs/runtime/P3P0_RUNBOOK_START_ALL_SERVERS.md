# P3P0 — Runbook démarrage runtime Obsidia / X108

Status: DOC_ONLY_REAL_COMMANDS_NOT_COMMITTED
Scope: démarrage local Kernel + API + connecteurs runtime
Repo: `obsidia-x108-proofs_REMOTE_A5F21C6B`

---

## 0. Architecture runtime locale

```text
Kernel X108  → serveur décisionnel réel       → port 3001
API Obsidia  → bridge HTTP vers le kernel      → port 8000
Connecteurs  → clients de test / affichage     → bank / aviation / trading
```

Règle d’autorité :

```text
Kernel       = source de vérité
API          = bridge only
Connecteurs = callers / affichage uniquement
```

Les connecteurs ne sont pas des serveurs.
Ils lancent des appels vers l’API, qui relaie vers le Kernel.

---

## 1. Terminal 1 — Kernel X108

Laisser ce terminal ouvert.

```powershell
$REPO = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
Set-Location $REPO
chcp 65001
$env:PYTHONPATH = $REPO
$env:PYTHONIOENCODING = "utf-8"
node runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs
```

Commande courte si l’environnement est déjà prêt :

```powershell
node runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs
```

Résultat attendu :

```text
Prêt pour Ragnarok sur http://localhost:3001
```

Endpoint kernel :

```text
http://127.0.0.1:3001/kernel/ragnarok
```

---

## 2. Terminal 2 — API Obsidia 8000

Laisser ce terminal ouvert.

```powershell
$REPO = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
Set-Location $REPO
chcp 65001
$env:PYTHONPATH = $REPO
$env:PYTHONIOENCODING = "utf-8"
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```

Résultat attendu :

```text
Uvicorn running on http://127.0.0.1:8000
```

Endpoints API utilisés par les connecteurs :

```text
POST /api/live/kernel/adapters/bank
POST /api/live/kernel/adapters/gps
POST /api/live/kernel/adapters/trading
```

---

## 3. Terminal 3 — Connecteur Aviation / GPS

```powershell
$REPO = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
Set-Location $REPO
chcp 65001
$env:PYTHONPATH = $REPO
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"
python connectors\aviation_robo.py
```

Commande courte si l’environnement est déjà prêt :

```powershell
python connectors\aviation_robo.py
```

Résultat attendu :

```text
[AERO/GPS][ALLOW/S0]
TRAJECTORY_VALID
```

---

## 4. Terminal 4 — Connecteur Bank

```powershell
$REPO = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
Set-Location $REPO
chcp 65001
$env:PYTHONPATH = $REPO
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"
python connectors\bank_normal_flow.py
```

Commande courte si l’environnement est déjà prêt :

```powershell
python connectors\bank_normal_flow.py
```

Résultat attendu :

```text
[BANK][ALLOW/S1]
ANALYZE
```

---

## 5. Terminal 5 — Connecteur Trading

```powershell
$REPO = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
Set-Location $REPO
chcp 65001
$env:PYTHONPATH = $REPO
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"
python connectors\trading_live.py
```

Commande courte si l’environnement est déjà prêt :

```powershell
python connectors\trading_live.py
```

Résultat attendu :

```text
[TRADING][BLOCK/S4]
REVIEW
CONTRADICTION_THRESHOLD_REACHED
```

---

## 6. Séquence complète réelle

```text
Terminal 1:
node runtime_terrain_bank_trading_gps\server.kernel.sealed.cjs

Terminal 2:
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000

Terminal 3:
python connectors\aviation_robo.py

Terminal 4:
python connectors\bank_normal_flow.py

Terminal 5:
python connectors\trading_live.py
```

---

## 7. Vérifier que Kernel et API tournent

```powershell
Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "server\.kernel\.sealed\.cjs|apps\.obsidia_api\.main"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-List
```

Ports :

```powershell
netstat -ano | findstr ":3001"
netstat -ano | findstr ":8000"
```

---

## 8. Smoke API

```powershell
Invoke-WebRequest "http://127.0.0.1:8000/openapi.json" -UseBasicParsing |
  Select-Object StatusCode
```

Attendu :

```text
StatusCode : 200
```

---

## 9. Ordre d’arrêt

```text
1. Connecteurs : Ctrl+C ou fin naturelle
2. API : Ctrl+C
3. Kernel : Ctrl+C
```

Arrêt forcé Kernel + API :

```powershell
Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "server\.kernel\.sealed\.cjs|apps\.obsidia_api\.main"
  } |
  ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
  }
```

---

## 10. Freezes liés

Couleurs terminal :

```text
P3N0_TERMINAL_COLOR_STACK_FREEZE_20260612_084414
= VALIDATED_LOCAL_FREEZE_REPAIRED_NOT_COMMITTED
```

Métriques + consensus :

```text
P3O1_METRICS_CONSENSUS_FREEZE_20260612_091958
= VALIDATED_LOCAL_FREEZE_NOT_COMMITTED
```

---

## 11. Statut

```text
P3P0_RUNBOOK_START_ALL_SERVERS
= DOC_ONLY_REAL_COMMANDS_NOT_COMMITTED
```
