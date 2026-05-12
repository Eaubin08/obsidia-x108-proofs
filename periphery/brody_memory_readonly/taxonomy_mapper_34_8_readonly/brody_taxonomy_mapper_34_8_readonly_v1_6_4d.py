import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

BOUNDARY = {
    "readonly": True,
    "memory_authority": False,
    "memory_decision": False,
    "allowed_to_decide": False,
    "emits_act": False,
    "kernel_binding": False,
    "x108_merge": False,
    "kernel_mutation": False,
    "x108_mutation": False,
    "decision_authority": "KX108_ONLY",
    "scope": "BRODY_TAXONOMY_MAPPER_34_8_PERIPHERY_ONLY",
}

CATEGORIES = [
    {
        "category_id": "I",
        "category_name": "Arbres Fondamentaux",
        "tree_ids": ["01", "02", "03", "04", "05"],
    },
    {
        "category_id": "II",
        "category_name": "Arbres Cognitifs",
        "tree_ids": ["06", "07", "08", "09", "10"],
    },
    {
        "category_id": "III",
        "category_name": "Arbres de Connaissance",
        "tree_ids": ["11", "12", "13", "14", "15"],
    },
    {
        "category_id": "IV",
        "category_name": "Arbres Relationnels & Sociaux",
        "tree_ids": ["16", "17", "18", "19"],
    },
    {
        "category_id": "V",
        "category_name": "Arbres d’Action & de Transformation",
        "tree_ids": ["20", "21", "22"],
    },
    {
        "category_id": "VI",
        "category_name": "Arbres Temporels & Mémoriels",
        "tree_ids": ["23", "24", "25"],
    },
    {
        "category_id": "VII",
        "category_name": "Arbres Méta-Structurels",
        "tree_ids": ["26", "27", "28", "29"],
    },
    {
        "category_id": "VIII",
        "category_name": "Arbres liés à Obsidia / AGI",
        "tree_ids": ["30", "31", "32", "33", "34"],
    },
]

TREES = [
    ("01", "Arbre de l’Humain", "ARBRE_01__Arbre_de_l_Humain"),
    ("02", "Arbre de la Conscience", "ARBRE_02__Arbre_de_la_Conscience"),
    ("03", "Arbre de la Perception", "ARBRE_03__Arbre_de_la_Perception"),
    ("04", "Arbre du Sens", "ARBRE_04__Arbre_du_Sens"),
    ("05", "Arbre de l’Identité", "ARBRE_05__Arbre_de_l_Identite"),
    ("06", "Arbre de la Compréhension", "ARBRE_06__Arbre_de_la_Comprehension"),
    ("07", "Arbre de l’Organisation", "ARBRE_07__Arbre_de_l_Organisation"),
    ("08", "Arbre de la Pensée", "ARBRE_08__Arbre_de_la_Pensee"),
    ("09", "Arbre de l’Intelligence", "ARBRE_09__Arbre_de_l_Intelligence"),
    ("10", "Arbre du Langage", "ARBRE_10__Arbre_du_Langage"),
    ("11", "Arbre de la Science", "ARBRE_11__Arbre_de_la_Science"),
    ("12", "Arbre de la Technique", "ARBRE_12__Arbre_de_la_Technique"),
    ("13", "Arbre de l’Art", "ARBRE_13__Arbre_de_l_Art"),
    ("14", "Arbre de la Philosophie", "ARBRE_14__Arbre_de_la_Philosophie"),
    ("15", "Arbre de la Spiritualité", "ARBRE_15__Arbre_de_la_Spiritualite"),
    ("16", "Arbre de la Relation", "ARBRE_16__Arbre_de_la_Relation"),
    ("17", "Arbre du Collectif", "ARBRE_17__Arbre_du_Collectif"),
    ("18", "Arbre de la Transmission", "ARBRE_18__Arbre_de_la_Transmission"),
    ("19", "Arbre de la Culture", "ARBRE_19__Arbre_de_la_Culture"),
    ("20", "Arbre de l’Action", "ARBRE_20__Arbre_de_l_Action"),
    ("21", "Arbre de la Création", "ARBRE_21__Arbre_de_la_Creation"),
    ("22", "Arbre de la Transformation", "ARBRE_22__Arbre_de_la_Transformation"),
    ("23", "Arbre du Temps", "ARBRE_23__Arbre_du_Temps"),
    ("24", "Arbre de la Mémoire", "ARBRE_24__Arbre_de_la_Memoire"),
    ("25", "Arbre de l’Histoire", "ARBRE_25__Arbre_de_l_Histoire"),
    ("26", "Arbre de la Cohérence", "ARBRE_26__Arbre_de_la_Coherence"),
    ("27", "Arbre de la Vérité", "ARBRE_27__Arbre_de_la_Verite"),
    ("28", "Arbre de la Valeur", "ARBRE_28__Arbre_de_la_Valeur"),
    ("29", "Arbre de la Finalité", "ARBRE_29__Arbre_de_la_Finalite"),
    ("30", "Arbre Cognitif Global", "ARBRE_30__Arbre_Cognitif_Global"),
    ("31", "Arbre des Flux", "ARBRE_31__Arbre_des_Flux"),
    ("32", "Arbre des Connexions", "ARBRE_32__Arbre_des_Connexions"),
    ("33", "Arbre de l’Optimisation", "ARBRE_33__Arbre_de_l_Optimisation"),
    ("34", "Arbre de la Stabilité", "ARBRE_34__Arbre_de_la_Stabilite"),
]

V43_GROUPS_IMPLEMENTED = [
    "GROUPE_01__Memoire_Trace_Audit",
    "GROUPE_02__Temps_X_108_Non_contournement",
    "GROUPE_03__Semantique_OS4_Recit",
    "GROUPE_04__Ethique_ADeLe_Securite",
    "GROUPE_05__Agents_Infrastructure_Tools",
    "GROUPE_06__Cosmologie_Economie_R_D",
    "GROUPE_07__Ops_CI_CD_Validation_continue",
]

def norm(s):
    s = str(s or "").lower()
    s = s.replace("’", "'").replace("`", "'")
    repl = {
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a",
        "î": "i", "ï": "i",
        "ô": "o",
        "ù": "u", "û": "u",
        "ç": "c",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    return s

def flatten_text(obj):
    parts = []
    if isinstance(obj, dict):
        for v in obj.values():
            parts.append(flatten_text(v))
    elif isinstance(obj, list):
        for v in obj:
            parts.append(flatten_text(v))
    else:
        parts.append(str(obj))
    return " ".join(parts)

def read_pointer(path):
    out = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip()
    return out

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def main():
    if len(sys.argv) != 3:
        raise SystemExit("USAGE: python brody_taxonomy_mapper_34_8_readonly_v1_6_4d.py <x108_root> <out_root>")

    x108 = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    out_root.mkdir(parents=True, exist_ok=True)

    graphiti_ready_ptr = x108 / "CURRENT_BRODY_GRAPHITI_READY_EXPORT_READONLY.txt"
    ptr = read_pointer(graphiti_ready_ptr)
    records_path = Path(ptr.get("RECORDS", ""))

    if not records_path.exists():
        raise RuntimeError(f"GRAPHITI_READY_RECORDS_NOT_FOUND={records_path}")

    cat_by_tree = {}
    categories_out = []
    for cat in CATEGORIES:
        categories_out.append(cat)
        for tid in cat["tree_ids"]:
            cat_by_tree[tid] = {
                "category_id": cat["category_id"],
                "category_name": cat["category_name"],
            }

    trees_out = []
    for tid, name, folder in TREES:
        cat = cat_by_tree[tid]
        trees_out.append({
            "tree_id": tid,
            "tree_name": name,
            "tree_folder": folder,
            "category_id": cat["category_id"],
            "category_name": cat["category_name"],
        })

    taxonomy_authority = {
        "status": "BRODY_TAXONOMY_34_TO_8_SOURCE_AUTHORITY_READY",
        "source_doc": "LES 34 ARBRES _ Architecture et Structure Cognitive Globale.docx",
        "source_truth": "34 arbres -> 8 catégories ontologiques",
        "tree_count": 34,
        "category_count": 8,
        "future_grouping_9": "NOT_APPLIED_SOURCE_GAP",
        "implemented_regroupments_v43_count": 7,
        "implemented_regroupments_v43": V43_GROUPS_IMPLEMENTED,
        "categories": categories_out,
        "trees": trees_out,
        **BOUNDARY,
    }

    taxonomy_json = out_root / "taxonomy_34_to_8_source_authority.json"
    taxonomy_json.write_text(json.dumps(taxonomy_authority, indent=2, ensure_ascii=False), encoding="utf-8")

    enriched_jsonl = out_root / "graphiti_ready_records_v164d_taxonomy_enriched.jsonl"
    hits_csv = out_root / "graphiti_ready_v164d_taxonomy_hits.csv"
    metrics_json = out_root / "graphiti_ready_v164d_taxonomy_metrics.json"
    preview_txt = out_root / "graphiti_ready_v164d_taxonomy_preview.txt"

    records_count = 0
    enriched_count = 0
    tree_hit_counts = defaultdict(int)
    category_hit_counts = defaultdict(int)
    hits_rows = []

    with records_path.open("r", encoding="utf-8-sig", errors="ignore") as src, enriched_jsonl.open("w", encoding="utf-8") as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue

            rec = json.loads(line)
            records_count += 1

            blob = norm(flatten_text(rec))
            matched = []

            for tree in trees_out:
                tid = tree["tree_id"]
                names = [
                    tree["tree_name"],
                    tree["tree_folder"],
                    tree["tree_name"].replace("’", "'"),
                    tree["tree_name"].replace("Arbre de l’", "arbre de l_"),
                    f"arbre_{tid}",
                    f"ARBRE_{tid}",
                ]

                if any(norm(x) in blob for x in names):
                    matched.append(tree)

            seen = set()
            clean_matched = []
            for m in matched:
                if m["tree_id"] not in seen:
                    seen.add(m["tree_id"])
                    clean_matched.append(m)

            if clean_matched:
                enriched_count += 1

            cats = {}
            for m in clean_matched:
                tree_hit_counts[m["tree_id"]] += 1
                category_hit_counts[m["category_id"]] += 1
                cats[m["category_id"]] = m["category_name"]
                hits_rows.append({
                    "record_id": rec.get("id", ""),
                    "title": rec.get("title", rec.get("name", "")),
                    "tree_id": m["tree_id"],
                    "tree_name": m["tree_name"],
                    "category_id": m["category_id"],
                    "category_name": m["category_name"],
                })

            rec["taxonomy_v164d"] = {
                "source_truth": "34 arbres -> 8 catégories ontologiques",
                "source_doc": "LES 34 ARBRES _ Architecture et Structure Cognitive Globale.docx",
                "matched_tree_count": len(clean_matched),
                "matched_trees": clean_matched,
                "matched_categories": [
                    {"category_id": k, "category_name": v}
                    for k, v in sorted(cats.items())
                ],
                "future_grouping_9": "NOT_APPLIED_SOURCE_GAP",
                "implemented_regroupments_v43_count": 7,
                "readonly": True,
                "memory_decision": False,
                "decision_authority": "KX108_ONLY",
            }

            dst.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with hits_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["record_id", "title", "tree_id", "tree_name", "category_id", "category_name"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(hits_rows)

    metrics = {
        "status": "BRODY_GRAPHITI_READY_V164D_TAXONOMY_34_TO_8_PASS",
        "date": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "records_source": str(records_path),
        "records_count": records_count,
        "taxonomy_enriched_records_count": enriched_count,
        "taxonomy_hits_count": len(hits_rows),
        "tree_count": 34,
        "category_count": 8,
        "future_grouping_9": "NOT_APPLIED_SOURCE_GAP",
        "implemented_regroupments_v43_count": 7,
        "tree_hit_counts": dict(sorted(tree_hit_counts.items())),
        "category_hit_counts": dict(sorted(category_hit_counts.items())),
        "taxonomy_authority": str(taxonomy_json),
        "enriched_records": str(enriched_jsonl),
        "hits_csv": str(hits_csv),
        "taxonomy_authority_sha256": sha256_file(taxonomy_json),
        "enriched_records_sha256": sha256_file(enriched_jsonl),
        **BOUNDARY,
    }

    metrics_json.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# BRODY GRAPHITI READY V164D — 34 arbres -> 8 catégories")
    lines.append("")
    lines.append(f"- status: {metrics['status']}")
    lines.append(f"- records_count: {records_count}")
    lines.append(f"- taxonomy_enriched_records_count: {enriched_count}")
    lines.append(f"- taxonomy_hits_count: {len(hits_rows)}")
    lines.append(f"- category_count: 8")
    lines.append(f"- tree_count: 34")
    lines.append(f"- future_grouping_9: NOT_APPLIED_SOURCE_GAP")
    lines.append(f"- implemented_regroupments_v43_count: 7")
    lines.append(f"- memory_decision: false")
    lines.append(f"- decision_authority: KX108_ONLY")
    lines.append("")
    lines.append("## Category hit counts")
    for k, v in sorted(category_hit_counts.items()):
        cat_name = next(c["category_name"] for c in categories_out if c["category_id"] == k)
        lines.append(f"- {k} — {cat_name}: {v}")
    preview_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

    current = x108 / "CURRENT_BRODY_GRAPHITI_READY_V164D_TAXONOMY_34_TO_8.txt"
    current.write_text(
        "\n".join([
            f"CURRENT_BRODY_GRAPHITI_READY_V164D_TAXONOMY_34_TO_8={out_root}",
            f"TAXONOMY_AUTHORITY={taxonomy_json}",
            f"ENRICHED_RECORDS={enriched_jsonl}",
            f"HITS_CSV={hits_csv}",
            f"METRICS={metrics_json}",
            f"PREVIEW={preview_txt}",
            "STATUS=BRODY_GRAPHITI_READY_V164D_TAXONOMY_34_TO_8_PASS",
            "SOURCE_TRUTH=34_ARBRES_TO_8_CATEGORIES_ONTOLOGIQUES",
            "FUTURE_GROUPING_9=NOT_APPLIED_SOURCE_GAP",
            "IMPLEMENTED_REGROUPMENTS_V43_COUNT=7",
            "MEMORY_DECISION=false",
            "DECISION_AUTHORITY=KX108_ONLY",
            "KERNEL_MUTATION=false",
            "X108_MERGE=false",
            "NEXT=VERIFY_AND_COMMIT_V164D_TAXONOMY_MAPPER",
        ]) + "\n",
        encoding="utf-8"
    )

    print(json.dumps(metrics, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
