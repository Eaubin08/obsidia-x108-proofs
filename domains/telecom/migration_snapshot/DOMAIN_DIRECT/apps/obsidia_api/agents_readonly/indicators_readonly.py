"""
apps/obsidia_api/agents_readonly/indicators_readonly.py

P73 — Indicators Readonly Adapter
Wrapper readonly des indicateurs de sigma/utils/indicators.py.
Expose les fonctions mathematiques pures sans importer sigma directement.

Source originale : agents/utils/indicators.py (identique a sigma/utils/indicators.py)
Categorie P73 : DO_NOT_IMPORT_DUPLICATE — indicateurs identiques dans sigma.
Wrapper cree pour usage API layer sans couplage direct a sigma/.

BOUNDARY P73 :
DRY_RUN_ONLY = True
READONLY = True
DECISION_AUTHORITY = "KX108_ONLY"
EMITS_ACT = False
EMITS_VERDICT = False
MEMORY_WRITE = False
GRAPHITI_WRITE = False
NEO4J_WRITE = False
KERNEL_MUTATION = False
SIGMA_OVERRIDE = False
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Iterable, Optional

DRY_RUN_ONLY: bool = True
READONLY: bool = True
DECISION_AUTHORITY: str = "KX108_ONLY"
EMITS_ACT: bool = False
EMITS_VERDICT: bool = False
MEMORY_WRITE: bool = False
GRAPHITI_WRITE: bool = False
NEO4J_WRITE: bool = False
KERNEL_MUTATION: bool = False
SIGMA_OVERRIDE: bool = False


def sma(values: Iterable[float], period: int) -> Optional[float]:
    values = list(values)
    if len(values) < period or period <= 0:
        return None
    return sum(values[-period:]) / period


def ema(values: Iterable[float], period: int) -> Optional[float]:
    values = list(values)
    if len(values) < period or period <= 0:
        return None
    k = 2 / (period + 1)
    out = values[0]
    for v in values[1:]:
        out = v * k + out * (1 - k)
    return out


def rsi(values: Iterable[float], period: int = 14) -> Optional[float]:
    prices = list(values)
    if len(prices) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(-period, 0):
        delta = prices[i] - prices[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def zscore(values: Iterable[float], period: int = 20) -> Optional[float]:
    prices = list(values)
    if len(prices) < period:
        return None
    window = prices[-period:]
    m = mean(window)
    std = pstdev(window)
    if std == 0:
        return 0.0
    return (window[-1] - m) / std


def realized_volatility(values: Iterable[float], period: int = 20) -> Optional[float]:
    prices = list(values)
    if len(prices) < period + 1:
        return None
    rets = []
    for i in range(-period, 0):
        prev = prices[i - 1]
        if prev == 0:
            continue
        rets.append((prices[i] - prev) / prev)
    if len(rets) < 2:
        return None
    return pstdev(rets)


def bollinger(values: Iterable[float], period: int = 20, mult: float = 2.0):
    prices = list(values)
    if len(prices) < period:
        return None, None, None
    window = prices[-period:]
    mid = sum(window) / period
    std = pstdev(window)
    return mid - mult * std, mid, mid + mult * std
