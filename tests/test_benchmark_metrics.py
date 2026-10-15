#!/usr/bin/env python3
"""Unit checks for benchmark set and ranking metrics."""

import importlib.util
from pathlib import Path


path = Path("research/benchmark/evaluate_benchmark.py")
spec = importlib.util.spec_from_file_location("evaluate_benchmark", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main():
    assert module.prf({"A", "B"}, {"B", "C"}) == (0.5, 0.5, 0.5, 0.0)
    assert module.prf(set(), set()) == (1.0, 1.0, 1.0, 1.0)
    recall, rr, ndcg = module.retrieval_scores({"B"}, ["A", "B", "C"], 3)
    assert recall == 1.0 and rr == 0.5
    assert 0.0 < ndcg < 1.0
    recall, rr, ndcg = module.retrieval_scores({"Z"}, ["A", "B"], 2)
    assert (recall, rr, ndcg) == (0.0, 0.0, 0.0)
    print("PASS: benchmark metrics return expected exact and ranking scores")


if __name__ == "__main__":
    main()
