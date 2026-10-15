#!/usr/bin/env python3
"""Cross-format integrity checks for a release export."""

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", default="v1.2.0")
    args = parser.parse_args()
    release_dir = Path("data/releases") / args.release

    canonical = json.loads((release_dir / "all_requirements.json").read_text(encoding="utf-8"))
    records = canonical["requirements"]
    ids = [r["id"] for r in records]
    assert len(ids) == len(set(ids))

    with (release_dir / "requirements.csv").open(encoding="utf-8-sig", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    assert [r["id"] for r in csv_rows] == ids
    assert all(r["industry_scope"] for r in csv_rows)
    assert sum(r["verification_status"] == "pending_human_verification" for r in csv_rows) == 0

    jsonld = json.loads((release_dir / "requirements.jsonld").read_text(encoding="utf-8"))
    graph = jsonld["@graph"]
    assert [r["id"].removeprefix("trus:") for r in graph] == ids
    assert all("workflow_trigger_details" in r and "industry_scope" in r for r in graph)

    db = sqlite3.connect(":memory:")
    db.executescript((release_dir / "requirements.sql").read_text(encoding="utf-8"))
    sql_rows = db.execute(
        "SELECT id, requirement_text, industry_scope, verification_status FROM requirement ORDER BY rowid"
    ).fetchall()
    assert [r[0] for r in sql_rows] == ids
    assert [r[1] for r in sql_rows] == [r["requirement_text"] for r in records]
    assert all(r[2] in {"all_covered_industries", "listed_naics_only"} for r in sql_rows)
    assert sum(r[3] == "pending_human_verification" for r in sql_rows) == 0
    manifest_lines = (release_dir / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
    manifest = dict(line.split("  ", 1)[::-1] for line in manifest_lines)
    for name, expected in manifest.items():
        assert hashlib.sha256((release_dir / name).read_bytes()).hexdigest() == expected
    print(f"PASS: {len(ids)} records agree across JSON, CSV, JSON-LD, and SQL")


if __name__ == "__main__":
    main()
