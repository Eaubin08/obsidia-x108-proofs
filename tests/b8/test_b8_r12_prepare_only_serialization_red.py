import pytest
from types import MappingProxyType
from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from app.knowledge.b8.serialization import _check_json, api_projection

class DummyEnum(Enum):
    A = "A_VALUE"

@dataclass
class DummyDataclass:
    field1: str
    field2: int

def test_r12_reproduce_mappingproxy_serialization_fails():
    # R12: prepare-only path object
    obj = {
        "candidate_refs": MappingProxyType({"a": 1}),
        "items": (1, 2),
        "tags": frozenset(["tag1"]),
        "status": DummyEnum.A,
        "path": Path("/some/path"),
        "meta": DummyDataclass(field1="foo", field2=42)
    }
    
    with pytest.raises(ValueError, match="non-JSON value of type mappingproxy"):
        _check_json(obj, "$", set())
        
    projected = api_projection(obj)
    
    # Should not raise
    _check_json(projected, "$", set())
    
    # Verify exact structure
    assert projected == {
        "candidate_refs": {"a": 1},
        "items": [1, 2],
        "tags": ["tag1"],
        "status": "A_VALUE",
        "path": "/some/path" if str(Path("/some/path")) == "/some/path" else str(Path("/some/path")),
        "meta": {"field1": "foo", "field2": 42}
    }
