#!/usr/bin/env python3
"""
PHASE 2 — TLC RÉELLE
TLA passe en verified pour de vrai

Sortie :
- TLC détecté et exécuté
- X108.tla exécuté
- ObsidiaDistX108A12.tla exécuté (si applicable)
- rapport canonique
- verify.json

verified=true UNIQUEMENT si TLC passe
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timezone

def detect_tlc() -> dict:
    """Détecter TLC dans l'environnement"""
    
    # Chercher tlc.jar
    tlc_paths = [
        '/usr/local/bin/tlc',
        '/usr/bin/tlc',
        os.path.expanduser('~/.local/bin/tlc'),
        '/opt/tla/tlc.jar'
    ]
    
    for path in tlc_paths:
        if os.path.exists(path):
            return {
                "detected": True,
                "path": path,
                "type": "jar" if path.endswith('.jar') else "executable"
            }
    
    # Chercher dans PATH
    result = subprocess.run(['which', 'tlc'], capture_output=True, text=True)
    if result.returncode == 0:
        return {
            "detected": True,
            "path": result.stdout.strip(),
            "type": "executable"
        }
    
    return {
        "detected": False,
        "path": None,
        "type": None,
        "message": "TLC not found in PATH or standard locations"
    }

def run_tlc_on_spec(spec_file: str, output_dir: str) -> dict:
    """Exécuter TLC sur une spec TLA+"""
    
    spec_name = Path(spec_file).stem
    spec_log = os.path.join(output_dir, f"{spec_name}_tlc.log")
    
    # Déterminer la commande TLC
    tlc_detection = detect_tlc()
    
    if not tlc_detection["detected"]:
        return {
            "spec": spec_name,
            "verified": False,
            "status": "incomplete",
            "reason": "TLC not detected",
            "log": None
        }
    
    # Préparer commande TLC
    if tlc_detection["type"] == "jar":
        cmd = ['java', '-jar', tlc_detection["path"], spec_file]
    else:
        cmd = [tlc_detection["path"], spec_file]
    
    # Exécuter TLC
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=output_dir)
    
    # Écrire log
    with open(spec_log, 'w') as f:
        f.write(f"=== TLC EXECUTION ===\n")
        f.write(f"Spec: {spec_file}\n")
        f.write(f"Command: {' '.join(cmd)}\n")
        f.write(f"Return code: {result.returncode}\n")
        f.write(f"\nStdout:\n{result.stdout}\n")
        f.write(f"\nStderr:\n{result.stderr}\n")
    
    # Déterminer verified
    verified = result.returncode == 0
    
    return {
        "spec": spec_name,
        "verified": verified,
        "status": "verified" if verified else "failed",
        "return_code": result.returncode,
        "log": spec_log,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def phase2_tlc_real(decision_id: str, trace_path: str, vars_path: str, output_dir: str = None) -> dict:
    """Exécuter PHASE 2 — TLC réelle"""
    
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), f"traces/tla/{decision_id}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n=== PHASE 2 — TLC RÉELLE ===")
    print(f"Decision ID: {decision_id}")
    print(f"Trace path: {trace_path}")
    print(f"Vars path: {vars_path}")
    print(f"Output dir: {output_dir}")
    print()
    
    # 1. Détecter TLC
    tlc_detection = detect_tlc()
    print(f"TLC Detection: {tlc_detection['detected']}")
    if tlc_detection['detected']:
        print(f"  Path: {tlc_detection['path']}")
        print(f"  Type: {tlc_detection['type']}")
    else:
        print(f"  Reason: {tlc_detection['message']}")
    print()
    
    # 2. Vérifier que trace.json et vars.json existent
    if not os.path.exists(trace_path):
        print(f"❌ Trace file not found: {trace_path}")
        return {
            "decision_id": decision_id,
            "verified": False,
            "status": "failed",
            "reason": f"Trace file not found: {trace_path}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    if not os.path.exists(vars_path):
        print(f"❌ Vars file not found: {vars_path}")
        return {
            "decision_id": decision_id,
            "verified": False,
            "status": "failed",
            "reason": f"Vars file not found: {vars_path}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    print(f"✅ Trace file found: {trace_path}")
    print(f"✅ Vars file found: {vars_path}")
    print()
    
    # 3. Chercher specs TLA+
    spec_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'formal', 'tla')
    x108_spec = os.path.join(spec_dir, 'X108.tla')
    distributed_spec = os.path.join(spec_dir, 'ObsidiaDistX108A12.tla')
    
    results = []
    
    # 4. Exécuter TLC sur X108.tla
    if os.path.exists(x108_spec):
        print(f"Executing TLC on X108.tla...")
        result = run_tlc_on_spec(x108_spec, output_dir)
        results.append(result)
        print(f"  Result: {result['status']}")
    else:
        print(f"⚠️ X108.tla not found: {x108_spec}")
    
    # 5. Exécuter TLC sur ObsidiaDistX108A12.tla (si applicable)
    if os.path.exists(distributed_spec):
        print(f"Executing TLC on ObsidiaDistX108A12.tla...")
        result = run_tlc_on_spec(distributed_spec, output_dir)
        results.append(result)
        print(f"  Result: {result['status']}")
    
    print()
    
    # 6. Créer rapport canonique
    overall_verified = all(r.get('verified', False) for r in results) if results else False
    
    verify_json = {
        "decision_id": decision_id,
        "trace_path": trace_path,
        "vars_path": vars_path,
        "tlc_detected": tlc_detection['detected'],
        "tlc_path": tlc_detection.get('path'),
        "specs_executed": results,
        "verified": overall_verified,
        "status": "verified" if overall_verified else ("incomplete" if not tlc_detection['detected'] else "failed"),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    verify_json_file = os.path.join(output_dir, 'verify.json')
    with open(verify_json_file, 'w') as f:
        json.dump(verify_json, f, indent=2)
    
    print(f"✅ verify.json créé : {verify_json_file}")
    print()
    print(f"=== RÉSULTAT ===")
    print(f"verified: {overall_verified}")
    print(f"status: {verify_json['status']}")
    print()
    
    return verify_json

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: phase2_tlc_real.py <decision_id> <trace_path> <vars_path> [output_dir]")
        print("Example: phase2_tlc_real.py dec-123 /tmp/trace.json /tmp/vars.json /tmp/traces")
        sys.exit(1)
    
    decision_id = sys.argv[1]
    trace_path = sys.argv[2]
    vars_path = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else None
    
    result = phase2_tlc_real(decision_id, trace_path, vars_path, output_dir)
    print(json.dumps(result, indent=2))
