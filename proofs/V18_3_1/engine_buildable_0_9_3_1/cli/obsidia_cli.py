from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from unified_interface.pipeline import run as unified_run
from obsidia_kernel.contract import result_to_dict

def _read_json(path: str | None) -> Dict[str, Any]:
    if path is None or path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def cmd_decision(args) -> int:
    payload = _read_json(args.input)
    res = unified_run(payload)
    out = result_to_dict(res)
    print(json.dumps(out, indent=2))
    return 0

def cmd_replay(args) -> int:
    import os
    store_dir = args.store_dir
    path = os.path.join(store_dir, f"{args.trace_id}.json")
    if not os.path.exists(path):
        print("trace_id not found", file=sys.stderr)
        return 2
    with open(path, "r", encoding="utf-8") as f:
        print(f.read())
    return 0

def main() -> int:
    p = argparse.ArgumentParser(prog="obsidia")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decision", help="Run decision gateway on an input JSON request.")
    d.add_argument("input", nargs="?", default="-", help="Path to JSON file, or '-' for stdin.")
    d.set_defaults(fn=cmd_decision)

    r = sub.add_parser("replay", help="Read stored trace by trace_id (from api_store).")
    r.add_argument("trace_id")
    r.add_argument("--store-dir", default="api_store")
    r.set_defaults(fn=cmd_replay)

    args = p.parse_args()
    return args.fn(args)

if __name__ == "__main__":
    raise SystemExit(main())
