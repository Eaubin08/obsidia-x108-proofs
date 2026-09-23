"""Auto-load Graphiti/Neo4j env from .env.graphiti.local if not already set."""
import os
from pathlib import Path

_LOADED = False

def load_graphiti_env():
    global _LOADED
    if _LOADED: return
    if os.environ.get("NEO4J_PASSWORD"):
        _LOADED = True
        return
    candidates = [
        Path(__file__).resolve().parents[3] / "graphiti-lab" / ".env.graphiti.local",
    ]
    for fpath in candidates:
        if fpath.exists():
            with open(fpath, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip(); v = v.strip().strip('"').strip("'")
                        os.environ[k] = v
            _LOADED = True
            return
