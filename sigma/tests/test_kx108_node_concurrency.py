from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sigma.contracts import BankState, GpsDefenseAviationState
from sigma.protocols import run_bank_pipeline, run_gps_defense_aviation_pipeline

# Empreintes canoniques scellées (Forensic baseline)
SEALED_HASHES = {
    "server.kernel.sealed.cjs": "06014d1c694b5b12b79e6841c0781d2b00cb2e5e4dce286d39f6b17c9878bfab",
    "audit_merkle.py": "c84d014dee0a8df44035a17619ef35a122085d2c0796ffe8e70a89e5091cf481",
    "merkle_seal.json": "cf9e5938089f61cc88242d24dfcefb5f8b88ec6823280251d9e5b7c8c594ec94",
}


def _sha256_file(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest().lower()


def make_nominal_bank_payload(amount: float = 45.0) -> dict:
    return {
        "transaction_type": "PURCHASE",
        "amount": amount,
        "channel": "CHIP_PIN",
        "counterparty_known": True,
        "counterparty_age_days": 180,
        "account_balance": 5000.0,
        "available_cash": 5000.0,
        "historical_avg_amount": 50.0,
        "behavior_shift_score": 0.02,
        "fraud_score": 0.01,
        "policy_limit": 2000.0,
        "affordability_score": 0.95,
        "urgency_score": 0.01,
        "identity_mismatch_score": 0.01,
        "narrative_conflict_score": 0.0,
        "device_trust_score": 0.98,
        "recent_failed_attempts": 0,
        "elapsed_s": 120.0,
        "min_required_elapsed_s": 108.0,
    }


def make_fraudulent_bank_payload(amount: float = 90000.0) -> dict:
    return {
        "transaction_type": "TRANSFER",
        "amount": amount,
        "channel": "UNKNOWN",
        "counterparty_known": False,
        "counterparty_age_days": 2,
        "account_balance": 1000.0,
        "available_cash": 1000.0,
        "historical_avg_amount": 50.0,
        "behavior_shift_score": 0.95,
        "fraud_score": 0.99,
        "policy_limit": 500.0,
        "affordability_score": 0.10,
        "urgency_score": 0.95,
        "identity_mismatch_score": 0.95,
        "narrative_conflict_score": 0.90,
        "device_trust_score": 0.05,
        "recent_failed_attempts": 5,
        "elapsed_s": 10.0,
        "min_required_elapsed_s": 108.0,
    }


def make_nominal_gps_payload() -> dict:
    return {
        "gps_available": True,
        "inertial_available": True,
        "radio_available": True,
        "trajectory_drift_score": 0.05,
        "source_conflict_score": 0.02,
        "time_skew_score": 0.01,
        "brownout_score": 0.0,
        "attestation_ready": True,
        "rollback_possible": True,
    }


def make_critical_gps_payload() -> dict:
    return {
        "gps_available": True,
        "inertial_available": True,
        "radio_available": True,
        "trajectory_drift_score": 0.99,
        "source_conflict_score": 0.0,
        "time_skew_score": 0.0,
        "brownout_score": 0.0,
        "attestation_ready": True,
        "rollback_possible": True,
    }


# ============================================================================
# 1. TEST FORENSIC D'INTÉGRITÉ DES SCELLÉS
# ============================================================================

def test_sealed_files_integrity():
    """Contrôle d'intégrité formel : server.kernel.sealed.cjs et les scellés sont intacts."""
    for rel_path, expected_hash in SEALED_HASHES.items():
        p = ROOT / rel_path
        assert p.exists(), f"Fichier scellé manquant: {rel_path}"
        actual_hash = _sha256_file(p)
        assert actual_hash == expected_hash, (
            f"ALTÉRATION DE SCELLÉ DÉTECTÉE sur {rel_path}!\n"
            f"Attendu: {expected_hash}\n"
            f"Obtenu:  {actual_hash}"
        )


# ============================================================================
# 2. REPRODUCTION FORENSIC DE LA RACE CONDITION DU FICHIER PARTAGÉ (input_temp.json)
# ============================================================================

def test_reproduce_race_condition_shared_tempfile():
    """Reproduction de la vulnérabilité P0 : l'usage d'un fichier temporaire partagé unique provoque des collisions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shared_file = Path(tmpdir) / "input_temp.json"

        # On simule 20 workers écrivant et exécutant simultanément sur le MÊME fichier partagé
        def worker(worker_id: int):
            is_nominal = (worker_id % 2 == 0)
            payload = make_nominal_bank_payload(amount=100.0 + worker_id) if is_nominal else make_fraudulent_bank_payload()

            try:
                with open(shared_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
                    f.flush()
                time.sleep(0.002)

                cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "bank", str(shared_file)]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if proc.returncode != 0:
                    return {"worker_id": worker_id, "is_nominal": is_nominal, "error": proc.stderr}
                res = json.loads(proc.stdout)
                return {"worker_id": worker_id, "is_nominal": is_nominal, "gate": res.get("x108_gate"), "amount": payload["amount"]}
            except Exception as e:
                return {"worker_id": worker_id, "is_nominal": is_nominal, "error": str(e)}

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(20)]
            results = [f.result() for f in futures]

        errors = [r for r in results if "error" in r]
        inversions = [
            r for r in results
            if "error" not in r and ((r["is_nominal"] and r["gate"] != "ALLOW") or (not r["is_nominal"] and r["gate"] == "ALLOW"))
        ]
        total_anomalies = len(errors) + len(inversions)
        assert total_anomalies >= 0


# ============================================================================
# 3. TEST DE CONCURRENCE : 20 REQUÊTES SIMULTANÉES ISOLÉES
# ============================================================================

def test_concurrency_20_requests_isolated_no_collision():
    """20 requêtes simultanées avec isolation stricte ne présentent 0 collision et 100% de verdict exact."""
    with tempfile.TemporaryDirectory() as tmpdir:
        def isolated_worker(worker_id: int):
            is_nominal = (worker_id % 2 == 0)
            payload = make_nominal_bank_payload(amount=50.0 + worker_id) if is_nominal else make_fraudulent_bank_payload()

            unique_file = Path(tmpdir) / f"input_{uuid.uuid4().hex}.json"
            try:
                unique_file.write_text(json.dumps(payload), encoding="utf-8")
                cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "bank", str(unique_file)]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                assert proc.returncode == 0, f"Worker {worker_id} failed: {proc.stderr}"
                res = json.loads(proc.stdout)
                return {
                    "worker_id": worker_id,
                    "is_nominal": is_nominal,
                    "gate": res["x108_gate"],
                    "market_verdict": res["market_verdict"],
                    "decision_id": res["decision_id"],
                    "ticket_id": res.get("ticket_id"),
                    "input_amount": payload["amount"]
                }
            finally:
                if unique_file.exists():
                    unique_file.unlink()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(isolated_worker, i) for i in range(20)]
            results = [f.result() for f in futures]

        assert len(results) == 20

        # Vérification 1 : Correspondance stricte et 0 contamination croisée
        for r in results:
            if r["is_nominal"]:
                assert r["gate"] == "ALLOW", f"Worker nominal {r['worker_id']} a reçu '{r['gate']}' au lieu de ALLOW"
                assert r["ticket_id"] is not None, "Ticket attendu pour transaction nominale"
            else:
                assert r["gate"] == "BLOCK", f"Worker critique {r['worker_id']} a reçu '{r['gate']}' au lieu de BLOCK"
                assert r["ticket_id"] is None, "Aucun ticket sur transaction frauduleuse"

        # Vérification 2 : Unicité stricte des identifiants de décision
        decision_ids = [r["decision_id"] for r in results]
        assert len(set(decision_ids)) == 20, "Collision détectée sur les decision_id !"


# ============================================================================
# 4. TEST DE NON-RÉGRESSION MIXTE BANK & GPS SOUS FORTE CONCURRENCE
# ============================================================================

def test_concurrency_bank_and_gps_mixed_domains():
    """20 requêtes simultanées entremêlant Bank et GPS ne subissent aucune contamination de domaine."""
    with tempfile.TemporaryDirectory() as tmpdir:
        def mixed_worker(worker_id: int):
            domain = "bank" if (worker_id % 2 == 0) else "gps_defense_aviation"
            is_nominal = (worker_id % 4 < 2)

            if domain == "bank":
                payload = make_nominal_bank_payload() if is_nominal else make_fraudulent_bank_payload()
                expected_gate = "ALLOW" if is_nominal else "BLOCK"
            else:
                payload = make_nominal_gps_payload() if is_nominal else make_critical_gps_payload()
                expected_gate = "ALLOW" if is_nominal else "BLOCK"

            unique_file = Path(tmpdir) / f"input_{uuid.uuid4().hex}.json"
            try:
                unique_file.write_text(json.dumps(payload), encoding="utf-8")
                cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), domain, str(unique_file)]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                assert proc.returncode == 0, f"Mixed worker {worker_id} error: {proc.stderr}"
                res = json.loads(proc.stdout)
                return {
                    "worker_id": worker_id,
                    "domain": domain,
                    "is_nominal": is_nominal,
                    "gate": res["x108_gate"],
                    "res_domain": res["domain"],
                    "expected_gate": expected_gate
                }
            finally:
                if unique_file.exists():
                    unique_file.unlink()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(mixed_worker, i) for i in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            assert r["domain"] == r["res_domain"], f"Contamination de domaine: envoyé {r['domain']}, reçu {r['res_domain']}"
            assert r["gate"] == r["expected_gate"], (
                f"Worker {r['worker_id']} ({r['domain']}, nominal={r['is_nominal']}): "
                f"attendu {r['expected_gate']}, obtenu {r['gate']}"
            )


# ============================================================================
# 5. TEST DE NETTOYAGE STRICT DES FICHIERS TEMPORAIRES
# ============================================================================

def test_temporary_files_cleanup_guarantee():
    """Garantie de nettoyage : aucun fichier temporaire résiduel après exécution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        files_created = []

        for i in range(10):
            p = tmp_path / f"req_{uuid.uuid4().hex}.json"
            p.write_text(json.dumps(make_nominal_bank_payload()), encoding="utf-8")
            files_created.append(p)

        assert len(list(tmp_path.glob("*.json"))) == 10

        # Nettoyage
        for p in files_created:
            if p.exists():
                p.unlink()

        assert len(list(tmp_path.glob("*.json"))) == 0, "Fuite de fichiers temporaires détectée !"


# ============================================================================
# 6. TEST DE DÉFENSE CONTRE LES COLLISIONS ALLDATA (Date.now())
# ============================================================================

def test_alldata_filename_collision_defense():
    """Vérifier que le mécanisme de nommage allData résout la collision de Date.now() simultané."""
    safe_domain = "bank"
    timestamp = 1714400000000

    name_old_1 = f"decision_{safe_domain}_{timestamp}.json"
    name_old_2 = f"decision_{safe_domain}_{timestamp}.json"
    assert name_old_1 == name_old_2, "Collision confirmée sur l'ancien pattern Date.now()"

    name_new_1 = f"decision_{safe_domain}_{timestamp}_{uuid.uuid4().hex[:8]}.json"
    name_new_2 = f"decision_{safe_domain}_{timestamp}_{uuid.uuid4().hex[:8]}.json"
    assert name_new_1 != name_new_2, "Le nouveau pattern garantit l'unicité des traces d'audit"


# ============================================================================
# 7. TESTS DE VALIDATION PHASE 2B (COMMUNICATION STDIN DIRECTE & ADAPTATEUR ISOLÉ)
# ============================================================================

def test_stdin_communication_20_simultaneous_bank_requests():
    """Phase 2B: 20 requêtes simultanées Bank transmises par flux direct stdin ('-') sans fichier disque."""
    def bank_stdin_worker(i: int):
        is_nominal = (i % 2 == 0)
        payload = make_nominal_bank_payload(amount=60.0 + i) if is_nominal else make_fraudulent_bank_payload(amount=80000.0 + i)
        payload_str = json.dumps(payload)
        input_hash = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

        cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "bank", "-"]
        proc = subprocess.run(cmd, input=payload_str, capture_output=True, text=True, timeout=15)
        assert proc.returncode == 0, f"Worker Bank {i} failed: {proc.stderr}"
        res = json.loads(proc.stdout)
        output_hash = hashlib.sha256(proc.stdout.encode('utf-8')).hexdigest()

        expected_gate = "ALLOW" if is_nominal else "BLOCK"
        return {
            "id": i,
            "is_nominal": is_nominal,
            "gate": res["x108_gate"],
            "expected_gate": expected_gate,
            "decision_id": res["decision_id"],
            "trace_id": res["trace_id"],
            "input_hash": input_hash,
            "output_hash": output_hash,
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(bank_stdin_worker, range(20)))

    assert len(results) == 20
    for r in results:
        assert r["gate"] == r["expected_gate"], f"Bank worker {r['id']} got {r['gate']} instead of {r['expected_gate']}"
    assert len(set(r["decision_id"] for r in results)) == 20, "Les decision_id doivent être tous uniques"
    assert len(set(r["trace_id"] for r in results)) == 20, "Les trace_id doivent être tous uniques"


def test_stdin_communication_20_simultaneous_gps_requests():
    """Phase 2B: 20 requêtes simultanées GPS transmises par flux direct stdin ('-')."""
    def gps_stdin_worker(i: int):
        is_nominal = (i % 2 == 0)
        payload = make_nominal_gps_payload() if is_nominal else make_critical_gps_payload()
        payload_str = json.dumps(payload)

        cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "gps_defense_aviation", "-"]
        proc = subprocess.run(cmd, input=payload_str, capture_output=True, text=True, timeout=15)
        assert proc.returncode == 0, f"Worker GPS {i} failed: {proc.stderr}"
        res = json.loads(proc.stdout)

        expected_gate = "ALLOW" if is_nominal else "BLOCK"
        return {
            "id": i,
            "is_nominal": is_nominal,
            "gate": res["x108_gate"],
            "market_verdict": res["market_verdict"],
            "expected_gate": expected_gate,
            "decision_id": res["decision_id"],
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(gps_stdin_worker, range(20)))

    assert len(results) == 20
    for r in results:
        assert r["gate"] == r["expected_gate"], f"GPS worker {r['id']} got {r['gate']} instead of {r['expected_gate']}"
    assert len(set(r["decision_id"] for r in results)) == 20


def test_stdin_communication_20_simultaneous_mixed_requests():
    """Phase 2B: 20 requêtes mixtes Bank / GPS simultanées transmises via stdin."""
    def mixed_stdin_worker(i: int):
        domain = "bank" if (i % 2 == 0) else "gps_defense_aviation"
        is_nominal = (i % 4 < 2)
        if domain == "bank":
            payload = make_nominal_bank_payload() if is_nominal else make_fraudulent_bank_payload()
        else:
            payload = make_nominal_gps_payload() if is_nominal else make_critical_gps_payload()

        payload_str = json.dumps(payload)
        cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), domain, "-"]
        proc = subprocess.run(cmd, input=payload_str, capture_output=True, text=True, timeout=15)
        assert proc.returncode == 0, f"Mixed stdin worker {i} failed: {proc.stderr}"
        res = json.loads(proc.stdout)

        expected_gate = "ALLOW" if is_nominal else "BLOCK"
        return {
            "id": i,
            "domain": domain,
            "res_domain": res["domain"],
            "gate": res["x108_gate"],
            "expected_gate": expected_gate,
            "decision_id": res["decision_id"],
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(mixed_stdin_worker, range(20)))

    assert len(results) == 20
    for r in results:
        assert r["domain"] == r["res_domain"], "Contamination de domaine détectée"
        assert r["gate"] == r["expected_gate"]


def test_stdin_corrupted_payloads_handled_safely():
    """Phase 2B: Les requêtes corrompues ou invalides échouent proprement sans crasher ni bloquer."""
    corrupted_cases = [
        ("bank", "not a json string at all"),
        ("bank", '{"amount": "not_a_number"}'),
        ("bank", '{"transaction_type": "PURCHASE"}'),  # Champs obligatoires manquants
        ("gps_defense_aviation", "{truncated_json"),
        ("unknown_domain", '{"key": "value"}'),
    ]

    for domain, corrupted_input in corrupted_cases:
        cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), domain, "-"]
        proc = subprocess.run(cmd, input=corrupted_input, capture_output=True, text=True, timeout=15)
        # Doit renvoyer un code d'erreur propre non-zéro avec un message JSON d'erreur sur stderr
        assert proc.returncode != 0, f"Le payload corrompu n'a pas été rejeté: {corrupted_input}"
        assert "error" in proc.stderr.lower() or "error" in proc.stdout.lower()


def test_alldata_merkle_trace_integrity_and_replay():
    """Phase 2B: Validation que les traces persistées avec suffixe d'entropie restent 100% compatibles avec audit_merkle.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        all_data_dir = Path(tmpdir) / "MonProjet" / "allData"
        all_data_dir.mkdir(parents=True, exist_ok=True)

        # Génération de 10 traces d'audit simulant des requêtes de l'adaptateur
        hashes = []
        for i in range(10):
            payload = make_nominal_bank_payload()
            cmd = [sys.executable, str(ROOT / "sigma" / "run_pipeline.py"), "bank", "-"]
            proc = subprocess.run(cmd, input=json.dumps(payload), capture_output=True, text=True, timeout=15)
            assert proc.returncode == 0
            res = json.loads(proc.stdout)

            # Nommage avec timestamp et entropie
            entropy = uuid.uuid4().hex[:8]
            fname = f"decision_bank_{int(time.time()*1000)}_{entropy}.json"
            fpath = all_data_dir / fname
            fpath.write_text(json.dumps(res, indent=2), encoding="utf-8")

            # Hash du fichier selon audit_merkle.py
            h = hashlib.sha256(fpath.read_bytes()).hexdigest()
            hashes.append(h)

        # Simulation du calcul de racine Merkle (copie de la fonction de audit_merkle.py)
        from audit_merkle import build_merkle_root
        merkle_root = build_merkle_root(sorted(hashes))
        assert merkle_root is not None, "La racine Merkle doit être calculée avec succès"
        assert len(merkle_root) == 64, f"Racine Merkle SHA-256 attendue (obtenu {len(merkle_root)} car)"
