"""
Chain orchestrator: QUERY -> CONSUMER -> ENGINE (readonly, no modifications)
Runs the full context packet chain and captures all outputs.
"""
import subprocess, sys, json, os, pathlib

VENV_PYTHON = r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidiashell-main\.venv_api8011\Scripts\python.exe"
BASE = r"C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs\periphery\brody_memory_readonly"
QUERY_MOD = os.path.join(BASE, "context_packet_query_readonly", "brody_context_packet_query_readonly_v1.py")
CONSUMER_MOD = os.path.join(BASE, "context_packet_consumer_readonly", "brody_context_packet_consumer_readonly_v1.py")
ENGINE_MOD = os.path.join(BASE, "local_response_engine_readonly", "brody_local_response_engine_readonly_v1.py")

AUDIT_DIR = pathlib.Path(r"C:\Users\User\Desktop\obsidia-engine-proof-core\_local_audits\BRODY_CONTEXT_PACKET_CHAIN_TEST_READONLY_20260513_192629")
CAPTURES = AUDIT_DIR / "api_captures"
CHAIN_OUT = AUDIT_DIR / "chain_outputs"

env = {**os.environ, "NEO4J_PASSWORD": "obsidia-graphiti-dev", "NEO4J_URI": "bolt://localhost:7688", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
results = {}

# --- STEP 1: QUERY ---
print("[STEP 1] CONTEXT_PACKET_QUERY_READONLY -- query=Kernel limit=8")
r1 = subprocess.run([VENV_PYTHON, QUERY_MOD, "--query", "Kernel", "--limit", "8"],
                    capture_output=True, text=True, encoding="utf-8", env=env)
query_raw = r1.stdout.strip()
query_err = r1.stderr.strip()
results["step1_returncode"] = r1.returncode

if r1.returncode != 0:
    print(f"  ERROR rc={r1.returncode}: {query_err[:200]}")
    results["step1_status"] = "FAIL"
    print(json.dumps(results, indent=2))
    sys.exit(1)

try:
    query_obj = json.loads(query_raw)
except json.JSONDecodeError as e:
    print(f"  ERROR parsing query JSON: {e}")
    results["step1_status"] = "FAIL_JSON"
    sys.exit(1)

results["step1_status"] = query_obj.get("status")
results["step1_results_count"] = query_obj.get("results_count")
results["step1_decision_authority"] = query_obj.get("decision_authority")
results["step1_boundary_keys"] = {k: query_obj.get(k) for k in ["memory_decision","allowed_to_decide","emits_act","kernel_binding","x108_runtime_binding","x108_merge","kernel_mutation","x108_mutation"]}

(CAPTURES / "context_packet_query_kernel_output.json").write_text(query_raw, encoding="utf-8")
print(f"  status={results['step1_status']} results_count={results['step1_results_count']} decision_authority={results['step1_decision_authority']}")
print(f"  boundary_all_false={all(v == False for v in results['step1_boundary_keys'].values())}")

# --- STEP 2: CONSUMER ---
print("[STEP 2] CONTEXT_PACKET_CONSUMER_READONLY")
# Consumer expects --packet-json as a FILE PATH (reads it via Path().read_text)
query_packet_path = str(CAPTURES / "context_packet_query_kernel_output.json")
consumer_out_path = str(CHAIN_OUT / "consumer_output.json")
consumer_md_path = str(CHAIN_OUT / "consumer_response.md")
r2 = subprocess.run([VENV_PYTHON, CONSUMER_MOD,
                     "--packet-json", query_packet_path,
                     "--out-json", consumer_out_path,
                     "--out-md", consumer_md_path],
                    capture_output=True, text=True, encoding="utf-8", env=env)
consumer_raw = r2.stdout.strip()
consumer_err = r2.stderr.strip()
results["step2_returncode"] = r2.returncode

if r2.returncode != 0:
    print(f"  ERROR rc={r2.returncode}: {consumer_err[:400]}")
    results["step2_status"] = "FAIL"
    print(json.dumps(results, indent=2))
    sys.exit(1)

try:
    consumer_obj = json.loads(consumer_raw)
except json.JSONDecodeError as e:
    # Try reading the out-json file
    try:
        consumer_obj = json.loads(pathlib.Path(consumer_out_path).read_text(encoding="utf-8"))
        consumer_raw = json.dumps(consumer_obj)
    except Exception:
        print(f"  ERROR parsing consumer JSON: {e}")
        results["step2_status"] = "FAIL_JSON"
        print(json.dumps(results, indent=2))
        sys.exit(1)

results["step2_status"] = consumer_obj.get("status")
results["step2_boundary_keys"] = {k: consumer_obj.get(k) for k in ["memory_decision","emits_act","kernel_binding","x108_runtime_binding","x108_merge","kernel_mutation","x108_mutation"]}
print(f"  status={results['step2_status']}")
print(f"  boundary_all_false={all(v == False for v in results['step2_boundary_keys'].values())}")

# --- STEP 3: ENGINE ---
print("[STEP 3] LOCAL_RESPONSE_ENGINE_READONLY")
# Engine expects --hydrated-packet-json with context_packet at root.
# The query output (not consumer output) has context_packet at top level.
# The consumer output is a separate enriched response captured independently.
engine_out_path = str(CHAIN_OUT / "engine_output.json")
engine_md_path = str(CHAIN_OUT / "engine_response.md")
r3 = subprocess.run([VENV_PYTHON, ENGINE_MOD,
                     "--hydrated-packet-json", query_packet_path,
                     "--out-json", engine_out_path,
                     "--out-md", engine_md_path],
                    capture_output=True, text=True, encoding="utf-8", env=env)
engine_raw = r3.stdout.strip()
engine_err = r3.stderr.strip()
results["step3_returncode"] = r3.returncode

if r3.returncode != 0:
    print(f"  ERROR rc={r3.returncode}: {engine_err[:400]}")
    results["step3_status"] = "FAIL"
    print(json.dumps(results, indent=2))
    sys.exit(1)

try:
    engine_obj = json.loads(engine_raw)
except json.JSONDecodeError as e:
    try:
        engine_obj = json.loads(pathlib.Path(engine_out_path).read_text(encoding="utf-8"))
        engine_raw = json.dumps(engine_obj)
    except Exception:
        print(f"  ERROR parsing engine JSON: {e}")
        results["step3_status"] = "FAIL_JSON"
        print(json.dumps(results, indent=2))
        sys.exit(1)

results["step3_status"] = engine_obj.get("status")
results["step3_material_quality"] = engine_obj.get("material_quality")
results["step3_boundary_keys"] = {k: engine_obj.get(k) for k in ["memory_decision","emits_act","kernel_binding","x108_runtime_binding","x108_merge","kernel_mutation","x108_mutation"]}
print(f"  status={results['step3_status']}")
print(f"  material_quality={results['step3_material_quality']}")
print(f"  boundary_all_false={all(v == False for v in results['step3_boundary_keys'].values())}")

# --- VERDICT ---
step1_pass = results.get("step1_status") == "BRODY_CONTEXT_PACKET_QUERY_READONLY_PASS"
step2_pass = results.get("step2_status") == "BRODY_CONTEXT_PACKET_CONSUMER_READONLY_PASS"
step3_pass = results.get("step3_status") == "BRODY_LOCAL_RESPONSE_ENGINE_READONLY_PASS"

def no_explicit_true(d):
    """Boundary violation only if a key is explicitly True (not False, not None/absent)."""
    return not any(v is True for v in d.values())

all_boundaries_false = (
    no_explicit_true(results["step1_boundary_keys"]) and
    no_explicit_true(results["step2_boundary_keys"]) and
    no_explicit_true(results["step3_boundary_keys"])
)

chain_verdict = "CHAIN_PASS" if (step1_pass and step2_pass and step3_pass and all_boundaries_false) else "CHAIN_BLOCKED"
results["chain_verdict"] = chain_verdict
results["all_boundaries_false"] = all_boundaries_false

print(f"\n{'='*60}")
print(f"CHAIN VERDICT: {chain_verdict}")
print(f"STEP1 QUERY  : {'PASS' if step1_pass else 'FAIL'}")
print(f"STEP2 CONSUMER: {'PASS' if step2_pass else 'FAIL'}")
print(f"STEP3 ENGINE : {'PASS' if step3_pass else 'FAIL'}")
print(f"ALL_BOUNDARIES_FALSE: {all_boundaries_false}")
print(f"{'='*60}")

# Save summary
summary_path = AUDIT_DIR / "reports" / "chain_result_summary.json"
summary_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
print(f"\nSummary saved: {summary_path}")
