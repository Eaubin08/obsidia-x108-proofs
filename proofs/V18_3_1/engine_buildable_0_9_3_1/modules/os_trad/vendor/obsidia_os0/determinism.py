from __future__ import annotations
import json, hashlib
from dataclasses import is_dataclass, asdict
from typing import Any

def _to_primitive(x: Any):
    if is_dataclass(x):
        return {"__type__": x.__class__.__name__, **{k:_to_primitive(v) for k,v in asdict(x).items()}}
    if isinstance(x, (list, tuple)):
        return [_to_primitive(i) for i in x]
    if isinstance(x, dict):
        return {str(k): _to_primitive(v) for k,v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (str,int,float,bool)) or x is None:
        return x
    return {"__repr__": repr(x)}

def canonical_hash(ir_program: Any) -> str:
    prim=_to_primitive(ir_program)
    blob=json.dumps(prim, ensure_ascii=False, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
