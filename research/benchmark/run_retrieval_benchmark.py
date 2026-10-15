#!/usr/bin/env python3
"""Run deterministic BM25, dense, and hybrid retrieval on scenario text."""

import argparse
import csv
import hashlib
import importlib.util
import json
import platform
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bm25 = load_module("bm25_baseline", "bm25_baseline.py")
dense = load_module("dense_baseline", "dense_baseline.py")
hybrid = load_module("hybrid_baseline", "hybrid_baseline.py")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=Path, default=HERE / "scenarios_PROVISIONAL.csv")
    parser.add_argument("--release", default="v1.2.0")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--k1", type=float, default=1.5)
    parser.add_argument("--b", type=float, default=0.75)
    parser.add_argument("--rrf-k", type=float, default=60.0)
    parser.add_argument("--component-k", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=HERE / "runs" / "retrieval_provisional")
    args = parser.parse_args()

    dataset_path = ROOT / "data" / "releases" / args.release / "all_requirements.json"
    records = json.loads(dataset_path.read_text(encoding="utf-8"))["requirements"]
    by_id = {record["id"]: record for record in records}
    fields = ["requirement_text", "source_text_excerpt"]
    documents = [(record["id"], bm25.record_text(record, fields)) for record in records]
    bm25_index = bm25.BM25Index(documents, args.k1, args.b)
    dense_index = dense.DenseIndex(documents, args.model)
    with args.scenarios.open(encoding="utf-8-sig", newline="") as stream:
        scenarios = list(csv.DictReader(stream))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {name: [] for name in ["bm25", "dense", "hybrid"]}
    for scenario in scenarios:
        query = scenario["scenario_text"] + "\n" + scenario["organization_context"]
        bm25_results = bm25_index.search(query, args.component_k)
        dense_results = dense_index.search(query, args.component_k)
        hybrid_results = hybrid.reciprocal_rank_fusion(
            [bm25_results, dense_results], args.rrf_k
        )[: args.top_k]
        rankings = {
            "bm25": bm25_results[: args.top_k],
            "dense": dense_results[: args.top_k],
            "hybrid": hybrid_results,
        }
        for system_name, results in rankings.items():
            ranked_ids = [item["id"] for item in results]
            selected = [by_id[record_id] for record_id in ranked_ids]
            outputs[system_name].append({
                "scenario_id": scenario["scenario_id"],
                "ranked_requirement_ids": ranked_ids,
                "predicted_requirement_ids": ranked_ids,
                "predicted_trigger_labels": sorted({r["workflow_trigger"] for r in selected}),
                "predicted_evidence_labels": sorted({r["audit_evidence_type"] for r in selected}),
                "predicted_citations": sorted({r["provenance"]["source_clause"] for r in selected}),
                "predicted_decision": "answer",
                "scores": results,
            })

    for system_name, rows in outputs.items():
        path = args.output_dir / f"{system_name}_predictions.jsonl"
        path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")

    import sentence_transformers
    import torch
    manifest = {
        "status": "PROVISIONAL_DEVELOPMENT_RUN_NOT_FOR_CONFIRMATORY_CLAIMS",
        "scenario_file": str(args.scenarios).replace("\\", "/"),
        "scenario_sha256": sha256(args.scenarios),
        "dataset_file": str(dataset_path).replace("\\", "/"),
        "dataset_sha256": sha256(dataset_path),
        "release": args.release,
        "document_fields": fields,
        "bm25": {"k1": args.k1, "b": args.b},
        "dense": {"model": args.model, "similarity": "cosine_normalized_dot_product"},
        "hybrid": {"fusion": "reciprocal_rank_fusion", "rrf_k": args.rrf_k},
        "component_k": args.component_k,
        "top_k": args.top_k,
        "python": platform.python_version(),
        "sentence_transformers": sentence_transformers.__version__,
        "torch": torch.__version__,
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(scenarios)} scenarios x 3 retrieval systems to {args.output_dir}")


if __name__ == "__main__":
    main()
