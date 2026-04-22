from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Dict, Union, Callable

# ===== L2 Alphabet (12 symbols) =====

@dataclass(frozen=True)
class VALUE:
    v: Any

@dataclass(frozen=True)
class STATE:
    name: str

@dataclass(frozen=True)
class READ:
    state: STATE

@dataclass(frozen=True)
class WRITE:
    state: STATE
    value: Any  # VALUE or expression result

@dataclass(frozen=True)
class FLOW:
    steps: List[Any]  # list of IR nodes

@dataclass(frozen=True)
class COND:
    expr: Any  # callable(env)->bool OR tuple-based expression

@dataclass(frozen=True)
class LOOP:
    cond: COND
    body: List[Any]
    max_iters: int = 10_000

@dataclass(frozen=True)
class CALL:
    fn: str
    args: List[Any]

@dataclass(frozen=True)
class RETURN:
    value: Any

@dataclass(frozen=True)
class EVENT:
    name: str
    payload: Any = None
    t: Optional[int] = None  # optional timestamp (int)

@dataclass(frozen=True)
class TIME:
    t: int

@dataclass(frozen=True)
class ERROR(Exception):
    message: str
    code: str = "ERROR"
