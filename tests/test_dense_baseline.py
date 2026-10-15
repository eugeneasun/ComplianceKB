#!/usr/bin/env python3
"""Deterministic checks for the dense-embedding baseline implementation.

Requires sentence-transformers and a downloaded embedding model (skips
with a clear message if unavailable, rather than failing the whole suite
in an environment without them).
"""

import importlib.util
import sys
from pathlib import Path


path = Path("research/benchmark/dense_baseline.py")
spec = importlib.util.spec_from_file_location("dense_baseline", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

MODEL = "all-MiniLM-L6-v2"


def main():
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        print("SKIPPED: sentence-transformers not installed")
        return

    documents = [
        ("A", "employee chemical training initial assignment"),
        ("B", "annual injury summary posting deadline"),
        ("C", "equipment inspection and maintenance schedule"),
    ]
    try:
        index = module.DenseIndex(documents, MODEL)
    except Exception as exc:  # model not downloaded / no network in this environment
        print(f"SKIPPED: could not load model {MODEL} ({exc})")
        return

    result = index.search("training for new employees on hazardous chemicals", top_k=3)
    assert [r["rank"] for r in result] == [1, 2, 3]
    assert result[0]["id"] == "A", f"expected the chemical-training document to rank first, got {result[0]['id']}"
    assert result[0]["score"] >= result[1]["score"] >= result[2]["score"]
    # Cosine similarity of normalized embeddings must fall in [-1, 1] (with float slack).
    assert all(-1.0001 <= r["score"] <= 1.0001 for r in result)

    # Re-running search with the same index and query must be exactly reproducible.
    repeat = index.search("training for new employees on hazardous chemicals", top_k=3)
    assert [r["id"] for r in repeat] == [r["id"] for r in result]
    assert [r["score"] for r in repeat] == [r["score"] for r in result]

    print(f"PASS: dense baseline ({MODEL}) ranks the semantically closest document first and is reproducible")


if __name__ == "__main__":
    main()
