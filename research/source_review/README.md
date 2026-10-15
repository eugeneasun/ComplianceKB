# Source review and documented corrections

`original_89_review_dispositions.csv` is a selected projection of the original 89-record author review. It retains record IDs, source references and structured judgments about citation, excerpt, requirement text, atomicity, applicability, trigger and evidence. It excludes the reviewer's identity, private notes, pasted full-page text and free-text proposed corrections.

**These are historical findings before the v1.2.0 corrections, not the current failure status of v1.2.0 records.** The results were 22 PASS, 6 PASS_WITH_NOTE and 61 FAIL_NEEDS_CORRECTION. Multiple failed rows shared framework-level causes; the 61 dispositions are not 61 independent errors.

## Corrections incorporated into v1.2.0

The source implementation report records these correction categories:

- Replaced unsupported restrictive NAICS filtering for HazCom and Recordkeeping with explicit all-covered-industry scope.
- Removed construction NAICS 23 from LOTO and invalid NAICS/SIC value 28 from PSM.
- Added industry-scope distinctions, narrative conditions, recurring trigger details and supporting regulatory clauses.
- Corrected affected citations and stored excerpts and preserved material actors, conditions, exceptions, timing and cross-references.
- Separated independently auditable requirements and expanded trigger/evidence vocabularies where needed.
- Corrected the electronic-submission threshold recorded as `251+` to `250+`, with the applicable child-paragraph citation.

The original 89 IDs were retained. Ten PSM and nine Recordkeeping records received targeted author review, producing the 108-record v1.2.0 release. Among those 19 initial review dispositions were 17 PASS, one PASS_WITH_NOTE and one FAIL_NEEDS_CORRECTION. The last concerned OSHA-PSM-050's missing cross-reference to §1910.119(f)(4), which was incorporated into the corrected record. The note concerned overlapping but separately retained summary/posting requirements.

This is an English summary of the recorded implementation report and a projection of actual historical review fields, not a fresh independent legal audit or a complete per-edit provenance ledger. The private original workbook and free-text corrections are not distributed. Readers can inspect the [corrected release](../../data/releases/v1.2.0/) and the separate [independent annotation analysis](../annotation/).

Presence of review artifacts does not establish exhaustive regulatory coverage. Current-day legal or safety use still requires source-version, exception, applicability and site-evidence checks.
