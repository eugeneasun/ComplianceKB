#!/usr/bin/env python3
"""Deterministic checks for the RRF hybrid baseline's fusion logic.

Exercises reciprocal_rank_fusion directly with hand-built rank lists (no
model loading required) so this test runs even without sentence-transformers
installed, plus one integration check that skips cleanly if it is missing.
"""

import importlib.util
from pathlib import Path


path = Path("research/benchmark/hybrid_baseline.py")
spec = importlib.util.spec_from_file_location("hybrid_baseline", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_fusion_logic():
    bm25_ranked = [{"id": "A", "rank": 1}, {"id": "B", "rank": 2}, {"id": "C", "rank": 3}]
    dense_ranked = [{"id": "B", "rank": 1}, {"id": "A", "rank": 2}]
    fused = module.reciprocal_rank_fusion([bm25_ranked, dense_ranked], rrf_k=60)
    # A: 1/61 + 1/62 = 0.03251...  B: 1/62 + 1/61 = same as A (tie) -> broken by id order
    ids = [f["id"] for f in fused]
    assert set(ids) == {"A", "B", "C"}
    # A and B are tied (each appears once at rank 1 and once at rank 2 across the two
    # systems), so the deterministic id-order tiebreak must put A before B.
    assert ids[0] == "A" and ids[1] == "B"
    # C only appears in one list, at rank 3, so it must score lower and rank last.
    assert ids[-1] == "C"
    assert [f["rank"] for f in fused] == [1, 2, 3]

    # A document absent from every list must not appear in the fused output.
    fused_empty = module.reciprocal_rank_fusion([[], []], rrf_k=60)
    assert fused_empty == []
    print("PASS: reciprocal_rank_fusion combines ranks deterministically and ties break by id")


def test_integration():
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        print("SKIPPED: sentence-transformers not installed, skipping end-to-end hybrid check")
        return
    import json
    import tempfile
    from pathlib import Path as P

    dataset = {
        "requirements": [
            {"id": "A", "requirement_text": "employee chemical training initial assignment",
             "provenance": {"source_text_excerpt": "employee chemical training initial assignment"}},
            {"id": "B", "requirement_text": "annual injury summary posting deadline",
             "provenance": {"source_text_excerpt": "annual injury summary posting deadline"}},
            {"id": "C", "requirement_text": "equipment inspection and maintenance schedule",
             "provenance": {"source_text_excerpt": "equipment inspection and maintenance schedule"}},
        ]
    }
    with tempfile.TemporaryDirectory() as tmp:
        release_dir = P(tmp) / "data" / "releases" / "v-test"
        release_dir.mkdir(parents=True)
        (release_dir / "all_requirements.json").write_text(json.dumps(dataset), encoding="utf-8")
        import os
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            documents = [(r["id"], module.bm25_baseline.record_text(r, ["requirement_text"])) for r in dataset["requirements"]]
            bm25_index = module.bm25_baseline.BM25Index(documents, k1=1.2, b=0.75)
            bm25_results = bm25_index.search("chemical training new employee", top_k=3)
            try:
                dense_index = module.dense_baseline.DenseIndex(documents, "all-MiniLM-L6-v2")
            except Exception as exc:
                print(f"SKIPPED: could not load embedding model ({exc})")
                return
            dense_results = dense_index.search("chemical training new employee", top_k=3)
            fused = module.reciprocal_rank_fusion([bm25_results, dense_results], rrf_k=60)
            assert fused[0]["id"] == "A"
        finally:
            os.chdir(cwd)
    print("PASS: hybrid baseline end-to-end fuses BM25 and dense results")


def main():
    test_fusion_logic()
    test_integration()


if __name__ == "__main__":
    main()
