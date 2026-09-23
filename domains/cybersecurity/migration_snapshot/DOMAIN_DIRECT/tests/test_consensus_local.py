#!/usr/bin/env python3
"""
Simulation locale du consensus multi-nœuds Phase 9
Lance 4 instances FastAPI sur des ports 8011-8014 et exécute l'agrégateur.
Équivalent fonctionnel de docker compose sans Docker.
"""
import subprocess, time, json, urllib.request, os, sys, signal

PYTHONPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTS = [8011, 8012, 8013, 8014]
NODE_IDS = ["node1", "node2", "node3", "node4"]
PROCS = []

def start_nodes():
    for port, node_id in zip(PORTS, NODE_IDS):
        env = os.environ.copy()
        env["PYTHONPATH"] = PYTHONPATH
        env["OBSIDIA_NODE_ID"] = node_id
        p = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "core.api.app:APP",
             "--host", "0.0.0.0", "--port", str(port), "--log-level", "error"],
            cwd=PYTHONPATH, env=env,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        PROCS.append(p)
        print(f"  Nœud {node_id} démarré sur port {port} (PID {p.pid})")

def post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def consensus(responses):
    counts = {}
    for r in responses:
        d = r.get("decision")
        counts[d] = counts.get(d, 0) + 1
    best = max(counts.items(), key=lambda x: x[1])
    if best[1] >= 3:
        return {"decision": best[0], "votes": counts, "supermajority": True}
    return {"decision": "BLOCK", "votes": counts, "supermajority": False,
            "reason": "no 3/4 supermajority"}

def stop_nodes():
    for p in PROCS:
        p.terminate()
    for p in PROCS:
        p.wait()

def main():
    print("=== OBSIDIA Phase 9 — Simulation Consensus Multi-Nœuds ===\n")
    print("Démarrage des 4 nœuds...")
    start_nodes()
    print("Attente de l'initialisation (5s)...")
    time.sleep(5)

    payload = {
        "metrics": {"T_mean": 0.2, "H_score": 0.3, "A_score": 0.1, "S": 0.25},
        "theta_S": 0.25,
        "nonce": "distributed-demo-local-1"
    }

    print(f"\nPayload envoyé : {json.dumps(payload, indent=2)}\n")
    print("Interrogation des 4 nœuds...")

    responses = []
    for port, node_id in zip(PORTS, NODE_IDS):
        url = f"http://localhost:{port}/v1/decision"
        # Chaque nœud reçoit un nonce unique (comportement réel en production)
        node_payload = dict(payload)
        node_payload["nonce"] = f"distributed-demo-local-{node_id}-1"
        try:
            resp = post(url, node_payload)
            responses.append(resp)
            print(f"  [{node_id}:{port}] decision={resp.get('decision')} ✓")
        except Exception as e:
            print(f"  [{node_id}:{port}] ERREUR: {e}")
            responses.append({"decision": "ERROR", "error": str(e)})

    print("\n=== RÉSULTAT DU CONSENSUS ===")
    result = consensus(responses)
    print(json.dumps(result, indent=2))

    stop_nodes()
    print("\nNœuds arrêtés.")
    return result

if __name__ == "__main__":
    main()
