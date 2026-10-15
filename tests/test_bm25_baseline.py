#!/usr/bin/env python3
"""Deterministic checks for the BM25 baseline implementation."""

import importlib.util
from pathlib import Path


path = Path("research/benchmark/bm25_baseline.py")
spec = importlib.util.spec_from_file_location("bm25_baseline", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    documents = [
        ("A", "employee chemical training initial assignment"),
        ("B", "annual injury summary posting"),
        ("C", "equipment inspection and maintenance"),
    ]
    index = module.BM25Index(documents, k1=1.2, b=0.75)
    result = index.search("new employee chemical training", top_k=3)
    assert result[0]["id"] == "A"
    assert result[0]["score"] > result[1]["score"]
    assert [r["rank"] for r in result] == [1, 2, 3]
    assert index.search("unseen-token", top_k=2)[0]["id"] == "A", "zero-score ties must be deterministic"
    print("PASS: BM25 baseline ranks matching text first and resolves ties deterministically")


if __name__ == "__main__":
    main()
