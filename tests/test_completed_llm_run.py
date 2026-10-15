#!/usr/bin/env python3
"""Regression checks for the frozen 2026-09-27 development run."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "research" / "benchmark"
RUN = BENCH / "runs" / "llm_development_20260927"
SCENARIOS = BENCH / "scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv"
DATASET = ROOT / "data" / "releases" / "v1.2.0" / "all_requirements.json"
PROVIDERS = ["openai", "anthropic"]
SYSTEMS = ["raw_full", "bm25", "dense", "hybrid", "rkm_agent"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
assert manifest["status"] == "HUMAN_CONFIRMED_AI_ASSISTED_DEVELOPMENT_RUN_NOT_INDEPENDENT_CONFIRMATORY"
assert manifest["scenario_sha256"] == sha256(SCENARIOS)
assert manifest["dataset_sha256"] == sha256(DATASET)

costs = {provider: 0.0 for provider in PROVIDERS}
count = 0
for provider in PROVIDERS:
    for system in SYSTEMS:
        files = sorted((RUN / provider / system).glob("DEV-*.json"))
        assert len(files) == 24, (provider, system, len(files))
        for path in files:
            row = json.loads(path.read_text(encoding="utf-8"))
            assert row["status"] == "ok", path
            assert not row.get("duplicate_output_items"), path
            assert row["provider"] == provider and row["system"] == system
            costs[provider] += row["estimated_cost_usd"]
            count += 1
assert count == 240
assert all(cost < 9.50 for cost in costs.values()), costs

metrics = json.loads((RUN / "analysis" / "development_metrics.json").read_text(encoding="utf-8"))
assert metrics["status"] == "EXPLORATORY_AI_ASSISTED_DEVELOPMENT_SET"
assert metrics["independent_confirmatory"] is False
assert len(metrics["summaries"]) == 10
assert len(metrics["paired_comparisons"]) == 2
print(f"PASS: 240/240 frozen calls; costs={costs}; exploratory metrics and hashes verified")
