#!/usr/bin/env python3
"""Score frozen benchmark gold CSV against system predictions in JSONL format."""

import argparse
import csv
import json
import math
from pathlib import Path


def parse_set(value):
    return {item.strip() for item in (value or "").split("|") if item.strip()}


def prf(gold, predicted):
    tp = len(gold & predicted)
    precision = tp / len(predicted) if predicted else (1.0 if not gold else 0.0)
    recall = tp / len(gold) if gold else (1.0 if not predicted else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1, float(gold == predicted)


def retrieval_scores(relevant, ranking, k):
    top = ranking[:k]
    recall = len(relevant & set(top)) / len(relevant) if relevant else 1.0
    rr = next((1.0 / (i + 1) for i, item in enumerate(top) if item in relevant), 0.0)
    dcg = sum((1.0 if item in relevant else 0.0) / math.log2(i + 2) for i, item in enumerate(top))
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    ndcg = dcg / ideal if ideal else 1.0
    return recall, rr, ndcg


def mean(values):
    return sum(values) / len(values) if values else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gold", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.k <= 0:
        raise SystemExit("--k must be positive")

    with args.gold.open(encoding="utf-8-sig", newline="") as f:
        gold_rows = list(csv.DictReader(f))
    predictions = {}
    with args.predictions.open(encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            scenario_id = row.get("scenario_id")
            if not scenario_id or scenario_id in predictions:
                raise SystemExit(f"Invalid or duplicate scenario_id at prediction line {line_number}")
            predictions[scenario_id] = row

    gold_ids = [row["scenario_id"] for row in gold_rows]
    if len(gold_ids) != len(set(gold_ids)) or not gold_ids:
        raise SystemExit("Gold file must contain at least one unique scenario_id")
    if set(gold_ids) != set(predictions):
        missing = sorted(set(gold_ids) - set(predictions))
        extra = sorted(set(predictions) - set(gold_ids))
        raise SystemExit(f"Prediction coverage mismatch; missing={missing}, extra={extra}")

    mappings = {
        "requirements": ("gold_requirement_ids", "predicted_requirement_ids"),
        "triggers": ("gold_trigger_labels", "predicted_trigger_labels"),
        "evidence": ("gold_evidence_labels", "predicted_evidence_labels"),
        "citations": ("gold_citations", "predicted_citations"),
    }
    per_scenario = []
    aggregates = {name: {m: [] for m in ["precision", "recall", "f1", "exact_match"]} for name in mappings}
    retrieval = {m: [] for m in ["recall_at_k", "reciprocal_rank", "ndcg_at_k"]}
    decisions = []
    for gold in gold_rows:
        pred = predictions[gold["scenario_id"]]
        result = {"scenario_id": gold["scenario_id"]}
        for name, (gold_field, pred_field) in mappings.items():
            scores = prf(parse_set(gold[gold_field]), set(pred.get(pred_field, [])))
            for metric, value in zip(["precision", "recall", "f1", "exact_match"], scores):
                aggregates[name][metric].append(value)
                result[f"{name}_{metric}"] = value
        relevant = parse_set(gold["gold_requirement_ids"])
        rank_scores = retrieval_scores(relevant, pred.get("ranked_requirement_ids", []), args.k)
        for metric, value in zip(retrieval, rank_scores):
            retrieval[metric].append(value)
            result[metric] = value
        decision_correct = float(gold["gold_decision"] == pred.get("predicted_decision"))
        decisions.append(decision_correct)
        result["decision_accuracy"] = decision_correct
        per_scenario.append(result)

    summary = {
        "n": len(gold_rows), "k": args.k,
        **{f"{name}_{metric}": mean(values) for name, metrics in aggregates.items() for metric, values in metrics.items()},
        **{metric: mean(values) for metric, values in retrieval.items()},
        "decision_accuracy": mean(decisions),
    }
    output = {"summary": summary, "per_scenario": per_scenario}
    text = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
