#!/usr/bin/env python3
"""Deterministic dense-embedding retrieval baseline for a frozen ComplianceKB release.

Mirrors bm25_baseline.py's CLI and output shape so both baselines can be
compared under the same benchmark harness (research/benchmark/BENCHMARK_PROTOCOL_DRAFT.md).
All parameters that affect ranking are required arguments -- nothing is
silently defaulted -- so a frozen run can be reproduced exactly from its
recorded command line.

Determinism note: sentence-transformers encoding on CPU with no dropout
(eval mode, the library default for .encode()) is deterministic for a
fixed model version and fixed input order; there is no random seed to
record. The model name/version and library versions are included in the
output for exact reproducibility, per the protocol's requirement to
document "Embedding model/version, pooling, index, similarity, k".
"""

import argparse
import json
from pathlib import Path


def record_text(record, fields):
    values = []
    for field in fields:
        if field == "source_text_excerpt":
            values.append(record["provenance"]["source_text_excerpt"])
        else:
            values.append(str(record[field]))
    return "\n".join(values)


class DenseIndex:
    def __init__(self, documents, model_name):
        from sentence_transformers import SentenceTransformer
        import numpy as np

        self.np = np
        self.documents = documents
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        texts = [text for _, text in documents]
        embeddings = self.model.encode(
            texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True
        )
        self.embeddings = embeddings

    def search(self, query, top_k):
        np = self.np
        query_embedding = self.model.encode(
            [query], convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True
        )[0]
        # Both sides are L2-normalized, so the dot product is cosine similarity.
        scores = self.embeddings @ query_embedding
        order = sorted(
            range(len(self.documents)),
            key=lambda i: (-float(scores[i]), self.documents[i][0]),
        )
        return [
            {"id": self.documents[i][0], "score": float(scores[i]), "rank": rank}
            for rank, i in enumerate(order[:top_k], 1)
        ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--release", default="v1.2.0")
    parser.add_argument("--fields", nargs="+", required=True, choices=["requirement_text", "source_text_excerpt"])
    parser.add_argument("--model", required=True, help="sentence-transformers model name, e.g. all-MiniLM-L6-v2")
    parser.add_argument("--top-k", type=int, required=True)
    args = parser.parse_args()
    if args.top_k <= 0:
        raise SystemExit("--top-k must be positive")

    import sentence_transformers
    import torch

    path = Path("data/releases") / args.release / "all_requirements.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    documents = [(r["id"], record_text(r, args.fields)) for r in dataset["requirements"]]
    index = DenseIndex(documents, args.model)
    output = {
        "release": args.release,
        "query": args.query,
        "fields": args.fields,
        "model": args.model,
        "similarity": "cosine (normalized dot product)",
        "pooling": "sentence-transformers default (mean pooling for MiniLM-family models)",
        "sentence_transformers_version": sentence_transformers.__version__,
        "torch_version": torch.__version__,
        "top_k": args.top_k,
        "results": index.search(args.query, args.top_k),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
