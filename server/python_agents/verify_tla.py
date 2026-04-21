#!/usr/bin/env python3
"""
verify_tla.py — TLA FORT À FOND
Vérifier que la spec DÉPEND RÉELLEMENT des constantes injectées
Pas juste "noms dans stdout"
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def verify_tla_real(decision_id: str, trace_path: str, vars_path: str, target: str) -> tuple:
    """
    Vérifier RÉELLEMENT que la spec DÉPEND des constantes injectées.
    
    Stratégie :
    1. Vérifier que TLC existe
    2. Vérifier que la spec existe
    3. Lire trace.json et vars.json
    4. Créer deux configs TLC :
       a) Config 1 : AVEC l'instance (DECISION_TRACE, DECISION_VARS)
       b) Config 2 : SANS l'instance (constantes vides ou par défaut)
    5. Lancer TLC avec les deux configs
    6. Comparer les résultats :
       - Si Config 1 réussit ET Config 2 échoue → spec DÉPEND de l'instance
       - Si Config 1 échoue ET Config 2 échoue → spec ne consomme pas l'instance
       - Si Config 1 réussit ET Config 2 réussit → spec ne dépend pas de l'instance
    
    Returns:
        (verified: bool, status: str, details: dict)
    """
    
    # Vérifier que TLC existe
    tlc_cmd = None
    for candidate in ["tlc", "java -cp /opt/tla/tla2tools.jar tlc2.TLC"]:
        try:
            cmd_to_test = candidate.split()[0] if candidate.startswith("tlc") else candidate.split()[0]
            result_test = subprocess.run(
                [cmd_to_test, "--version"],
                capture_output=True,
                timeout=5
            )
            if result_test.returncode == 0 or result_test.returncode == 1:
                tlc_cmd = candidate
                break
        except:
            pass
    
    if not tlc_cmd:
        return False, "incomplete", {
            "reason": "TLC not found",
            "stderr": "TLC model checker not found in PATH"
        }
    
    # Lire trace et vars pour vérifier qu'ils sont valides
    try:
        trace_data = json.loads(Path(trace_path).read_text())
        vars_data = json.loads(Path(vars_path).read_text())
    except Exception as e:
        return False, "failed", {
            "reason": f"Invalid JSON: {e}",
            "stderr": str(e)
        }
    
    # Vérifier que la spec existe
    spec_path = Path("formal/tla") / target
    if not spec_path.exists():
        return False, "incomplete", {
            "reason": f"Spec not found: {target}",
            "stderr": f"{spec_path} does not exist"
        }
    
    # Créer deux configs TLC pour tester la dépendance
    try:
        traces_dir = Path(f"traces/tla/{decision_id}")
        traces_dir.mkdir(parents=True, exist_ok=True)
        
        # Config 1 : AVEC l'instance
        config_with_instance = f"""
SPECIFICATION Spec
CONSTANT decision_id = "{decision_id}"
CONSTANT DECISION_TRACE = {json.dumps(trace_data)}
CONSTANT DECISION_VARS = {json.dumps(vars_data)}
"""
        
        # Config 2 : SANS l'instance (constantes vides/par défaut)
        config_without_instance = f"""
SPECIFICATION Spec
CONSTANT decision_id = "{decision_id}"
CONSTANT DECISION_TRACE = {{}}
CONSTANT DECISION_VARS = {{}}
"""
        
        cfg_file = target.replace('.tla', '.cfg')
        
        # Lancer TLC avec Config 1 (AVEC instance)
        config_with_file = traces_dir / f"{cfg_file}.with"
        config_with_file.write_text(config_with_instance)
        
        cmd_with = f"{tlc_cmd} -config {config_with_file} {target}"
        
        result_with = subprocess.run(
            cmd_with,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="formal/tla"
        )
        
        # Lancer TLC avec Config 2 (SANS instance)
        config_without_file = traces_dir / f"{cfg_file}.without"
        config_without_file.write_text(config_without_instance)
        
        cmd_without = f"{tlc_cmd} -config {config_without_file} {target}"
        
        result_without = subprocess.run(
            cmd_without,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd="formal/tla"
        )
        
        # Analyser les résultats pour déterminer si la spec DÉPEND de l'instance
        with_success = result_with.returncode == 0
        without_success = result_without.returncode == 0
        
        # Cas 1 : Config 1 réussit ET Config 2 échoue → spec DÉPEND de l'instance ✅
        if with_success and not without_success:
            return True, "verified", {
                "reason": "Spec DEPENDS on instance: Config WITH instance passed, Config WITHOUT instance failed",
                "with_returncode": result_with.returncode,
                "without_returncode": result_without.returncode,
                "with_stdout": result_with.stdout,
                "without_stdout": result_without.stdout,
                "with_stderr": result_with.stderr,
                "without_stderr": result_without.stderr,
                "command_with": cmd_with,
                "command_without": cmd_without
            }
        
        # Cas 2 : Config 1 échoue → spec ne peut pas être vérifiée
        elif not with_success:
            return False, "failed", {
                "reason": "Spec verification failed even WITH instance",
                "with_returncode": result_with.returncode,
                "with_stderr": result_with.stderr,
                "command_with": cmd_with
            }
        
        # Cas 3 : Config 1 réussit ET Config 2 réussit → spec ne dépend pas de l'instance
        else:
            return False, "failed", {
                "reason": "Spec does NOT depend on instance: both configs passed",
                "with_returncode": result_with.returncode,
                "without_returncode": result_without.returncode,
                "command_with": cmd_with,
                "command_without": cmd_without
            }
            
    except subprocess.TimeoutExpired:
        return False, "incomplete", {
            "reason": "TLC verification timed out",
            "stderr": "Timeout"
        }
    except Exception as e:
        return False, "failed", {
            "reason": f"Exception: {e}",
            "stderr": str(e)
        }

def verify_tla(decision_id: str, trace_path: str, vars_path: str, target: str = "X108.tla") -> dict:
    """
    Vérifier une trace TLA FORT À FOND.
    
    La spec doit DÉPENDRE RÉELLEMENT des constantes injectées.
    """
    
    traces_dir = Path(f"traces/tla/{decision_id}")
    traces_dir.mkdir(parents=True, exist_ok=True)
    
    stdout_path = traces_dir / "tlc.stdout.log"
    stderr_path = traces_dir / "tlc.stderr.log"
    verify_file = traces_dir / "tla_verify.json"
    
    # Vérifier que les fichiers d'entrée existent
    trace_path_obj = Path(trace_path)
    vars_path_obj = Path(vars_path)
    
    if not trace_path_obj.exists():
        result = {
            "decision_id": decision_id,
            "target": target,
            "status": "incomplete",
            "verified": False,
            "trace_path": trace_path,
            "vars_path": vars_path,
            "reason": "Trace file not found"
        }
        verify_file.write_text(json.dumps(result, indent=2))
        return result
    
    if not vars_path_obj.exists():
        result = {
            "decision_id": decision_id,
            "target": target,
            "status": "incomplete",
            "verified": False,
            "trace_path": trace_path,
            "vars_path": vars_path,
            "reason": "Vars file not found"
        }
        verify_file.write_text(json.dumps(result, indent=2))
        return result
    
    # Vérifier RÉELLEMENT que la spec DÉPEND de l'instance
    verified, status, details = verify_tla_real(decision_id, trace_path, vars_path, target)
    
    stdout_path.write_text(details.get("with_stdout", details.get("stdout", "")))
    stderr_path.write_text(details.get("with_stderr", details.get("stderr", "")))
    
    result = {
        "decision_id": decision_id,
        "target": target,
        "status": status,
        "verified": verified,
        "trace_path": trace_path,
        "vars_path": vars_path,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "reason": details.get("reason"),
        "dependency_test": {
            "with_instance_returncode": details.get("with_returncode"),
            "without_instance_returncode": details.get("without_returncode"),
            "spec_depends_on_instance": verified
        }
    }
    
    verify_file.write_text(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_tla.py <decision_id> <trace_path> <vars_path> [target]")
        sys.exit(1)
    
    decision_id = sys.argv[1]
    trace_path = sys.argv[2]
    vars_path = sys.argv[3]
    target = sys.argv[4] if len(sys.argv) > 4 else "X108.tla"
    
    result = verify_tla(decision_id, trace_path, vars_path, target)
    print(json.dumps(result, indent=2))
