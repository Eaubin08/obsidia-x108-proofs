#!/usr/bin/env python3
"""
OBSIDIA KX108 — AUDIT MERKLE V2 VERIFIER & BUILDER
===================================================
Outil de scellement et de vérification cryptographique indépendant
pour le périmètre KX108 P0 (Phases 1 à 7).

Gouvernance :
- Maintient l'étanchéité stricte avec le sceau historique (merkle_seal.json).
- Canonicalise les feuilles : SHA256(rel_path:sha256).
- Réduction binaire Merkle avec duplication sur cardinalité impaire.
- Chaînage d'ancre : SHA256(historical_root:v2_scope_root).
- Vérification bit-à-bit sans dépendance externe.
"""

import os
import sys
import json
import hashlib
import tempfile
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# ============================================================================
# 1. PÉRIMÈTRE CANONIQUE KX108 P0 (26 FICHIERS OFFICIELS)
# ============================================================================

CANONICAL_V2_SCOPE = [
    ".gitignore",
    "apps/obsidia_api/routes/blockchain.py",
    "periphery/sigma_bridge.py",
    "periphery/world_calls/sovereign_ticket.py",
    "periphery/world_calls/ticket_store.py",
    "scripts/obsidure_bounded_apply.py",
    "server.kernel.isolated.cjs",
    "server.kernel.sealed.cjs",
    "sigma/aggregation.py",
    "sigma/contracts.py",
    "sigma/domains/bank_agents.py",
    "sigma/domains/gps_defense_aviation_agents.py",
    "sigma/domains/meta_agents.py",
    "sigma/evaluate.py",
    "sigma/guard.py",
    "sigma/packets.py",
    "sigma/protocols.py",
    "sigma/registry.py",
    "sigma/run_pipeline.py",
    "sigma/tests/test_gps_semantics.py",
    "sigma/tests/test_kx108_authority_p0.py",
    "sigma/tests/test_kx108_node_concurrency.py",
    "sigma/tests/test_kx108_phase2c_reconciliation.py",
    "sigma/tests/test_kx108_pre_decision_write_safety.py",
    "sigma/tests/test_kx108_sovereign_ticket_security.py",
    "sigma/tooling/governed_bounded_apply.py",
]

# ============================================================================
# 2. PRIMITIVES CRYPTOGRAPHIQUES DÉTERMINISTES
# ============================================================================

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().lower()

def sha256_file(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest().lower()

def canonical_leaf_hash(rel_path: str, file_hash: str) -> str:
    norm_path = rel_path.replace("\\", "/").strip("/")
    raw = f"{norm_path}:{file_hash.lower()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest().lower()

def build_merkle_tree(leaf_hashes: list[str]) -> str:
    if not leaf_hashes:
        return sha256_bytes(b"")
    curr = list(leaf_hashes)
    while len(curr) > 1:
        if len(curr) % 2 != 0:
            curr.append(curr[-1])
        nxt = []
        for i in range(0, len(curr), 2):
            combined = (curr[i] + curr[i + 1]).encode("utf-8")
            nxt.append(hashlib.sha256(combined).hexdigest().lower())
        curr = nxt
    return curr[0]

def compute_chained_root(historical_anchor: str, v2_scope_root: str) -> str:
    raw = f"{historical_anchor}:{v2_scope_root}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest().lower()

def sanitize_path(rel_path: str, base_dir: Path) -> Path:
    norm = rel_path.replace("\\", "/").strip()
    if norm.startswith("/") or ".." in norm.split("/"):
        raise ValueError(f"Chemin dangereux ou traversal détecté : {rel_path}")
    target = (base_dir / norm).resolve()
    base_resolved = base_dir.resolve()
    if not str(target).startswith(str(base_resolved)):
        raise ValueError(f"Échappement de périmètre détecté : {rel_path}")
    return target

# ============================================================================
# 3. DIAGNOSTIC FORENSIQUE DE LA RACINE HISTORIQUE
# ============================================================================

def diagnose_historical_root(root_dir: Path) -> dict:
    historical_file = root_dir / "merkle_seal.json"
    if not historical_file.exists():
        return {
            "status": "MISSING",
            "error": "merkle_seal.json introuvable",
            "historical_root": None
        }
    try:
        raw_content = historical_file.read_text(encoding="utf-8-sig")
        data = json.loads(raw_content)
        root_val = data.get("root") or data.get("merkle_root")
        count_val = data.get("count") or data.get("total_proofs_count")
        
        is_hex = all(c in "0123456789abcdefABCDEF" for c in str(root_val))
        length = len(str(root_val))
        
        # Classification forensique
        if length == 64 and is_hex:
            nature = "FULL_SHA256_256BIT"
        elif length == 24 and is_hex:
            nature = "TRUNCATED_PREFIX_96BIT"
        else:
            nature = "NON_STANDARD_FORMAT"
            
        return {
            "status": "PRESENT",
            "raw_value": root_val,
            "length": length,
            "is_hex": is_hex,
            "nature": nature,
            "count": count_val,
            "seal_status": data.get("status"),
            "last_seal": data.get("last_seal") or data.get("audit_date"),
        }
    except Exception as e:
        return {
            "status": "CORRUPTED",
            "error": str(e),
            "historical_root": None
        }

# ============================================================================
# 4. GÉNÉRATION FORMELLE DU SCELLÉ MERKLE V2
# ============================================================================

def generate_v2_seal(root_dir: Path, output_file: Path) -> dict:
    diag = diagnose_historical_root(root_dir)
    if diag["status"] != "PRESENT":
        raise RuntimeError(f"Impossible de générer le sceau V2 : {diag.get('error')}")
    
    historical_anchor = str(diag["raw_value"])
    
    # 1. Vérification et hachage des 26 fichiers
    manifest_entries = []
    for rel_path in sorted(CANONICAL_V2_SCOPE):
        file_path = sanitize_path(rel_path, root_dir)
        if not file_path.exists():
            raise FileNotFoundError(f"Fichier canonique manquant du scope V2 : {rel_path}")
        f_hash = sha256_file(file_path)
        manifest_entries.append({
            "path": rel_path,
            "sha256": f_hash
        })
        
    # 2. Calcul des feuilles ordonnées
    leaf_hashes = [
        canonical_leaf_hash(entry["path"], entry["sha256"])
        for entry in manifest_entries
    ]
    
    # 3. Réduction de l'arbre Merkle V2
    v2_scope_root = build_merkle_tree(leaf_hashes)
    
    # 4. Chaînage avec la racine historique
    chained_v2_root = compute_chained_root(historical_anchor, v2_scope_root)
    
    # 5. Détection HEAD Git
    git_head = "UNKNOWN"
    try:
        proc = subprocess.run(
            ["git", "-C", str(root_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True
        )
        git_head = proc.stdout.strip()
    except Exception:
        pass
        
    now_utc = datetime.now(timezone.utc).isoformat()
    
    seal_doc = {
        "version": "obsidia.kx108.merkle_seal.v2",
        "status": "LOCAL_SEAL / EXTERNAL_TIMESTAMP_PENDING",
        "issued_at_utc": now_utc,
        "git_head": git_head,
        "algorithm": "SHA-256",
        "leaf_canonicalization": "path:sha256",
        "leaf_ordering": "lexicographical_ascii",
        "historical_anchor": {
            "root_value": historical_anchor,
            "nature": diag["nature"],
            "length_chars": diag["length"],
            "source_file": "merkle_seal.json",
            "historical_proofs_count": diag.get("count"),
            "historical_status": diag.get("seal_status")
        },
        "v2_scope": {
            "file_count": len(manifest_entries),
            "manifest": manifest_entries,
            "v2_scope_root": v2_scope_root
        },
        "chained_v2_root": chained_v2_root,
        "rfc3161": {
            "status": "PENDING_EXTERNAL_TSA",
            "token_present": False,
            "notes": "Aucun jeton TSA tiers n'a été inséré artificiellement. Attente d'ancrage externe officiel."
        }
    }
    
    output_file.write_text(json.dumps(seal_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return seal_doc

# ============================================================================
# 5. VÉRIFICATION INDÉPENDANTE STRICTE DU SCELLÉ V2
# ============================================================================

def verify_v2_seal(root_dir: Path, seal_file: Path, check_git: bool = True) -> tuple[bool, list[str], dict]:
    errors = []
    details = {}
    
    if not seal_file.exists():
        return False, [f"Sceau V2 introuvable : {seal_file}"], {}
        
    try:
        raw_seal = seal_file.read_text(encoding="utf-8")
        seal_doc = json.loads(raw_seal)
    except Exception as e:
        return False, [f"Sceau V2 JSON invalide ou tronqué : {e}"], {}
        
    # Vérification schéma et version
    if seal_doc.get("version") != "obsidia.kx108.merkle_seal.v2":
        errors.append(f"Version du sceau non reconnue : {seal_doc.get('version')}")
        
    declared_hist = seal_doc.get("historical_anchor", {}).get("root_value")
    diag_hist = diagnose_historical_root(root_dir)
    if diag_hist["status"] != "PRESENT":
        errors.append(f"Ancre historique absente ou altérée sur disque : {diag_hist.get('error')}")
    elif str(diag_hist["raw_value"]) != str(declared_hist):
        errors.append(
            f"Désynchronisation ancre historique : déclarée '{declared_hist}', disque '{diag_hist['raw_value']}'"
        )
        
    manifest = seal_doc.get("v2_scope", {}).get("manifest", [])
    if len(manifest) != len(CANONICAL_V2_SCOPE):
        errors.append(f"Nombre de fichiers dans le manifeste incorrect : {len(manifest)} au lieu de {len(CANONICAL_V2_SCOPE)}")
        
    declared_paths = [m.get("path") for m in manifest]
    if declared_paths != sorted(CANONICAL_V2_SCOPE):
        errors.append("Le manifeste ne respecte pas l'ordre lexicographique strict ou diverge du périmètre canonique")
        
    # Vérification bit-à-bit sur disque
    recomputed_leaves = []
    for item in manifest:
        rel_path = item.get("path")
        declared_hash = item.get("sha256", "").lower()
        try:
            target_file = sanitize_path(rel_path, root_dir)
            if not target_file.exists():
                errors.append(f"Fichier manquant sur disque : {rel_path}")
                continue
            actual_hash = sha256_file(target_file)
            if actual_hash != declared_hash:
                errors.append(f"Altération binaire sur {rel_path} : attendu '{declared_hash}', calculé '{actual_hash}'")
            recomputed_leaves.append(canonical_leaf_hash(rel_path, actual_hash))
        except Exception as e:
            errors.append(f"Erreur d'accès sur {rel_path} : {e}")
            
    # Recalcul sous-arbre V2
    recomputed_v2_root = build_merkle_tree(recomputed_leaves)
    declared_v2_root = seal_doc.get("v2_scope", {}).get("v2_scope_root")
    if recomputed_v2_root != declared_v2_root:
        errors.append(f"Racine sous-arbre V2 altérée : déclarée '{declared_v2_root}', recalculée '{recomputed_v2_root}'")
        
    # Recalcul racine chaînée
    recomputed_chained_root = compute_chained_root(str(declared_hist), recomputed_v2_root)
    declared_chained_root = seal_doc.get("chained_v2_root")
    if recomputed_chained_root != declared_chained_root:
        errors.append(f"Racine chaînée finale altérée : déclarée '{declared_chained_root}', recalculée '{recomputed_chained_root}'")
        
    # Vérification de provenance Git non circulaire (optionnelle si exécuté sur clone sans git)
    if check_git and (root_dir / ".git").exists():
        subject_commit = (
            seal_doc.get("subject_commit") or 
            seal_doc.get("provenance", {}).get("subject_commit") or 
            seal_doc.get("git_head")
        )
        if subject_commit:
            try:
                # 1. Vérifier l'existence physique du commit sujet dans la base d'objets Git
                proc_cat = subprocess.run(
                    ["git", "-C", str(root_dir), "cat-file", "-t", subject_commit],
                    capture_output=True, text=True
                )
                if proc_cat.returncode != 0 or proc_cat.stdout.strip() != "commit":
                    errors.append(
                        f"Git subject_commit introuvable ou non commit: '{subject_commit}' (HEAD Git désynchronisé)"
                    )
                else:
                    # 2. Obtenir le HEAD actuel
                    proc = subprocess.run(
                        ["git", "-C", str(root_dir), "rev-parse", "HEAD"],
                        capture_output=True, text=True, check=True
                    )
                    current_head = proc.stdout.strip()
                    
                    # 3. Contrat non circulaire : subject_commit doit être HEAD ou ancêtre de HEAD
                    if current_head != subject_commit:
                        proc_ancestor = subprocess.run(
                            ["git", "-C", str(root_dir), "merge-base", "--is-ancestor", subject_commit, current_head],
                            capture_output=True, text=True
                        )
                        if proc_ancestor.returncode != 0:
                            errors.append(
                                f"Rupture de lignée Git : subject_commit '{subject_commit}' n'est ni HEAD ni un ancêtre de '{current_head}' (HEAD Git désynchronisé)"
                            )
            except Exception as e:
                errors.append(f"Erreur vérification Git provenance: {e}")
            
    is_valid = (len(errors) == 0)
    details = {
        "is_valid": is_valid,
        "files_checked": len(manifest),
        "v2_scope_root": recomputed_v2_root,
        "chained_v2_root": recomputed_chained_root,
        "historical_anchor": declared_hist,
        "rfc3161_status": seal_doc.get("rfc3161", {}).get("status"),
        "errors": errors
    }
    return is_valid, errors, details

# ============================================================================
# 6. BATTERIE DE TESTS DE FALSIFICATION (10 SCÉNARIOS)
# ============================================================================

def run_falsification_suite(base_repo: Path) -> dict:
    """Exécute les 10 scénarios d'attaque et de falsification dans un environnement sandbox isolé."""
    results = {}
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        sandbox = Path(tmp_dir) / "obsidia_sandbox"
        sandbox.mkdir(parents=True, exist_ok=True)
        
        # Copie chirurgicale uniquement des 26 fichiers canoniques et du sceau historique
        shutil.copy2(base_repo / "merkle_seal.json", sandbox / "merkle_seal.json")
        for rel_path in CANONICAL_V2_SCOPE:
            src = base_repo / rel_path
            dst = sandbox / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        
        seal_file = sandbox / "merkle_seal_v2.json"
        generate_v2_seal(sandbox, seal_file)
        
        # 10. Sceau nominal inchangé
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["10_NOMINAL_UNTOUCHED"] = {"expected_valid": True, "actual_valid": v, "detected": (v is True)}
        
        # 1. Fichier modifié (1 octet altéré dans contracts.py)
        target = sandbox / "sigma" / "contracts.py"
        orig_bytes = target.read_bytes()
        target.write_bytes(orig_bytes + b"\n# MALICIOUS INJECTION")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        target.write_bytes(orig_bytes)
        results["01_FILE_CONTENT_MODIFIED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False and any("contracts.py" in e for e in errs))}
        
        # 2. Fichier supprimé
        target_del = sandbox / "scripts" / "obsidure_bounded_apply.py"
        del_bytes = target_del.read_bytes()
        target_del.unlink()
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        target_del.write_bytes(del_bytes)
        results["02_FILE_DELETED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False and any("manquant" in e for e in errs))}
        
        # 3. Fichier ajouté au manifeste sans autorisation
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["v2_scope"]["manifest"].append({"path": "malicious_script.sh", "sha256": "0" * 64})
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["03_UNAUTHORIZED_FILE_ADDED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False)}
        generate_v2_seal(sandbox, seal_file)
        
        # 4. Empreinte modifiée dans le manifeste
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["v2_scope"]["manifest"][0]["sha256"] = "a" * 64
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["04_MANIFEST_HASH_TAMPERED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False)}
        generate_v2_seal(sandbox, seal_file)
        
        # 5. Chemin modifié dans le manifeste
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["v2_scope"]["manifest"][0]["path"] = "fake_path/fake_file.py"
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["05_MANIFEST_PATH_TAMPERED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False)}
        generate_v2_seal(sandbox, seal_file)
        
        # 6. Ordre des feuilles modifié
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["v2_scope"]["manifest"].reverse()
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["06_LEAF_ORDER_INVERTED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False)}
        generate_v2_seal(sandbox, seal_file)
        
        # 7. Racine historique remplacée
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["historical_anchor"]["root_value"] = "ffffffffffffffffffffffff"
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["07_HISTORICAL_ROOT_REPLACED"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False)}
        generate_v2_seal(sandbox, seal_file)
        
        # 8. HEAD Git différent
        seal_data = json.loads(seal_file.read_text(encoding="utf-8"))
        seal_data["git_head"] = "0000000000000000000000000000000000000000"
        seal_file.write_text(json.dumps(seal_data), encoding="utf-8")
        subprocess.run(["git", "-C", str(sandbox), "init"], capture_output=True)
        subprocess.run(["git", "-C", str(sandbox), "config", "user.email", "audit@obsidia.org"], capture_output=True)
        subprocess.run(["git", "-C", str(sandbox), "config", "user.name", "Auditor"], capture_output=True)
        subprocess.run(["git", "-C", str(sandbox), "commit", "--allow-empty", "-m", "test"], capture_output=True)
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=True)
        results["08_GIT_HEAD_DISCREPANCY"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False and any("HEAD Git" in e for e in errs))}
        shutil.rmtree(sandbox / ".git", ignore_errors=True)
        generate_v2_seal(sandbox, seal_file)
        
        # 9. Sceau tronqué / JSON corrompu
        seal_file.write_text('{"version": "obsidia.kx108.merkle_seal.v2", "status": "INCOMPLETE"', encoding="utf-8")
        v, errs, _ = verify_v2_seal(sandbox, seal_file, check_git=False)
        results["09_SEAL_TRUNCATED_JSON"] = {"expected_valid": False, "actual_valid": v, "detected": (v is False and any("invalide" in e for e in errs))}
        
    return results

# ============================================================================
# 7. CLI PRINCIPALE
# ============================================================================

def main():
    root_dir = Path(__file__).resolve().parent
    seal_file = root_dir / "merkle_seal_v2.json"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose-historical":
        diag = diagnose_historical_root(root_dir)
        print(json.dumps(diag, indent=2))
        sys.exit(0)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "--generate":
        print(f"[*] Génération du sceau Merkle V2 vers {seal_file}...")
        seal = generate_v2_seal(root_dir, seal_file)
        print(f"[+] Sceau Merkle V2 généré avec succès !")
        print(f"    - Historical Anchor : {seal['historical_anchor']['root_value']} ({seal['historical_anchor']['nature']})")
        print(f"    - V2 Scope Root     : {seal['v2_scope']['v2_scope_root']}")
        print(f"    - Chained V2 Root   : {seal['chained_v2_root']}")
        print(f"    - Files Sealed      : {seal['v2_scope']['file_count']}")
        sys.exit(0)
        
    elif len(sys.argv) > 1 and sys.argv[1] == "--verify":
        print(f"[*] Vérification indépendante du sceau {seal_file}...")
        valid, errors, details = verify_v2_seal(root_dir, seal_file)
        if valid:
            print("[+] VÉRIFICATION RÉUSSIE : Sceau Merkle V2 valide et intègre à 100%.")
            print(f"    - Fichiers vérifiés  : {details['files_checked']}/{len(CANONICAL_V2_SCOPE)}")
            print(f"    - Ancre historique   : {details['historical_anchor']}")
            print(f"    - Racine V2          : {details['v2_scope_root']}")
            print(f"    - Racine chaînée     : {details['chained_v2_root']}")
            print(f"    - Statut RFC3161     : {details['rfc3161_status']}")
            sys.exit(0)
        else:
            print("[-] ÉCHEC DE VÉRIFICATION DU SCEAU V2 :")
            for e in errors:
                print(f"    ! {e}")
            sys.exit(1)
            
    elif len(sys.argv) > 1 and sys.argv[1] == "--test-tamper":
        print("[*] Exécution de la batterie de tests de falsification (10 scénarios)...")
        results = run_falsification_suite(root_dir)
        all_passed = True
        for scenario, res in sorted(results.items()):
            status = "PASS" if res["detected"] else "FAIL"
            print(f"    [{status}] Scénario {scenario} (Détecté: {res['detected']})")
            if not res["detected"]:
                all_passed = False
        if all_passed:
            print("[+] 10/10 SCÉNARIOS DE FALSIFICATION DÉTECTÉS AVEC SUCCÈS.")
            sys.exit(0)
        else:
            print("[-] Certains scénarios de falsification n'ont pas été détectés !")
            sys.exit(1)
            
    else:
        print("Usage:")
        print("  python audit_merkle_v2.py --diagnose-historical")
        print("  python audit_merkle_v2.py --generate")
        print("  python audit_merkle_v2.py --verify")
        print("  python audit_merkle_v2.py --test-tamper")
        sys.exit(1)

if __name__ == "__main__":
    main()
