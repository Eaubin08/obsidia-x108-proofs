"""Minimal runtime assembly (A+B+C) based on XLS-derived registry."""

from __future__ import annotations
from typing import Any, Dict, Optional
from obsidia_registry import load_minimal_registry

def assemble_minimal_engine(registry_path: Optional[str] = None) -> Dict[str, Any]:
    reg = load_minimal_registry(registry_path)
    return {
        "pivot_agents": reg.pivot_agents,
        "domaines_vrais": reg.domaines_vrais,
        "domaines_archi_cognitive": reg.domaines_archi_cognitive,
    }

def main():
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument("--registry", default=None, help="Path to minimal registry json")
    args = p.parse_args()
    e = assemble_minimal_engine(args.registry)
    print(json.dumps({
        "pivot_agents": len(e["pivot_agents"]),
        "domaines_vrais": len(e["domaines_vrais"]),
        "domaines_archi_cognitive": len(e["domaines_archi_cognitive"]),
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()


# --- Cortex Injection (D) ---
def load_cortex_from_registry(registry_path=None):
    import json, os
    if registry_path is None:
        for root, dirs, files in os.walk('.'):
            if 'minimal_engine_registry_from_xls.json' in files:
                registry_path = os.path.join(root, 'minimal_engine_registry_from_xls.json')
                break
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('cortex_detected', [])
