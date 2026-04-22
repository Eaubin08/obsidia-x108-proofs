#!/usr/bin/env python3
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sigma.obsidia_sigma_v130 import ObsidiaSigmaMonitor

def main():
    monitor = ObsidiaSigmaMonitor(config_path=str(ROOT / "sigma" / "sigma_config.json"))
    monitor.evaluate_step("S1", ["smoke_risk"], [])
    report = monitor.export_to_proofkit()["V18_9_sigma_stability"]

    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print("Sigma monitor public")
        print(f"status           : {report['status']}")
        print(f"steps_evaluated  : {report['steps_evaluated']}")
        print(f"violations_total : {report['violations_total']}")

if __name__ == "__main__":
    main()