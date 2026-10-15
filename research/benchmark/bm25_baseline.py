#!/usr/bin/env python3
"""Deterministic BM25 retrieval baseline for a frozen ComplianceKB release."""

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text):
    return TOKEN_RE.findall(text.lower())


class BM25Index:
    def __init__(self, documents, k1, b):
        if k1 <= 0 or not 0 <= b <= 1:
            raise ValueError("k1 must be positive and b must be in [0, 1]")
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.tokens = [tokenize(text) for _, text in documents]
        self.lengths = [len(tokens) for tokens in self.tokens]
        self.average_length = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0
        self.term_frequencies = [Counter(tokens) for tokens in self.tokens]
        document_frequency = Counter()
        for tokens in self.tokens:
            document_frequency.update(set(tokens))
        n = len(documents)
        self.idf = {
            term: math.log(1.0 + (n - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query, top_k):
        query_terms = tokenize(query)
        scores = []
        for index, ((record_id, _), frequencies, length) in enumerate(
            zip(self.documents, self.term_frequencies, self.lengths)
        ):
            score = 0.0
            for term in query_terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                normalization = frequency + self.k1 * (
                    1.0 - self.b + self.b * length / self.average_length
                )
                score += self.idf.get(term, 0.0) * frequency * (self.k1 + 1.0) / normalization
            scores.append((record_id, score, index))
        scores.sort(key=lambda item: (-item[1], item[0]))
        return [{"id": record_id, "score": score, "rank": rank} for rank, (record_id, score, _) in enumerate(scores[:top_k], 1)]


def record_text(record, fields):
    values = []
    for field in fields:
        if field == "source_text_excerpt":
            values.append(record["provenance"]["source_text_excerpt"])
        else:
            values.append(str(record[field]))
    return "\n".join(values)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--release", default="v1.2.0")
    parser.add_argument("--fields", nargs="+", required=True, choices=["requirement_text", "source_text_excerpt"])
    parser.add_argument("--k1", type=float, required=True)
    parser.add_argument("--b", type=float, required=True)
    parser.add_argument("--top-k", type=int, required=True)
    args = parser.parse_args()
    if args.top_k <= 0:
        raise SystemExit("--top-k must be positive")
    path = Path("data/releases") / args.release / "all_requirements.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    documents = [(r["id"], record_text(r, args.fields)) for r in dataset["requirements"]]
    index = BM25Index(documents, args.k1, args.b)
    output = {
        "release": args.release, "query": args.query, "fields": args.fields,
        "k1": args.k1, "b": args.b, "top_k": args.top_k,
        "results": index.search(args.query, args.top_k),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
