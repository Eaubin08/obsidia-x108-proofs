# P56C — P08/P10/P11 Conflict Audit Only
## Status
CONFLICT_AUDIT_GENERATED_PATCH_NOT_APPLIED
## Fusion status
FUSION_BLOCKED_PENDING_P08_P10_P11_DECISIONS
## Source patch authorized
false

## P08 — protocols.py
- Focus: domain/protocol extension
- Decision: GPS_EXTENSION_DETECTED_REQUIRES_DECISION
- Blocking: True
- Diff: `docs\core_import\P56C_AUDIT_ONLY_P08_protocols.py.diff`
- Core lines: 42
- Proof lines: 51

### Added functions in proof
- run_gps_defense_aviation_pipeline

### Added imports in proof
- from .aggregation import aggregate_bank, aggregate_ecom, aggregate_trading, aggregate_gps_defense_aviation
- from .contracts import BankState, CanonicalDecisionEnvelope, EcomState, TradingState, GpsDefenseAviationState
- from .domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents

### Notes
- Proof adds GPS defense aviation protocol surface.
- Must not overwrite core protocols automatically.

### Risk hits proof
- L3: `from .aggregation import aggregate_bank, aggregate_ecom, aggregate_trading, aggregate_gps_defense_aviation`
- L8: `from .domains.gps_defense_aviation_agents import build_gps_defense_aviation_agents`
- L45: `def run_gps_defense_aviation_pipeline(state: GpsDefenseAviationState) -> CanonicalDecisionEnvelope:`
- L46: `aggregate = aggregate_gps_defense_aviation(`
- L47: `[a.evaluate(state) for a in build_gps_defense_aviation_agents()]`

## P10 — obsidia_sigma_v130.py
- Focus: sigma monitor config/path/encoding/metrics
- Decision: CONFIG_PATH_CONFLICT_REQUIRES_DECISION
- Blocking: True
- Diff: `docs\core_import\P56C_AUDIT_ONLY_P10_obsidia_sigma_v130.py.diff`
- Core lines: 295
- Proof lines: 292

### Added functions in proof

### Added imports in proof

### Notes
- Default config path differs: core agents/sigma_config.json vs proof sigma/sigma_config.json.
- Proof adds explicit UTF-8 encoding for file IO.

### Risk hits proof
- L6: `- Les seuils sont lus depuis sigma/sigma_config.json si present.`
- L17: `monitor.evaluate_step(severity, risks, contras)`
- L31: `# Valeurs par defaut v1.4.0 (utilisees si sigma_config.json absent)`
- L37: `def _load_sigma_config(config_path: str = "sigma/sigma_config.json") -> Dict[str, Any]:`
- L42: `p = Path(config_path)`
- L45: `with open(p, "r", encoding="utf-8") as f:`
- L57: `Les seuils sont charges depuis sigma/sigma_config.json (si present),`
- L67: `config_path: str = "sigma/sigma_config.json",`
- L70: `cfg = _load_sigma_config(config_path)`
- L77: `self.config_source = config_path if Path(config_path).exists() else "defaults_v1.4.0"`
- L106: `def _to_vector(self, severity: str, risk_count: int, contra_count: int) -> float:`
- L107: `base = SEVERITY_MAP.get(severity, 0.0)`
- L116: `severity: str,`
- L125: `z_t = self._to_vector(severity, len(risks), len(contras))`
- L130: `"severity": severity,`
- L264: `path = Path(report_path)`
- L268: `with open(path, "r", encoding="utf-8") as f:`
- L275: `with open(path, "w", encoding="utf-8") as f:`
- L276: `json.dump(existing, f, indent=2)`
- L289: `p = Path(fp)`

## P11 — run_pipeline.py
- Focus: runtime pipeline behavior
- Decision: RUNTIME_BEHAVIOR_DELTA_REQUIRES_ADAPTER
- Blocking: True
- Diff: `docs\core_import\P56C_AUDIT_ONLY_P11_run_pipeline.py.diff`
- Core lines: 59
- Proof lines: 271

### Added functions in proof
- _is_plain_number
- _require_int
- _require_number
- apply_sigma
- load_state
- validate_bank_payload

### Added imports in proof
- from sigma.contracts import TradingState, BankState, EcomState, GpsDefenseAviationState
- from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor
- from sigma.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline, run_gps_defense_aviation_pipeline
- math

### Notes
- Proof runner adds Sigma application layer.
- Proof runner may mutate output market_verdict/severity via apply_sigma.
- Do not overwrite core python_agents/run_pipeline.py.

### Risk hits proof
- L13: `ROOT = Path(__file__).resolve().parent.parent`
- L18: `from sigma.protocols import run_trading_pipeline, run_bank_pipeline, run_ecom_pipeline, run_gps_defense_aviation_pipeline`
- L41: `ALLOWED_BANK_FIELDS = {f.name for f in dataclasses.fields(BankState)}`
- L51: `JSON must be parsed before trying Path(arg).exists(), otherwise Linux can`
- L65: `p = Path(raw)`
- L178: `unknown = sorted(set(state_data.keys()) - ALLOWED_BANK_FIELDS)`
- L204: `severity=result_dict.get("severity", "S0"),`
- L212: `result_dict["market_verdict"] = "HOLD_STABILITY_ALERT"`
- L213: `result_dict["severity"] = "S4"`
- L214: `result_dict["sigma_override"] = True`
- L216: `result_dict["sigma_override"] = False`
- L229: `print(json.dumps({"error": "Usage: run_pipeline.py <domain> <json_state_or_json_file>"}), file=sys.stderr)`
- L236: `print(json.dumps({"error": f"Invalid JSON input: {e}"}), file=sys.stderr)`
- L239: `sigma = ObsidiaSigmaMonitor(config_path=str(ROOT / "sigma" / "sigma_config.json"))`
- L252: `elif domain == "gps_defense_aviation":`
- L254: `result = run_gps_defense_aviation_pipeline(state)`
- L256: `print(json.dumps({"error": f"Unknown domain: {domain}. Use trading|bank|ecom|gps_defense_aviation"}), file=sys.stderr)`
- L261: `print(json.dumps(result_dict, ensure_ascii=False))`
- L263: `print(json.dumps({"error": f"State validation error: {e}"}), file=sys.stderr)`
- L266: `print(json.dumps({"error": f"Pipeline error: {e}"}), file=sys.stderr)`
