#!/usr/bin/env python3
"""Deterministic hybrid (BM25 + dense) retrieval baseline for a frozen ComplianceKB release.

Fusion method: Reciprocal Rank Fusion (RRF), the standard rank-only fusion
method from Cormack, Clarke & Buettcher (SIGIR 2009). RRF was chosen over a
weighted score sum because BM25 and cosine-similarity scores are on
different, non-comparable scales, so min-max normalizing them before a
weighted sum would silently introduce an extra, unrecorded design decision;
RRF instead combines only each system's *rank* of a document, which needs
no cross-system score calibration. Every parameter that affects the result
(k1, b, embedding model, rrf_k, per-system top_k, final top_k) is a required
argument, per the protocol's requirement to document "Fusion method and
weights, component settings, k".

    RRF(d) = sum over systems s of 1 / (rrf_k + rank_s(d))

A document not retrieved by a given system in its own top_k contributes 0
for that system (it is not penalized further, and it is not treated as
tied for last place).
"""

import argparse
import importlib.util
import json
from pathlib import Path


def _load(module_name, relative_path):
    path = Path(__file__).resolve().parent / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bm25_baseline = _load("bm25_baseline", "bm25_baseline.py")
dense_baseline = _load("dense_baseline", "dense_baseline.py")


def reciprocal_rank_fusion(ranked_lists, rrf_k):
    """ranked_lists: list of lists of dicts with an 'id' and 'rank' key (rank starts at 1)."""
    scores = {}
    for ranked_list in ranked_lists:
        for entry in ranked_list:
            scores[entry["id"]] = scores.get(entry["id"], 0.0) + 1.0 / (rrf_k + entry["rank"])
    ordered_ids = sorted(scores, key=lambda doc_id: (-scores[doc_id], doc_id))
    return [
        {"id": doc_id, "score": scores[doc_id], "rank": rank}
        for rank, doc_id in enumerate(ordered_ids, 1)
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--release", default="v1.2.0")
    parser.add_argument("--fields", nargs="+", required=True, choices=["requirement_text", "source_text_excerpt"])
    parser.add_argument("--k1", type=float, required=True, help="BM25 k1")
    parser.add_argument("--b", type=float, required=True, help="BM25 b")
    parser.add_argument("--model", required=True, help="sentence-transformers model name")
    parser.add_argument("--component-top-k", type=int, required=True, help="top_k retrieved by each component system before fusion")
    parser.add_argument("--rrf-k", type=float, required=True, help="RRF rank-damping constant (commonly 60)")
    parser.add_argument("--top-k", type=int, required=True, help="final fused top_k to return")
    args = parser.parse_args()
    if args.top_k <= 0 or args.component_top_k <= 0:
        raise SystemExit("--top-k and --component-top-k must be positive")
    if args.rrf_k <= 0:
        raise SystemExit("--rrf-k must be positive")

    path = Path("data/releases") / args.release / "all_requirements.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    documents = [(r["id"], bm25_baseline.record_text(r, args.fields)) for r in dataset["requirements"]]

    bm25_index = bm25_baseline.BM25Index(documents, args.k1, args.b)
    bm25_results = bm25_index.search(args.query, args.component_top_k)

    dense_index = dense_baseline.DenseIndex(documents, args.model)
    dense_results = dense_index.search(args.query, args.component_top_k)

    fused = reciprocal_rank_fusion([bm25_results, dense_results], args.rrf_k)[: args.top_k]

    output = {
        "release": args.release,
        "query": args.query,
        "fields": args.fields,
        "fusion_method": "reciprocal_rank_fusion",
        "rrf_k": args.rrf_k,
        "component_top_k": args.component_top_k,
        "components": {
            "bm25": {"k1": args.k1, "b": args.b},
            "dense": {"model": args.model, "similarity": "cosine"},
        },
        "top_k": args.top_k,
        "results": fused,
        "component_results": {"bm25": bm25_results, "dense": dense_results},
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
