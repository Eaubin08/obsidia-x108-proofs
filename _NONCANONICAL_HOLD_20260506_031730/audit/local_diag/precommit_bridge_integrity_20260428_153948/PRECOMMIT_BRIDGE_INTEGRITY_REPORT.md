# PRECOMMIT BRIDGE INTEGRITY AUDIT — 20260428_153948

## 1. Git status
```text
 M connectors/bank_normal_flow.py
 M merkle_seal.json
 M server.kernel.sealed.cjs
 M sigma/utils/__pycache__/__init__.cpython-313.pyc
 M sigma/utils/__pycache__/indicators.cpython-313.pyc
?? audit/local_diag/
?? audit/local_rescue/
```

## 2. Git diff stat
```text
 connectors/bank_normal_flow.py                     |   7 ++--
 merkle_seal.json                                   |  10 ++---
 server.kernel.sealed.cjs                           |  41 +++++++++++++--------
 sigma/utils/__pycache__/__init__.cpython-313.pyc   | Bin 188 -> 188 bytes
 sigma/utils/__pycache__/indicators.cpython-313.pyc | Bin 3276 -> 3276 bytes
 5 files changed, 34 insertions(+), 24 deletions(-)
```

## 3. Git diff check
```text
merkle_seal.json:3: trailing whitespace.
+    "audit_date": "2026-04-28 15:30:44",
merkle_seal.json:4: trailing whitespace.
+    "total_proofs_count": 2320,
merkle_seal.json:5: trailing whitespace.
+    "merkle_root": "55bf8fbe215a4c6b5d5da237ded947fdd8d5a2c81f7a65a38e7cb88b7344d35a",
merkle_seal.json:6: trailing whitespace.
+    "first_proof": "decision_bank_1777377982714.json",
merkle_seal.json:7: trailing whitespace.
+    "last_proof": "decision_trading_1777383043195.json"
```

## 4. Critical source files integrity table

| File | Exists | Git status | SHA256 current | HEAD blob | BOM |
|---|---:|---|---|---|---:|
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | True |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |
| $f | True | $status | $sha | $headBlob | False |

## 5. Bridge mapping scan
```text

  MonProjet\server.kernel.sealed.cjs:6:app.use(express.json());
  MonProjet\server.kernel.sealed.cjs:7:
> MonProjet\server.kernel.sealed.cjs:8:app.post('/kernel/ragnarok', (req, res) => {
  MonProjet\server.kernel.sealed.cjs:9:    const sigmaDir = path.join(__dirname, '..', 'sigma');
> MonProjet\server.kernel.sealed.cjs:10:    const scriptPath = path.join(sigmaDir, 'run_pipeline.py');
  MonProjet\server.kernel.sealed.cjs:11:    let tempFilePath = null;
  MonProjet\server.kernel.sealed.cjs:12:
  MonProjet\server.kernel.sealed.cjs:13:    // --- CHIRURGIE DYNAMIQUE ---
> MonProjet\server.kernel.sealed.cjs:14:    const domain = req.body.domain || "gps_defense_aviation";
> MonProjet\server.kernel.sealed.cjs:15:    const safeDomain = String(domain).replace(/[^a-zA-Z0-9_-]/g, "_");
  MonProjet\server.kernel.sealed.cjs:16:    tempFilePath = path.join(
  MonProjet\server.kernel.sealed.cjs:17:        __dirname,
> MonProjet\server.kernel.sealed.cjs:18:        
`input_${safeDomain}_${Date.now()}_${process.pid}_${Math.random().toString(16).slice(2)}.json`
  MonProjet\server.kernel.sealed.cjs:19:    );
> MonProjet\server.kernel.sealed.cjs:20:    const dataToProcess = req.body.state || req.body.data || 
req.body.payload || req.body;
  MonProjet\server.kernel.sealed.cjs:21:
  MonProjet\server.kernel.sealed.cjs:22:    try {
> MonProjet\server.kernel.sealed.cjs:23:        fs.writeFileSync(tempFilePath, JSON.stringify(dataToProcess, 
null, 2));
  MonProjet\server.kernel.sealed.cjs:24:    } catch (err) {
  MonProjet\server.kernel.sealed.cjs:25:        return res.status(500).json({ error: "Failed to write temp 
file", details: err.message });
  MonProjet\server.kernel.sealed.cjs:26:    }
  MonProjet\server.kernel.sealed.cjs:27:
> MonProjet\server.kernel.sealed.cjs:28:    console.log(`\x1b[35m[BRIDGE]\x1b[0m ðŸš€ Routing -> Domain: 
${domain}`);
  MonProjet\server.kernel.sealed.cjs:29:
> MonProjet\server.kernel.sealed.cjs:30:    const py = spawn('python', ['-u', scriptPath, domain, 
tempFilePath], {
  MonProjet\server.kernel.sealed.cjs:31:        env: { ...process.env, PYTHONPATH: path.join(__dirname, '..') }
  MonProjet\server.kernel.sealed.cjs:32:    });
  MonProjet\server.kernel.sealed.cjs:33:
  MonProjet\server.kernel.sealed.cjs:34:    let result = '';
  MonProjet\server.kernel.sealed.cjs:35:
> MonProjet\server.kernel.sealed.cjs:36:    py.stdout.on('data', (data) => {
> MonProjet\server.kernel.sealed.cjs:37:        const str = data.toString();
  MonProjet\server.kernel.sealed.cjs:38:        if (str.trim().startsWith('{')) {
  MonProjet\server.kernel.sealed.cjs:39:            result += str;
  MonProjet\server.kernel.sealed.cjs:40:        } else {
  MonProjet\server.kernel.sealed.cjs:43:    });
  MonProjet\server.kernel.sealed.cjs:44:
> MonProjet\server.kernel.sealed.cjs:45:    py.stderr.on('data', (data) => {
> MonProjet\server.kernel.sealed.cjs:46:        console.error(`\x1b[33mðŸ“¢ [KERNEL_TRACE]:\x1b[0m 
${data.toString().trim()}`);
  MonProjet\server.kernel.sealed.cjs:47:    });
  MonProjet\server.kernel.sealed.cjs:48:
  MonProjet\server.kernel.sealed.cjs:49:    py.on('close', (code) => {
  MonProjet\server.kernel.sealed.cjs:60:            const parsedResult = JSON.parse(result);
  MonProjet\server.kernel.sealed.cjs:61:
> MonProjet\server.kernel.sealed.cjs:62:            const allDataDir = path.join(__dirname, 'allData');
> MonProjet\server.kernel.sealed.cjs:63:            if (!fs.existsSync(allDataDir)) fs.mkdirSync(allDataDir);
  MonProjet\server.kernel.sealed.cjs:64:
> MonProjet\server.kernel.sealed.cjs:65:            const filename = `decision_${domain}_${Date.now()}.json`;
> MonProjet\server.kernel.sealed.cjs:66:            fs.writeFileSync(path.join(allDataDir, filename), 
JSON.stringify(parsedResult, null, 2));
  MonProjet\server.kernel.sealed.cjs:67:            console.log(`\x1b[32mðŸ’¾ [SAVE]\x1b[0m ${filename}`);
  MonProjet\server.kernel.sealed.cjs:68:
  MonProjet\server.kernel.sealed.cjs:69:            res.json(parsedResult);



```

## 6. Bank validation scan
```text

  sigma\run_pipeline.py:14:    sys.path.insert(0, str(ROOT))
  sigma\run_pipeline.py:15:
> sigma\run_pipeline.py:16:from sigma.contracts import TradingState, BankState, EcomState, 
GpsDefenseAviationState
  sigma\run_pipeline.py:17:from sigma.protocols import run_trading_pipeline, run_bank_pipeline, 
run_ecom_pipeline, run_gps_defense_aviation_pipeline
  sigma\run_pipeline.py:18:from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor
  sigma\run_pipeline.py:19:
  sigma\run_pipeline.py:20:
> sigma\run_pipeline.py:21:REQUIRED_BANK_FIELDS = {
  sigma\run_pipeline.py:22:    "transaction_type",
  sigma\run_pipeline.py:23:    "amount",
  sigma\run_pipeline.py:24:    "channel",
  sigma\run_pipeline.py:25:    "counterparty_known",
  sigma\run_pipeline.py:38:}
  sigma\run_pipeline.py:39:
> sigma\run_pipeline.py:40:ALLOWED_BANK_FIELDS = {f.name for f in dataclasses.fields(BankState)}
  sigma\run_pipeline.py:41:
  sigma\run_pipeline.py:42:
  sigma\run_pipeline.py:43:def load_state(arg: str) -> dict:
  sigma\run_pipeline.py:44:    p = Path(arg)
  sigma\run_pipeline.py:48:
  sigma\run_pipeline.py:49:
> sigma\run_pipeline.py:50:def validate_bank_payload(state_data: dict) -> None:
  sigma\run_pipeline.py:51:    if not isinstance(state_data, dict):
  sigma\run_pipeline.py:52:        raise ValueError("Bank payload must be a JSON object")
  sigma\run_pipeline.py:53:
> sigma\run_pipeline.py:54:    missing = sorted(REQUIRED_BANK_FIELDS - set(state_data.keys()))
  sigma\run_pipeline.py:55:    if missing:
  sigma\run_pipeline.py:56:        raise ValueError(f"Missing required bank fields: {', '.join(missing)}")
  sigma\run_pipeline.py:57:
> sigma\run_pipeline.py:58:    unknown = sorted(set(state_data.keys()) - ALLOWED_BANK_FIELDS)
  sigma\run_pipeline.py:59:    if unknown:
  sigma\run_pipeline.py:60:        raise ValueError(f"Unknown bank fields: {', '.join(unknown)}")
  sigma\run_pipeline.py:61:
  sigma\run_pipeline.py:62:
  sigma\run_pipeline.py:105:            result = run_trading_pipeline(state)
  sigma\run_pipeline.py:106:        elif domain == "bank":
> sigma\run_pipeline.py:107:            validate_bank_payload(state_data)
> sigma\run_pipeline.py:108:            state = BankState(**state_data)
  sigma\run_pipeline.py:109:            result = run_bank_pipeline(state)
  sigma\run_pipeline.py:110:        elif domain == "ecom":
  sigma\run_pipeline.py:111:            state = EcomState(**state_data)
  sigma\run_pipeline.py:112:            result = run_ecom_pipeline(state)
  sigma\contracts.py:215:
  sigma\contracts.py:216:@dataclass
> sigma\contracts.py:217:class BankState(UniversalBase):
  sigma\contracts.py:218:    transaction_type: str = ""; amount: float = 0.0; channel: str = ""
  sigma\contracts.py:219:    counterparty_known: bool = False; counterparty_age_days: int = 0
  sigma\contracts.py:220:    account_balance: float = 0.0; available_cash: float = 0.0
  sigma\contracts.py:221:    historical_avg_amount: float = 0.0; behavior_shift_score: float = 0.0
  sigma\contracts.py:223:    affordability_score: float = 0.0; urgency_score: float = 0.0
  sigma\contracts.py:224:    identity_mismatch_score: float = 0.0; narrative_conflict_score: float = 0.0
> sigma\contracts.py:225:    device_trust_score: float = 0.0; recent_failed_attempts: int = 0
  sigma\contracts.py:226:    elapsed_s: float = 0.0; min_required_elapsed_s: float = 108.0
  sigma\contracts.py:227:    def __post_init__(self):
  sigma\contracts.py:228:        for field_info in fields(self):
  sigma\contracts.py:229:            val = getattr(self, field_info.name)



```

## 7. Merkle check
```text
MERKLE_EXIT=0
Merkle root declared: b9ac7a047f846764caebf32edb8ad491a697865530b1386e2080c3f517652bf8
Format VALID (SHA-256 hex) ÔÇö full recomputation requires audit_entries in metadata.json
```

## 8. Audit conclusion placeholder
```text
PRECOMMIT_AUDIT_GENERATED=TRUE
COMMIT_NOT_DONE_YET=TRUE
AUDIT_DIR=.\audit\local_diag\precommit_bridge_integrity_20260428_153948
REPORT=.\audit\local_diag\precommit_bridge_integrity_20260428_153948\PRECOMMIT_BRIDGE_INTEGRITY_REPORT.md
```
