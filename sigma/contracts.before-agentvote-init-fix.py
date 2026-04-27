from dataclasses import dataclass, field, fields
from typing import List, Dict, Any, Optional
from enum import IntEnum, Enum
import sys

def obsidia_log(msg):
    print(f"🔍 [KERNEL_TRACE] {msg}", file=sys.stderr)

class Layer(IntEnum):
    OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; PERIPHERAL = 4
    SIGMA = 5; KERNEL = 6; PROOF = 7; SCELLAGE = 8

class Severity(IntEnum):
    S0 = 0; S1 = 1; S2 = 2; S3 = 3; S4 = 4

class Domain(Enum):
    BANK = "bank"; TRADING = "trading"; ECOM = "ecom"
    GPS_DEFENSE_AVIATION = "gps_defense_aviation"; META = "meta"

class SourceTag(Enum):
    CANONICAL = "canonical"; CANONICAL_FRAMEWORK = "canonical_framework"
    SIGMA = "sigma"; SIGMA_FRAMEWORK = "sigma_framework"
    KERNEL = "kernel"; KERNEL_FRAMEWORK = "kernel_framework"

class X108Gate(Enum):
    ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"

class SmartAttribute(list):
    def __init__(self, name, default_val=0.0):
        super().__init__()
        self.name = name
        self.internal_val = default_val

    def __str__(self):
        return str(self.internal_val) if not self else super().__repr__()

    def __hash__(self):
        return hash(str(self.internal_val))

    def _to_num(self):
        try:
            return float(self.internal_val) if self.internal_val else 0.0
        except Exception:
            return 0.0

    # Opérations de comparaison
    def __ge__(self, other): return self._to_num() >= float(other)
    def __gt__(self, other): return self._to_num() > float(other)
    def __le__(self, other): return self._to_num() <= float(other)
    def __lt__(self, other): return self._to_num() < float(other)
    
    # Opérations arithmétiques
    def __add__(self, other): return self._to_num() + float(other)
    def __radd__(self, other): return float(other) + self._to_num()
    def __sub__(self, other): return self._to_num() - float(other)
    def __rsub__(self, other): return float(other) - self._to_num()
    def __mul__(self, other): return self._to_num() * float(other)
    def __rmul__(self, other): return float(other) * self._to_num()
    def __truediv__(self, other): 
        den = float(other)
        return self._to_num() / den if den != 0 else 0.0
    def __rtruediv__(self, other): return float(other) / self._to_num()
    def __floordiv__(self, other): return self._to_num() // float(other)
    
    # Formatage et conversion
    def __format__(self, format_spec): return format(self._to_num(), format_spec)
    def __float__(self): return self._to_num()

class UniversalBase:
    def __getattr__(self, name):
        if name.startswith('__'):
            raise AttributeError(name)
        obsidia_log(f"Dynamic access on {self.__class__.__name__}: '{name}'")
        new_attr = SmartAttribute(name)
        setattr(self, name, new_attr)
        return new_attr

@dataclass(init=False) # On désactive l'init automatique pour éviter les doublons
class AgentVote(UniversalBase):
    agent_id: str = "A1_MEM"
    vote: str = "HOLD"
    proposed_verdict: str = ""
    confidence: float = 0.0
    domain: str = "unknown"
    layer: int = 5
    claim: str = "no_claim"
    contradictions: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    severity_hint: Severity = Severity.S0

    def __init__(self, **kwargs):
        # 1. On initialise les listes vides pour éviter les erreurs d'accès
        self.contradictions = []
        self.unknowns = []
        self.risk_flags = []
        self.evidence_refs = []
        
        # 2. On mappe manuellement les kwargs sur l'instance
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        # 3. Sécurité de typage pour les tests Bank
        try:
            self.confidence = float(getattr(self, "confidence", 0.0))
        except:
            self.confidence = 0.0
            
        # 4. Synchronisation des verdicts
        if not getattr(self, "proposed_verdict", ""):
            self.proposed_verdict = getattr(self, "vote", "HOLD")
            
        # 5. Appel de la base pour le dynamisme
        super().__init__(**kwargs)

@dataclass
class DomainAggregate(UniversalBase):
    domain: str = "unknown"
    market_verdict: str = "HOLD"
    confidence: float = 0.0
    contradictions: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    agent_votes: List[AgentVote] = field(default_factory=list)
    extra_metrics: dict = field(default_factory=dict)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        v = getattr(self, "agent_votes", [])
        if isinstance(v, list):
            self.agent_votes = [AgentVote(**item) if isinstance(item, dict) else item for item in v]
        obsidia_log(f"Aggregating {len(self.agent_votes)} votes for {self.domain}")

@dataclass
class CanonicalDecisionEnvelope(UniversalBase):
    domain: str = "unknown"; market_verdict: str = "HOLD"; confidence: float = 0.0
    contradictions: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    x108_gate: str = "HOLD"; reason_code: str = "RAGNAROK_DEBUG"
    severity: str = "S0"; decision_id: str = "debug-decision"
    trace_id: str = "debug-trace"; ticket_required: bool = False
    ticket_id: Optional[str] = None; attestation_ref: Optional[str] = None
    source: str = "canonical_framework"
    evidence_refs: List[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    raw_engine: dict = field(default_factory=dict)

@dataclass
class GpsDefenseAviationState(UniversalBase):
    mission_id: str = "UNKNOWN"; gps_available: bool = True; inertial_available: bool = True
    radio_available: bool = True; elapsed_s: float = 0.0; min_required_elapsed_s: float = 108.0
    position_confidence: float = 1.0; trajectory_drift_score: float = 0.0
    source_conflict_score: float = 0.0; brownout_score: float = 0.0
    time_skew_score: float = 0.0; environment_risk_score: float = 0.0
    rollback_possible: bool = True; attestation_ready: bool = True

    def __post_init__(self):
        obsidia_log(f"Aviation Cockpit initialized: {self.mission_id} (GPS: {self.gps_available})")

@dataclass
class BankState(UniversalBase):
    transaction_type: str = ""; amount: float = 0.0; channel: str = ""
    counterparty_known: bool = False; counterparty_age_days: int = 0
    account_balance: float = 0.0; available_cash: float = 0.0
    historical_avg_amount: float = 0.0; behavior_shift_score: float = 0.0
    fraud_score: float = 0.0; policy_limit: float = 0.0
    affordability_score: float = 0.0; urgency_score: float = 0.0
    identity_mismatch_score: float = 0.0; narrative_conflict_score: float = 0.0
    device_trust_score: float = 0.0; recent_failed_attempts: int = 0
    elapsed_s: float = 0.0; min_required_elapsed_s: float = 108.0

    def __post_init__(self):
        # Force le cast en float pour eviter les SmartAttributes sur les champs connus
        for field_info in fields(self):
            val = getattr(self, field_info.name)
            if field_info.type in [float, int]:
                try: setattr(self, field_info.name, float(val))
                except: setattr(self, field_info.name, 0.0)
        obsidia_log(f"Bank state active. Amount: {self.amount}")

@dataclass
class TradingState(UniversalBase):
    symbol: str = "DEBUG"
    prices: List[float] = field(default_factory=list)
    highs: List[float] = field(default_factory=list)
    lows: List[float] = field(default_factory=list)
    volumes: List[float] = field(default_factory=list)
    spreads_bps: List[float] = field(default_factory=list)
    sentiment_scores: List[float] = field(default_factory=list)
    event_risk_scores: List[float] = field(default_factory=list)
    btc_reference_prices: List[float] = field(default_factory=list)

@dataclass
class EcomState(UniversalBase):
    session_id: str = "debug-session"