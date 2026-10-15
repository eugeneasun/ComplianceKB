#!/usr/bin/env python3
"""Validate benchmark scenario structure without supplying or inventing gold labels."""

import argparse
import csv
from pathlib import Path


REQUIRED = [
    "scenario_id", "scenario_text", "organization_context", "task_types", "gold_requirement_ids",
    "gold_trigger_labels", "gold_evidence_labels", "gold_citations", "gold_decision", "gold_rationale",
    "scenario_author", "gold_verifier", "source_basis", "split", "generation_method", "leakage_notes",
]
VALID_DECISIONS = {"answer", "need_more_information", "human_escalation"}
VALID_SPLITS = {"development", "test"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenarios", type=Path)
    args = parser.parse_args()
    with args.scenarios.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != REQUIRED:
            raise SystemExit("Scenario columns do not match the frozen template")
        rows = list(reader)
    if not rows:
        raise SystemExit("Scenario file contains no benchmark rows")
    ids = [r["scenario_id"].strip() for r in rows]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise SystemExit("scenario_id values must be non-empty and unique")
    for row in rows:
        missing = [field for field in REQUIRED if field != "leakage_notes" and not row[field].strip()]
        if missing:
            raise SystemExit(f"{row['scenario_id']}: missing {missing}")
        if row["gold_decision"] not in VALID_DECISIONS:
            raise SystemExit(f"{row['scenario_id']}: invalid gold_decision")
        if row["split"] not in VALID_SPLITS:
            raise SystemExit(f"{row['scenario_id']}: invalid split")
    print(f"PASS: {len(rows)} benchmark scenarios satisfy the structural protocol")


if __name__ == "__main__":
    main()
