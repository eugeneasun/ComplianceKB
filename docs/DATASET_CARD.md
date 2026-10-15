# Dataset card

## Purpose and origin

ComplianceKB structures selected independently auditable requirements from four OSHA frameworks: 29 CFR 1910.119 (PSM), 1910.1200 (HazCom), 1910.147 (LOTO), and Part 1904 (Recordkeeping). It is not a complete representation of U.S. industrial law or every obligation in those frameworks.

Source passages were converted into draft records with AI assistance, reviewed by the author against regulatory sources, corrected, and exported into versioned releases. The audit trail distinguished source support, applicability, requirement granularity, activating conditions, and expected evidence. The original 89-record review recorded 22 PASS, 6 PASS_WITH_NOTE and 61 FAIL_NEEDS_CORRECTION dispositions; these are not 61 independent extraction errors. The corrected experimental release includes 108 records after targeted additions and review.

## Record fields

| Field | Interpretation |
|---|---|
| `id` | Stable record identifier |
| `requirement_text` | Curated statement of what must, must not, or may be done |
| `requirement_type`, `is_mandatory` | Modality of the statement |
| `risk_level` | Curated consequence category; not a calibrated probability |
| `applicability` | Descriptive scope, industry conditions, and jurisdiction |
| `workflow_trigger` | Principal activating event or state |
| `audit_evidence_type` | Principal artifact or condition to inspect |
| `verification_method` | How the proposed evidence would be examined |
| `provenance` | Clause, URL, stored excerpt, version/date, normalized-text hash, and curation metadata |
| `verification_status` | Recorded review disposition; not a legal certification |

The [schema](../data/requirement.schema.json) and [data dictionary](../data/SCHEMA.md) describe the machine-readable structure. Stable IDs and source hashes serve different purposes: a stable ID identifies a record; a hash fingerprints its stored normalized excerpt.

## Versions and representativeness

Use v1.2.0 to reproduce the paper. Later releases extend the corpus but have no corresponding 240-call evaluation. Coverage-audit candidates were selected for ongoing, independently auditable requirements; some narrow exceptions, trade-secret provisions, one-time classification tasks and passive response duties were excluded. No probabilistic population sampling or exhaustive coverage claim follows from these record counts.

Dates and regulatory versions are recorded per item. Opening a present-day official page does not prove that its content matches the historical version stored with the record. New legal or safety use requires a fresh source and applicability review.

## Independent annotation

The second annotator used the frozen codebook to assign one primary risk, evidence and trigger label per sampled record without viewing the first annotator's labels. The 50 IDs were retained from the earlier seeded sample of the original 89-record pool. Do not describe this as a newly drawn stratified sample of all 108 records.

The completed file accidentally named the eighth header `always_on`; its 50 values remained in the workflow-trigger column. Analysis repaired that header in memory by position without altering labels. The public paired-label projection uses explicit column names and excludes free-text reviewer notes and identities. Original input hashes are recorded in the results JSON for lineage.

## Appropriate uses and limits

Appropriate uses include representation research, retrieval experiments, output-label comparison and studying human review boundaries. Unsupported uses include autonomous compliance certification, calibrated risk prediction, claiming measured labor savings, and extrapolating results to other jurisdictions without validation.
