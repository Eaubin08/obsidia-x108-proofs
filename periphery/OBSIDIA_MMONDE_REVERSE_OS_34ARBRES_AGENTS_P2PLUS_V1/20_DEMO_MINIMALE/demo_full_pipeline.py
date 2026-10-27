# Démo minimale réelle : payload -> Shazam -> arbres dominants -> NodeContinuum -> ContextPacket -> export X-108 -> Reverse OS
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def main():
    trees_data = json.loads((ROOT / "04_ARBRES_34_TENSOR_MATRIX/arbres_34.canon.json").read_text(encoding="utf-8"))
    trees = trees_data["trees"]
    query = json.loads((Path(__file__).resolve().parent / "demo_query.json").read_text(encoding="utf-8"))
    payload = query["raw_payload"]

    import sys
    sys.path.insert(0, str(ROOT / "05_SHAZAM_COGNITIF"))
    shazam_mod = load_module("shazam_mod", "05_SHAZAM_COGNITIF/shazam_cognitif.py")
    shazam_out = shazam_mod.shazam(payload)

    dominant_tree_ids = [int(k) for k in shazam_out["dominant_trees"].keys()]
    dominant_tree_names = [trees[i]["name"] for i in dominant_tree_ids if 0 <= i < len(trees)]

    node_continuum = {
        "id": "NODE_CONTINUUM_DEMO_001",
        "description": "Nœud créé par divergence/contextualisation de démo.",
        "event_ids": [],
        "divergence": 0.21,
        "non_decision": True
    }

    context_packet = {
        "query": query["query"],
        "events": [],
        "activated_trees": shazam_out["dominant_trees"],
        "dominant_tree_names": dominant_tree_names,
        "calibrated_links": [],
        "projection": {"node_continuum": node_continuum},
        "confidence": 0.42,
        "non_decision": True,
        "export_target": "X-108"
    }

    export_mod = load_module("export_mod", "14_CONTEXT_EXPORT_X108_BOUNDARY/export_for_x108.py")
    exported_context = export_mod.export(context_packet)

    flow = {
        "agent_name": "DEMO_FULL_PIPELINE",
        "reason_code": "RC_CONTEXT_ONLY",
        "merkle_root": "demo_merkle_root_placeholder",
        "verdict": "NO_KERNEL_DECISION",
        "tree_vector": shazam_out["tree_activation"],
        "proof_status": "DEMO_ONLY"
    }
    reverse_mod = load_module("reverse_mod", "06_REVERSE_OS_SSR_JARVIS/reverse_os.py")
    reverse_output = reverse_mod.project(flow)

    out_dir = Path(__file__).resolve().parent
    (out_dir / "demo_output_context_packet.json").write_text(json.dumps(exported_context, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "demo_reverse_os_output.json").write_text(json.dumps(reverse_output, ensure_ascii=False, indent=2), encoding="utf-8")

    print("DEMO_MMONDE_PIPELINE_OK")
    print("no ACT produced")
    print("context only")
    print("X108 required for decision")

if __name__ == "__main__":
    main()
