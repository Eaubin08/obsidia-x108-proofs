from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agents.orchestrator_readonly import run_readonly_swarm


def main() -> int:
    parser = argparse.ArgumentParser(description="Obsidia Workflow Governance Primitive V3")
    parser.add_argument("--sop", required=True, help="Path to SOP text file")
    parser.add_argument("--title", default="Untitled workflow", help="Workflow title")
    parser.add_argument("--out", default="", help="Optional output JSON path")
    args = parser.parse_args()

    sop_text = Path(args.sop).read_text(encoding="utf-8")
    result = run_readonly_swarm(sop_text=sop_text, title=args.title)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
