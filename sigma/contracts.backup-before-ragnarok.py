from dataclasses import dataclass, field, fields
from typing import Optional, List, Dict, Any, Tuple
from enum import IntEnum, Enum
import sys

# --- FONCTION DE LOG INTERNE ---
def obsidia_log(msg):
    print(f"🔍 [KERNEL_TRACE] {msg}", file=sys.stderr)

# --- 1. ENUMS ---
class Layer(IntEnum):
    OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; PERIPHERAL = 4
    SIGMA = 5; KERNEL = 6; PROOF = 7; SCELLAGE = 8

class Severity(IntEnum):
    S0 = 0; S1 = 1; S2 = 2; S3 = 3; S4 = 4

class Domain(Enum):
    BANK = "bank"; TRADING = "trading"; ECOM = "ecom"
    GPS_DEFENSE_AVIATION = "gps_defense_aviation"; META = "meta"

class SourceTag(Enum):
    CANONICAL = "canonical"
    CANONICAL_FRAMEWORK = "canonical_framework"
    SIGMA = "sigma"
    SIGMA_FRAMEWORK = "sigma_framework"
    KERNEL = "kernel"
    KERNEL_FRAMEWORK = "kernel_framework"

class X108Gate(Enum):
    ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"

# --- 2. L'ATTRIBUT UNIVERSEL (SmartAttribute) ---
class SmartAttribute(list):
    def __init__(self, name, default_val=0.0):
        super().__init__()
        self.name = name
        self.internal_val = default_val

    def __str__(self): return str(self.internal_val) if not self else super().__repr__()
    def __hash__(self): return hash(str(self.internal_val))

    def _to_num(self):
        try: return float(self.internal_val) if self.internal_val else 0.0
        except: return 0.0

    def __ge__(self, other): return self._to_num() >= float(other)
    def __gt__(self, other): return self._to_num() > float(other)
    def __le__(self, other): return self._to_num() <= float(other)
    def __lt__(self, other): return self._to_num() < float(other)
    def __add__(self, other): return self._to_num() + float(other)
    def __radd__(self, other): return float(other) + self._to_num()
    def __sub__(self, other): return self._to_num() - float(other)
    def __rsub__(self, other): return float(other) - self._to_num()
    def __mul__(self, other): return self._to_num() * float(other)
    def __rmul__(self, other): return float(other) * self._to_num()

# --- 3. BASE UNIVERSELLE AVEC TRAPS ---
class UniversalBase:
    def __init__(self, *args, **kwargs):
        class_name = self.__class__.__name__
        f_names = [f.name for f in fields(self)]

        # Log de création
        obsidia_log(f"Instantiating {class_name}...")

        for i, val in enumerate(args):
            if i < len(f_names):
                setattr(self, f_names[i], val)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, name):
        # Log des accès dynamiques (ceux qui n'existent pas)
        obsidia_log(f"Dynamic access on {self.__class__.__name__}: '{name}'")
        new_attr = SmartAttribute(name)
        setattr(self, name, new_attr)
        return new_attr

# --- 4. STRUCTURES DE VOTE ---
@dataclass
class AgentVote(UniversalBase):
    agent_id: str = "A1_MEM"
    vote: str = "HOLD"
    proposed_verdict: str = "HOLD"
    confidence: float = 0.0
    domain: str = "unknown"
    layer: int = 5
    claim: str = "no_claim"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "confidence"):
            try: self.confidence = float(self.confidence)
            except: self.confidence = 0.0

@dataclass
class DomainAggregate(UniversalBase):
    domain: str = "unknown"
    agent_votes: List[AgentVote] = field(default_factory=list)
    confidence: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obsidia_log(f"Aggregating {len(getattr(self, 'agent_votes', []))} votes for {self.domain}")
        v = getattr(self, "agent_votes", [])
        if isinstance(v, list):
            self.agent_votes = [AgentVote(**item) if isinstance(item, dict) else item for item in v]

# --- 5. ÉTATS SATELLITES ---
@dataclass
class GpsDefenseAviationState(UniversalBase):
    mission_id: str = "UNKNOWN"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obsidia_log(f"Aviation Cockpit initialized: {self.mission_id}")

@dataclass
class CanonicalDecisionEnvelope(UniversalBase):
    x108_gate: str = "HOLD"
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)

@dataclass
class BankState(UniversalBase):
    amount: float = 0.0
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obsidia_log(f"Bank state active. Amount: {self.amount}")

@dataclass
class TradingState(UniversalBase):
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)

@dataclass
class EcomState(UniversalBase):
    def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)
