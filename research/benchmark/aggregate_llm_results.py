#!/usr/bin/env python3
"""Aggregate saved LLM responses into reproducible development-set metrics."""

import argparse
import csv
import json
import random
from pathlib import Path

from evaluate_benchmark import parse_set, prf, retrieval_scores

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SYSTEMS = ["raw_full", "bm25", "dense", "hybrid", "rkm_agent"]
PROVIDERS = ["openai", "anthropic"]
FIELDS = {
    "requirements": ("gold_requirement_ids", "predicted_requirement_ids"),
    "triggers": ("gold_trigger_labels", "predicted_trigger_labels"),
    "evidence": ("gold_evidence_labels", "predicted_evidence_labels"),
    "citations": ("gold_citations", "predicted_citations"),
}


def mean(values):
    return sum(values) / len(values) if values else 0.0


def percentile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    low = int(position)
    high = min(low + 1, len(values) - 1)
    fraction = position - low
    return values[low] * (1 - fraction) + values[high] * fraction


def bootstrap_ci(values, seed=20260927, iterations=10000):
    rng = random.Random(seed)
    n = len(values)
    samples = [mean([values[rng.randrange(n)] for _ in range(n)]) for _ in range(iterations)]
    return [percentile(samples, 0.025), percentile(samples, 0.975)]


def paired_bootstrap_delta(left, right, seed=20260927, iterations=10000):
    if len(left) != len(right):
        raise ValueError("Paired vectors must have the same length")
    differences = [a - b for a, b in zip(left, right)]
    return mean(differences), bootstrap_ci(differences, seed=seed, iterations=iterations)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, default=HERE / "runs" / "llm_development_20260927")
    parser.add_argument("--scenarios", type=Path, default=HERE / "scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv")
    parser.add_argument("--retrieval-dir", type=Path, default=HERE / "runs" / "retrieval_provisional")
    parser.add_argument("--output-dir", type=Path, default=HERE / "runs" / "llm_development_20260927" / "analysis")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with args.scenarios.open(encoding="utf-8-sig", newline="") as stream:
        gold = {row["scenario_id"]: row for row in csv.DictReader(stream)}
    if len(gold) != 24:
        raise SystemExit(f"Expected 24 scenarios, found {len(gold)}")

    rankings = {}
    for name in ["bm25", "dense", "hybrid"]:
        rankings[name] = {}
        with (args.retrieval_dir / f"{name}_predictions.jsonl").open(encoding="utf-8") as stream:
            for line in stream:
                row = json.loads(line)
                rankings[name][row["scenario_id"]] = row["ranked_requirement_ids"]
    records = json.loads((ROOT / "data" / "releases" / "v1.2.0" / "all_requirements.json").read_text(encoding="utf-8"))["requirements"]
    all_ids = [record["id"] for record in records]

    summaries = []
    per_scenario = []
    for provider in PROVIDERS:
        for system in SYSTEMS:
            condition_rows = []
            predictions = []
            for scenario_id, gold_row in gold.items():
                path = args.run_dir / provider / system / f"{scenario_id}.json"
                result = json.loads(path.read_text(encoding="utf-8"))
                if result.get("status") != "ok":
                    raise SystemExit(f"Non-success result: {path}")
                answer = result["answer"]
                retrieval_name = "hybrid" if system == "rkm_agent" else system
                ranking = all_ids if system == "raw_full" else rankings[retrieval_name][scenario_id]
                prediction = {"scenario_id": scenario_id, **answer, "ranked_requirement_ids": ranking}
                predictions.append(prediction)
                scored = {
                    "provider": provider,
                    "model": result["model"],
                    "system": system,
                    "scenario_id": scenario_id,
                    "decision_accuracy": float(answer["predicted_decision"] == gold_row["gold_decision"]),
                    "estimated_cost_usd": result["estimated_cost_usd"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "elapsed_seconds": result["elapsed_seconds"],
                    "duplicate_output_field_count": len(result.get("duplicate_output_items", {})),
                }
                for label, (gold_field, prediction_field) in FIELDS.items():
                    precision, recall, f1, exact = prf(parse_set(gold_row[gold_field]), set(answer[prediction_field]))
                    scored[f"{label}_precision"] = precision
                    scored[f"{label}_recall"] = recall
                    scored[f"{label}_f1"] = f1
                    scored[f"{label}_exact_match"] = exact
                if system == "raw_full":
                    retrieval_recall, reciprocal_rank, ndcg = None, None, None
                else:
                    retrieval_recall, reciprocal_rank, ndcg = retrieval_scores(
                        parse_set(gold_row["gold_requirement_ids"]), ranking, 10
                    )
                scored.update({"retrieval_recall_at_10": retrieval_recall, "retrieval_mrr_at_10": reciprocal_rank, "retrieval_ndcg_at_10": ndcg})
                condition_rows.append(scored)
                per_scenario.append(scored)

            prediction_path = args.output_dir / f"{provider}__{system}_predictions.jsonl"
            prediction_path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in predictions), encoding="utf-8")
            summary = {
                "provider": provider,
                "model": condition_rows[0]["model"],
                "system": system,
                "n": len(condition_rows),
                "total_cost_usd": sum(row["estimated_cost_usd"] for row in condition_rows),
                "total_input_tokens": sum(row["input_tokens"] for row in condition_rows),
                "total_output_tokens": sum(row["output_tokens"] for row in condition_rows),
                "mean_latency_seconds": mean([row["elapsed_seconds"] for row in condition_rows]),
                "duplicate_output_field_count": sum(row["duplicate_output_field_count"] for row in condition_rows),
            }
            reported = [
                "requirements_f1", "requirements_exact_match", "triggers_f1", "triggers_exact_match",
                "evidence_f1", "evidence_exact_match", "citations_f1", "citations_exact_match",
                "decision_accuracy", "retrieval_recall_at_10", "retrieval_mrr_at_10", "retrieval_ndcg_at_10",
            ]
            for metric in reported:
                values = [row[metric] for row in condition_rows if row[metric] is not None]
                summary[metric] = mean(values) if values else None
                if metric in {"requirements_f1", "triggers_f1", "evidence_f1", "citations_f1", "decision_accuracy"}:
                    summary[metric + "_bootstrap_95ci"] = bootstrap_ci(values)
            summaries.append(summary)

    comparisons = []
    for provider in PROVIDERS:
        indexed = {
            (row["system"], row["scenario_id"]): row
            for row in per_scenario if row["provider"] == provider
        }
        comparison = {"provider": provider, "contrast": "rkm_agent_minus_hybrid", "n": len(gold)}
        for metric in ["requirements_f1", "triggers_f1", "evidence_f1", "citations_f1", "decision_accuracy"]:
            rkm = [indexed[("rkm_agent", scenario_id)][metric] for scenario_id in gold]
            hybrid = [indexed[("hybrid", scenario_id)][metric] for scenario_id in gold]
            delta, interval = paired_bootstrap_delta(rkm, hybrid)
            differences = [a - b for a, b in zip(rkm, hybrid)]
            comparison[metric + "_mean_delta"] = delta
            comparison[metric + "_paired_bootstrap_95ci"] = interval
            comparison[metric + "_wins_ties_losses"] = [
                sum(value > 0 for value in differences),
                sum(value == 0 for value in differences),
                sum(value < 0 for value in differences),
            ]
        comparisons.append(comparison)

    (args.output_dir / "development_metrics.json").write_text(
        json.dumps({
            "status": "EXPLORATORY_AI_ASSISTED_DEVELOPMENT_SET",
            "independent_confirmatory": False,
            "bootstrap_iterations": 10000,
            "bootstrap_seed": 20260927,
            "summaries": summaries,
            "paired_comparisons": comparisons,
            "per_scenario": per_scenario,
        }, indent=2) + "\n",
        encoding="utf-8",
    )
    table_fields = [
        "provider", "model", "system", "n", "requirements_f1", "requirements_exact_match",
        "triggers_f1", "evidence_f1", "citations_f1", "decision_accuracy",
        "retrieval_recall_at_10", "total_cost_usd", "mean_latency_seconds",
    ]
    with (args.output_dir / "development_metrics_summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=table_fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in table_fields} for row in summaries)
    (args.output_dir / "paired_rkm_vs_hybrid.json").write_text(json.dumps(comparisons, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summaries": summaries, "paired_comparisons": comparisons}, indent=2))


if __name__ == "__main__":
    main()
