#!/usr/bin/env python3
"""Offline checks for benchmark context isolation and output schema."""

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "research" / "benchmark" / "run_llm_benchmark.py"
spec = importlib.util.spec_from_file_location("run_llm_benchmark", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

records = json.loads((ROOT / "data" / "releases" / "v1.2.0" / "all_requirements.json").read_text(encoding="utf-8"))["requirements"]
with (ROOT / "research" / "benchmark" / "scenarios_PROVISIONAL.csv").open(encoding="utf-8-sig", newline="") as stream:
    scenario = next(csv.DictReader(stream))

rankings = {}
for name in ["bm25", "dense", "hybrid"]:
    rankings[name] = {}
    path = ROOT / "research" / "benchmark" / "runs" / "retrieval_provisional" / f"{name}_predictions.jsonl"
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        rankings[name][row["scenario_id"]] = row["ranked_requirement_ids"]

hybrid_context, hybrid_ids = module.build_context("hybrid", records, rankings, scenario["scenario_id"])
rkm_context, rkm_ids = module.build_context("rkm_agent", records, rankings, scenario["scenario_id"])
assert hybrid_ids == rkm_ids, "hybrid and RKM conditions must receive the same candidate IDs"
assert "workflow_trigger" not in hybrid_context and "audit_evidence_type" not in hybrid_context
assert "workflow_trigger" in rkm_context and "audit_evidence_type" in rkm_context

prompt = module.build_prompt("rkm_agent", scenario, rkm_context)
assert "gold_requirement_ids" not in prompt and "gold_rationale" not in prompt
assert scenario["gold_requirement_ids"] not in prompt, "serialized gold ID set leaked into prompt"

all_ids = sorted(record["id"] for record in records)
schema = module.answer_schema(all_ids)
assert schema["properties"]["predicted_requirement_ids"]["items"]["enum"] == all_ids
assert set(schema["properties"]["predicted_decision"]["enum"]) == {
    "answer", "need_more_information", "human_escalation"
}

print("PASS: LLM benchmark preserves candidate parity, withholds gold fields, and freezes the output schema")
