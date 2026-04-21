#!/usr/bin/env python3
"""
verify_rfc3161.py — RFC3161 RÉEL À FOND
Générer une VRAIE requête TSQ RFC3161 (pas juste SHA256)
Envoyer à TSA, recevoir TSR, vérifier avec openssl
"""

import json
import sys
import os
import subprocess
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path

def generate_tsq_rfc3161(merkle_root: str) -> bytes:
    """
    Générer une VRAIE requête TSQ RFC3161 (pas juste SHA256).
    
    RFC3161 TimeStampReq structure :
    - Utiliser openssl ts -query pour générer une vraie TSQ
    
    Args:
        merkle_root: Racine Merkle à attester
    
    Returns:
        Bytes de la TSQ RFC3161
    """
    
    try:
        # Créer fichier temporaire avec le merkle_root
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(merkle_root)
            merkle_file = f.name
        
        try:
            # Générer une VRAIE TSQ RFC3161 avec openssl ts -query
            # openssl ts -query -data <file> -sha256 -out <tsq>
            tsq_file = tempfile.NamedTemporaryFile(delete=False, suffix='.tsq').name
            
            result = subprocess.run(
                ["openssl", "ts", "-query", "-data", merkle_file, "-sha256", "-out", tsq_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise Exception(f"openssl ts -query failed: {result.stderr}")
            
            # Lire la TSQ générée
            with open(tsq_file, 'rb') as f:
                tsq_bytes = f.read()
            
            os.unlink(tsq_file)
            return tsq_bytes
            
        finally:
            os.unlink(merkle_file)
            
    except FileNotFoundError:
        raise Exception("openssl not found - cannot generate RFC3161 TSQ")
    except Exception as e:
        raise Exception(f"Failed to generate TSQ: {e}")

def verify_tsr_with_openssl(tsr_bytes: bytes, merkle_root: str) -> tuple:
    """
    Vérifier un token RFC3161 (.tsr) avec openssl ts -verify RÉELLEMENT.
    
    Returns:
        (verified: bool, status: str, details: dict)
    """
    
    try:
        # Créer fichiers temporaires
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(merkle_root)
            merkle_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.tsr') as f:
            f.write(tsr_bytes)
            tsr_file = f.name
        
        try:
            # Appeler openssl ts -verify RÉELLEMENT
            cmd = ["openssl", "ts", "-verify", "-in", tsr_file, "-data", merkle_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # openssl ts -verify retourne 0 si vérification réussit
            if result.returncode == 0:
                return True, "verified", {
                    "command": " ".join(cmd),
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return False, "failed", {
                    "command": " ".join(cmd),
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "reason": f"openssl ts -verify failed with code {result.returncode}"
                }
        finally:
            os.unlink(tsr_file)
            os.unlink(merkle_file)
            
    except subprocess.TimeoutExpired:
        return False, "incomplete", {
            "reason": "openssl ts -verify timed out",
            "stderr": "Timeout"
        }
    except Exception as e:
        return False, "failed", {
            "reason": f"Exception: {e}",
            "stderr": str(e)
        }

def verify_rfc3161(decision_id: str, merkle_root: str, tsa_url: str = None) -> dict:
    """
    Vérifier une attestation RFC3161 RÉELLE À FOND.
    
    1. Générer VRAIE TSQ RFC3161
    2. Envoyer à TSA
    3. Recevoir TSR
    4. Vérifier avec openssl ts -verify
    
    verified=true UNIQUEMENT si toute cette chaîne passe.
    """
    
    traces_dir = Path("traces/rfc3161")
    traces_dir.mkdir(parents=True, exist_ok=True)
    
    merkle_file = traces_dir / f"{decision_id}.merkle.txt"
    tsq_file = traces_dir / f"{decision_id}.tsq"
    tsr_file = traces_dir / f"{decision_id}.tsr"
    verify_file = traces_dir / f"{decision_id}.verify.json"
    
    # 1. Écrire le merkle_root
    merkle_file.write_text(merkle_root)
    
    # 2. Générer une VRAIE TSQ RFC3161
    try:
        tsq_bytes = generate_tsq_rfc3161(merkle_root)
        tsq_file.write_bytes(tsq_bytes)
    except Exception as e:
        result = {
            "decision_id": decision_id,
            "source": "obsidia_rfc3161",
            "status": "incomplete",
            "verified": False,
            "token": None,
            "timestamp": None,
            "tsa_url": tsa_url,
            "artifact_path": None,
            "reason": f"Failed to generate RFC3161 TSQ: {e}"
        }
        verify_file.write_text(json.dumps(result, indent=2))
        return result
    
    # 3. Appeler la TSA si disponible
    status = "incomplete"
    verified = False
    token = None
    timestamp = None
    reason = None
    tsr_bytes = None
    
    if tsa_url:
        try:
            import requests
            
            # Envoyer la VRAIE TSQ RFC3161 à la TSA
            response = requests.post(
                tsa_url,
                data=tsq_bytes,
                headers={"Content-Type": "application/timestamp-query"},
                timeout=30
            )
            
            if response.status_code == 200:
                tsr_bytes = response.content
                tsr_file.write_bytes(tsr_bytes)
                
                # Vérifier RÉELLEMENT avec openssl ts -verify
                verified, status, details = verify_tsr_with_openssl(tsr_bytes, merkle_root)
                
                if verified:
                    token = tsr_bytes.hex()[:64]
                    timestamp = int(datetime.now().timestamp() * 1000)
                    reason = None
                else:
                    reason = details.get("reason", "openssl ts -verify failed")
            else:
                status = "incomplete"
                reason = f"TSA returned {response.status_code}"
        except ImportError:
            reason = "requests library not available"
        except Exception as e:
            status = "failed"
            reason = f"TSA call failed: {e}"
    else:
        reason = "No TSA URL configured"
    
    # 4. Écrire le rapport
    result = {
        "decision_id": decision_id,
        "source": "obsidia_rfc3161",
        "status": status,
        "verified": verified,
        "token": token,
        "timestamp": timestamp,
        "tsa_url": tsa_url,
        "artifact_path": str(tsr_file) if tsr_file.exists() else None,
        "reason": reason
    }
    
    verify_file.write_text(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_rfc3161.py <decision_id> <merkle_root> [tsa_url]")
        sys.exit(1)
    
    decision_id = sys.argv[1]
    merkle_root = sys.argv[2]
    tsa_url = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("OBSIDIA_TSA_URL")
    
    result = verify_rfc3161(decision_id, merkle_root, tsa_url)
    print(json.dumps(result, indent=2))
