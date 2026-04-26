from dataclasses import dataclass, field, fields
from typing import Optional, List, Dict, Any
from enum import IntEnum, Enum
import sys

def obsidia_log(msg):
     print(f"🔍 [KERNEL_TRACE] {msg}", file=sys.stderr)

class Layer(IntEnum):
     OBSERVATION = 1; INTERPRETATION = 2; CONTRADICTION = 3; SIGMA = 5; KERNEL = 6

class Severity(IntEnum): S0 = 0; S1 = 1; S2 = 2; S3 = 3

class Domain(Enum):
     BANK = "bank"; TRADING = "trading"; ECOM = "ecom"; GPS_DEFENSE_AVIATION = "gps_defense_aviation"

class X108Gate(Enum): ALLOW = "ALLOW"; HOLD = "HOLD"; BLOCK = "BLOCK"

class UniversalBase:
     def __init__(self, *args, **kwargs):
         f_names = [f.name for f in fields(self)]
         for i, val in enumerate(args):
             if i < len(f_names): setattr(self, f_names[i], val)
         for k, v in kwargs.items(): setattr(self, k, v)

# --- LE MOULE BANQUE COMPLET ---
@dataclass
class BankState(UniversalBase):
    amount: float = 0.0
    account_balance: float = 0.0
    affordability_score: float = 0.0
    available_cash: float = 0.0
    behavior_shift_score: float = 0.0
    channel: str = ""
    counterparty_age_days: int = 0
    counterparty_known: bool = False
    device_trust_score: float = 0.0
    fraud_score: float = 0.0
    historical_avg_amount: float = 0.0
    identity_mismatch_score: float = 0.0
    narrative_conflict_score: float = 0.0
    policy_limit: float = 0.0
    transaction_type: str = ""
    urgency_score: float = 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        obsidia_log(f"Bank State Initialized: {self.amount} EUR")

@dataclass
class GpsDefenseAviationState(UniversalBase):
     mission_id: str = "UNKNOWN"
     def __init__(self, *args, **kwargs):
         super().__init__(*args, **kwargs)
         obsidia_log(f"Aviation State Initialized: {self.mission_id}")

@dataclass
class TradingState(UniversalBase):
     def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)
@dataclass
class EcomState(UniversalBase):
     def __init__(self, *args, **kwargs): super().__init__(*args, **kwargs)
@dataclass
class AgentVote(UniversalBase):
     agent_id: str = ""; vote: str = "HOLD"; confidence: float = 0.0; domain: str = "unknown"
@dataclass
class DomainAggregate(UniversalBase):
     domain: str = "unknown"; confidence: float = 0.0
@dataclass
class CanonicalDecisionEnvelope(UniversalBase):
     x108_gate: str = "HOLD"
