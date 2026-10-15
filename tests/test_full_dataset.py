#!/usr/bin/env python3
"""
Full-dataset CI test: JSON Schema validation + integrity checks for ALL frameworks.
(Supersedes test_provenance.py which covered PSM only.)
Run: python3 tests/test_full_dataset.py
"""
import json
import sys
import argparse
import hashlib
import re
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

with open("data/requirement.schema.json") as f:
    SCHEMA = json.load(f)

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"[^\w\s§.()\-]", "", text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", default="v1.2.0")
    args = parser.parse_args()
    path = Path("data/releases") / args.release / "all_requirements.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    recs = data["requirements"]
    errors = []

    ids = set()
    hashes = {}
    for r in recs:
        # 1. Formal schema validation
        if jsonschema is not None:
            try:
                jsonschema.validate(r, SCHEMA)
            except jsonschema.ValidationError as e:
                errors.append(f"{r.get('id','?')}: schema — {e.message[:100]}")
                continue
        else:
            required = SCHEMA["required"]
            missing = [field for field in required if field not in r]
            if missing:
                errors.append(f"{r.get('id','?')}: missing required fields {missing}")
                continue
            for field in ("requirement_type", "risk_level", "verification_method", "audit_evidence_type", "workflow_trigger", "verification_status"):
                allowed = SCHEMA["properties"][field].get("enum", [])
                if allowed and r.get(field) not in allowed:
                    errors.append(f"{r['id']}: invalid {field}={r.get(field)!r}")
            for field in SCHEMA["properties"]["applicability"]["required"]:
                if field not in r["applicability"]:
                    errors.append(f"{r['id']}: missing applicability.{field}")
            for field in SCHEMA["properties"]["provenance"]["required"]:
                if field not in r["provenance"]:
                    errors.append(f"{r['id']}: missing provenance.{field}")
        # 2. Unique IDs
        if r["id"] in ids:
            errors.append(f"{r['id']}: duplicate id")
        ids.add(r["id"])
        # 3. Clause consistency: URL anchor must contain the clause reference
        clause_anchor = r["provenance"]["source_clause"].replace("§", "")
        if clause_anchor not in r["provenance"]["source_url"]:
            errors.append(f"{r['id']}: URL anchor does not match source_clause")
        # 4. Hash uniqueness sanity (same excerpt -> same hash is OK, but flag exact dupes)
        h = r["provenance"]["source_text_hash"]
        expected_hash = hashlib.sha256(normalize_text(r["provenance"]["source_text_excerpt"]).encode("utf-8")).hexdigest()
        if h != expected_hash:
            errors.append(f"{r['id']}: source_text_hash does not match normalized excerpt")
        if h in hashes and hashes[h] != r["provenance"]["source_clause"]:
            errors.append(f"{r['id']}: identical excerpt hash as {hashes[h]} — check for copy-paste")
        hashes[h] = r["provenance"]["source_clause"]
        # 5. Applicability semantics introduced in v1.2.0.
        a = r["applicability"]
        if a["industry_scope"] == "all_covered_industries" and a["industries_naics"]:
            errors.append(f"{r['id']}: all_covered_industries must not carry a restrictive NAICS list")
        if a["industry_scope"] == "listed_naics_only" and not a["industries_naics"] and not a.get("industry_condition"):
            errors.append(f"{r['id']}: listed_naics_only needs codes or an industry_condition")

    if errors:
        print(f"FAILED — {len(errors)} issue(s):")
        for e in errors:
            print(f"   {e}")
        sys.exit(1)
    fw = {}
    for r in recs:
        fw[r["provenance"]["source_framework"]] = fw.get(r["provenance"]["source_framework"], 0) + 1
    mode = "jsonschema" if jsonschema is not None else "built-in schema checks"
    print(f"PASSED — {len(recs)} records in {args.release}, all valid under {mode}, with unique IDs, consistent URLs and hashes.")
    for k, v in sorted(fw.items()):
        print(f"   {k}: {v}")

if __name__ == "__main__":
    main()
