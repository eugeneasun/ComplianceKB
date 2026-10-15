#!/usr/bin/env python3
"""Run reproducible, resumable provisional LLM/agent benchmark calls.

Every response is persisted immediately. The runner enforces a per-provider
cost ceiling and never prints API keys. Results remain provisional until the
scenario mappings receive independent human verification.
"""

import argparse
import csv
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRIGGERS = [
    "onboarding_new_employee", "process_assignment", "job_reassignment", "training_refresh",
    "chemical_procurement", "equipment_change", "procedure_change", "facility_change",
    "new_process_startup", "incident_occurrence", "annual_review", "periodic_review",
    "scheduled_inspection", "audit_preparation", "permit_renewal", "regulatory_update", "always_on",
]
EVIDENCE = [
    "written_program", "procedure", "training_record", "qualification_record",
    "performance_evaluation", "inspection_record", "permit", "physical_condition",
    "incident_record", "complaint_record", "certification", "manifest_or_form",
    "safety_data_sheet", "retention_record",
]
SYSTEMS = ["raw_full", "bm25", "dense", "hybrid", "rkm_agent"]
PROVIDERS = {
    "openai": {
        "model": "gpt-5.6-terra",
        "input_per_million": 2.0,
        "output_per_million": 12.0,
    },
    "anthropic": {
        "model": "claude-sonnet-5",
        "input_per_million": 2.0,
        "output_per_million": 10.0,
    },
}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def post_json(url, headers, body, timeout=180):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response), len(data)


def answer_schema(all_ids):
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "predicted_requirement_ids": {"type": "array", "items": {"type": "string", "enum": all_ids}},
            "predicted_trigger_labels": {"type": "array", "items": {"type": "string", "enum": TRIGGERS}},
            "predicted_evidence_labels": {"type": "array", "items": {"type": "string", "enum": EVIDENCE}},
            "predicted_citations": {"type": "array", "items": {"type": "string"}},
            "predicted_decision": {"type": "string", "enum": ["answer", "need_more_information", "human_escalation"]},
            "rationale": {"type": "string"},
            "missing_information_or_escalation_reason": {"type": "string"},
        },
        "required": [
            "predicted_requirement_ids", "predicted_trigger_labels", "predicted_evidence_labels",
            "predicted_citations", "predicted_decision", "rationale",
            "missing_information_or_escalation_reason",
        ],
    }


def official_entry(record):
    provenance = record["provenance"]
    return (
        f"[{record['id']}] {provenance['source_clause']}\n"
        f"Official excerpt: {provenance['source_text_excerpt']}\n"
        f"Source: {provenance['source_url']}"
    )


def rkm_entry(record):
    provenance = record["provenance"]
    return json.dumps({
        "id": record["id"],
        "requirement_text": record["requirement_text"],
        "is_mandatory": record["is_mandatory"],
        "requirement_type": record["requirement_type"],
        "risk_level": record["risk_level"],
        "audit_evidence_type": record["audit_evidence_type"],
        "workflow_trigger": record["workflow_trigger"],
        "applicability": record["applicability"],
        "source_clause": provenance["source_clause"],
        "source_url": provenance["source_url"],
        "source_text_excerpt": provenance["source_text_excerpt"],
        "source_text_hash": provenance["source_text_hash"],
    }, ensure_ascii=False, sort_keys=True)


def build_context(system_name, records, rankings, scenario_id):
    by_id = {record["id"]: record for record in records}
    if system_name == "raw_full":
        selected = records
        return "\n\n".join(official_entry(record) for record in selected), [r["id"] for r in selected]
    retrieval_system = "hybrid" if system_name == "rkm_agent" else system_name
    ranked_ids = rankings[retrieval_system][scenario_id]
    selected = [by_id[record_id] for record_id in ranked_ids]
    formatter = rkm_entry if system_name == "rkm_agent" else official_entry
    return "\n\n".join(formatter(record) for record in selected), ranked_ids


def build_prompt(system_name, scenario, context):
    representation = (
        "structured, human-verified ComplianceKB records" if system_name == "rkm_agent"
        else "authoritative regulatory excerpts without operational labels"
    )
    return f"""You are evaluating a compliance-reasoning system. Use only the supplied context. Do not rely on unstated facts.

System condition: {system_name}
Available representation: {representation}

Scenario:
{scenario['scenario_text']}

Organization context:
{scenario['organization_context']}

Tasks:
{scenario['task_types']}

Decision policy:
- answer: supplied facts and context support a determinate response.
- need_more_information: a material factual predicate is missing; identify it.
- human_escalation: supplied facts conflict or require qualified legal, safety, or engineering judgment.

Return only the required JSON object. Select only requirements supported by the scenario. Return exact source_clause strings in predicted_citations. Do not treat every retrieved item as applicable.

Context:
{context}
"""


def call_openai(prompt, schema, model):
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": "Perform source-grounded regulatory reasoning and follow the JSON schema exactly."},
            {"role": "user", "content": prompt},
        ],
        "reasoning": {"effort": "low"},
        "max_output_tokens": 2000,
        "text": {"format": {"type": "json_schema", "name": "compliance_answer", "strict": True, "schema": schema}},
    }
    headers = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}
    raw, request_bytes = post_json("https://api.openai.com/v1/responses", headers, body)
    texts = []
    for item in raw.get("output", []):
        for block in item.get("content", []):
            if block.get("type") == "output_text":
                texts.append(block.get("text", ""))
    answer = json.loads("".join(texts))
    usage = raw.get("usage", {})
    return raw, answer, usage.get("input_tokens", 0), usage.get("output_tokens", 0), request_bytes


def call_anthropic(prompt, schema, model):
    body = {
        "model": model,
        "max_tokens": 2000,
        "system": "Perform source-grounded regulatory reasoning and follow the JSON schema exactly.",
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"effort": "low", "format": {"type": "json_schema", "schema": schema}},
    }
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    raw, request_bytes = post_json("https://api.anthropic.com/v1/messages", headers, body)
    texts = [block.get("text", "") for block in raw.get("content", []) if block.get("type") == "text"]
    answer = json.loads("".join(texts))
    usage = raw.get("usage", {})
    input_tokens = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
    return raw, answer, input_tokens, usage.get("output_tokens", 0), request_bytes


def cost(provider, input_tokens, output_tokens):
    rates = PROVIDERS[provider]
    return input_tokens / 1_000_000 * rates["input_per_million"] + output_tokens / 1_000_000 * rates["output_per_million"]


def duplicate_output_items(answer):
    duplicates = {}
    for field in [
        "predicted_requirement_ids", "predicted_trigger_labels",
        "predicted_evidence_labels", "predicted_citations",
    ]:
        values = answer.get(field, [])
        repeated = sorted({value for value in values if values.count(value) > 1})
        if repeated:
            duplicates[field] = repeated
    return duplicates


def run_one(provider, system_name, scenario, prompt, schema, output_dir):
    model = PROVIDERS[provider]["model"]
    call = call_openai if provider == "openai" else call_anthropic
    started = time.time()
    last_error = None
    for attempt in range(1, 4):
        try:
            raw, answer, input_tokens, output_tokens, request_bytes = call(prompt, schema, model)
            result = {
                "status": "ok",
                "provider": provider,
                "model": model,
                "system": system_name,
                "scenario_id": scenario["scenario_id"],
                "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
                "request_bytes": request_bytes,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost_usd": cost(provider, input_tokens, output_tokens),
                "elapsed_seconds": time.time() - started,
                "attempts": attempt,
                "duplicate_output_items": duplicate_output_items(answer),
                "answer": answer,
                "raw_response": raw,
            }
            path = output_dir / provider / system_name / f"{scenario['scenario_id']}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return result
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
            detail = str(exc)
            if isinstance(exc, urllib.error.HTTPError):
                detail += " " + exc.read().decode("utf-8", "replace")[:2000]
            last_error = f"{type(exc).__name__}: {detail}"
            if attempt < 3:
                time.sleep(2 ** attempt)
    result = {
        "status": "error", "provider": provider, "model": model, "system": system_name,
        "scenario_id": scenario["scenario_id"], "error": last_error,
        "elapsed_seconds": time.time() - started,
    }
    path = output_dir / provider / system_name / f"{scenario['scenario_id']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenarios", type=Path, default=HERE / "scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv")
    parser.add_argument("--retrieval-dir", type=Path, default=HERE / "runs" / "retrieval_provisional")
    parser.add_argument("--output-dir", type=Path, default=HERE / "runs" / "llm_provisional")
    parser.add_argument("--providers", nargs="+", choices=sorted(PROVIDERS), default=sorted(PROVIDERS))
    parser.add_argument("--systems", nargs="+", choices=SYSTEMS, default=SYSTEMS)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--budget-per-provider", type=float, default=9.50)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    dataset_path = ROOT / "data" / "releases" / "v1.2.0" / "all_requirements.json"
    records = json.loads(dataset_path.read_text(encoding="utf-8"))["requirements"]
    all_ids = sorted(record["id"] for record in records)
    schema = answer_schema(all_ids)
    with args.scenarios.open(encoding="utf-8-sig", newline="") as stream:
        scenarios = list(csv.DictReader(stream))
    if args.limit:
        scenarios = scenarios[: args.limit]

    rankings = {}
    for name in ["bm25", "dense", "hybrid"]:
        rankings[name] = {}
        path = args.retrieval_dir / f"{name}_predictions.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            rankings[name][row["scenario_id"]] = row["ranked_requirement_ids"]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "HUMAN_CONFIRMED_AI_ASSISTED_DEVELOPMENT_RUN_NOT_INDEPENDENT_CONFIRMATORY",
        "scenario_file": str(args.scenarios).replace("\\", "/"),
        "scenario_sha256": sha256_bytes(args.scenarios.read_bytes()),
        "dataset_sha256": sha256_bytes(dataset_path.read_bytes()),
        "providers": {name: PROVIDERS[name] for name in args.providers},
        "systems": args.systems,
        "reasoning_effort": "low",
        "temperature": "not set; unsupported/non-comparable on selected current reasoning models",
        "max_output_tokens": 2000,
        "workers": args.workers,
        "budget_per_provider_usd": args.budget_per_provider,
        "prompting": "zero-shot, identical decision policy and output schema; context varies by system condition",
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    for provider in args.providers:
        existing_cost = 0.0
        for path in (args.output_dir / provider).glob("*/*.json") if (args.output_dir / provider).exists() else []:
            try:
                existing_cost += json.loads(path.read_text(encoding="utf-8")).get("estimated_cost_usd", 0.0)
            except json.JSONDecodeError:
                pass
        jobs = []
        for system_name in args.systems:
            for scenario in scenarios:
                output_path = args.output_dir / provider / system_name / f"{scenario['scenario_id']}.json"
                if output_path.exists() and json.loads(output_path.read_text(encoding="utf-8")).get("status") == "ok":
                    continue
                context, _ = build_context(system_name, records, rankings, scenario["scenario_id"])
                prompt = build_prompt(system_name, scenario, context)
                conservative_next_call = len(prompt.encode("utf-8")) / 4 / 1_000_000 * PROVIDERS[provider]["input_per_million"] + 2000 / 1_000_000 * PROVIDERS[provider]["output_per_million"]
                if existing_cost + conservative_next_call > args.budget_per_provider:
                    break
                jobs.append((system_name, scenario, prompt))
            else:
                continue
            break
        print(f"{provider}: starting {len(jobs)} pending calls; recorded cost before run ${existing_cost:.4f}")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(run_one, provider, system_name, scenario, prompt, schema, args.output_dir) for system_name, scenario, prompt in jobs]
            for future in as_completed(futures):
                result = future.result()
                if result["status"] == "ok":
                    existing_cost += result["estimated_cost_usd"]
                    print(provider, result["system"], result["scenario_id"], f"${result['estimated_cost_usd']:.4f}", f"total=${existing_cost:.4f}")
                else:
                    print(provider, result["system"], result["scenario_id"], "ERROR", result["error"][:200])
        if existing_cost > args.budget_per_provider:
            raise SystemExit(f"Budget guard exceeded for {provider}: ${existing_cost:.4f}")


if __name__ == "__main__":
    main()
