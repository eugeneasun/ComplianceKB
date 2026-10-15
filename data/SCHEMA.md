# TrusOne-ComplianceKB — Data Dictionary (SCHEMA.md)

**Version:** 1.2.0
**License:** CC-BY-4.0 (data), MIT (code)
**Maintainer:** Eugene Sun · Advisor: Pengdu Liu

This document defines every field in the TrusOne-ComplianceKB dataset, its type, and its allowed values. It is the authoritative reference for anyone reusing the dataset.

---

## Top-level requirement fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique requirement identifier. Format: `{FRAMEWORK}-{NNN}` (e.g., `OSHA-PSM-001`). |
| `requirement_text` | string | Atomic restatement of a single compliance obligation. One independently satisfiable obligation per record. |
| `is_mandatory` | boolean | `true` if the obligation uses SHALL/MUST; `false` for SHOULD/MAY. |
| `requirement_type` | enum | One of: `obligation`, `prohibition`, `permission`, `definition`. |
| `risk_level` | enum | One of: `critical`, `high`, `medium`, `low`. See codebook for decision rules. |
| `verification_method` | enum | How an auditor verifies compliance. One of: `document_review`, `physical_inspection`, `interview`, `record_review`, `observation`. |
| `audit_evidence_type` | enum | **(Novel field)** Type of evidence an auditor requests. See allowed values below. |
| `workflow_trigger` | enum | **(Novel field)** Operational event that surfaces the requirement. See allowed values below. |
| `workflow_trigger_details` | object (optional) | Additional triggers, a numeric recurrence interval, or a condition needed when one scalar trigger would lose legally relevant timing. |
| `verification_status` | enum | Whether the corrected record implements completed human verification or is a newly added record awaiting targeted human verification. |

---

## Applicability sub-object

| Field | Type | Description |
|-------|------|-------------|
| `industry_scope` | enum | `all_covered_industries` when applicability is controlled by the regulation rather than an enumerated NAICS list; otherwise `listed_naics_only`. |
| `industries_naics` | array[int] | NAICS codes used only when `industry_scope=listed_naics_only`. Empty when the regulation applies across all otherwise-covered industries. |
| `industry_condition` | string (optional) | Authoritative non-enumerated industry condition, such as inclusion in a CFR appendix, when a short NAICS list would be incomplete. |
| `business_activities` | array[string] | Controlled vocabulary of operational activities (see below). |
| `employee_size_band` | enum | One of: `1-10`, `11-50`, `20-249`, `51-250`, `250+`, `251+`, `100+`, `any`. The corrected Recordkeeping thresholds use `20-249` and `250+`; `251+` is retained only for backward compatibility with historical data. |
| `jurisdictions` | array[string] | `federal` for CFR; ISO frameworks are not jurisdiction-restricted. |

---

## Provenance sub-object

| Field | Type | Description |
|-------|------|-------------|
| `source_document_id` | string | Internal document identifier (e.g., `CFR-29-1910-119`). |
| `source_framework` | string | Framework code (e.g., `OSHA_PSM`). |
| `source_version` | string | Regulation version date (ISO 8601). |
| `source_clause` | string | Authoritative §-citation (e.g., `§1910.119(d)(2)`). |
| `supporting_clauses` | array[string] (optional) | Additional subparagraphs needed to support a composite restatement when `source_clause` names the primary paragraph. |
| `source_text_excerpt` | string | Verbatim public-domain CFR text (ISO: paraphrase). |
| `source_url` | string (URI) | Canonical eCFR link with section anchor. |
| `source_retrieved_at` | string (ISO 8601) | Datetime the source was retrieved. |
| `source_text_hash` | string | SHA-256 of the normalized excerpt. Enables amendment detection. |
| `curation_method` | enum | `ai_assisted_with_human_review`, `ai_assisted_pending_human_review`, `human_only`, or `human_reviewed`. |
| `curator` | string | Name of the curator who reviewed the record. |
| `review_date` | string (ISO 8601 date) | Date the record was human-reviewed. |

---

## Controlled vocabularies

### `audit_evidence_type` (novel field)
`written_program`, `training_record`, `inspection_record`, `permit`, `physical_condition`, `incident_record`, `certification`, `procedure`, `manifest_or_form`, `safety_data_sheet`, `qualification_record`, `retention_record`, `complaint_record`, `performance_evaluation`

### `workflow_trigger` (novel field)
`onboarding_new_employee`, `chemical_procurement`, `equipment_change`, `annual_review`, `incident_occurrence`, `new_process_startup`, `facility_change`, `regulatory_update`, `audit_preparation`, `permit_renewal`, `always_on`, `job_reassignment`, `process_assignment`, `procedure_change`, `periodic_review`, `training_refresh`, `scheduled_inspection`

### `business_activities`
`chemical_handling`, `confined_space_entry`, `electrical_work`, `equipment_maintenance`, `hazmat_transport`, `hot_work`, `material_storage`, `new_hire_onboarding`, `process_operation`, `waste_disposal`, `welding_cutting`

### NAICS codes
| Code | Sector |
|------|--------|
| 23 | Construction |
| 31 | Manufacturing (food, textile, apparel) |
| 32 | Manufacturing (chemical, plastics, petroleum) |

`28` is not a valid NAICS sector and is no longer permitted as a project-specific chemical grouping. Use an actual NAICS code or `industry_scope=all_covered_industries`.

---

## Amendment detection

The `source_text_hash` field stores the SHA-256 of the normalized source excerpt. To detect whether a regulation has been amended since the dataset freeze (2026-05-01):

1. Re-fetch the source text from `source_url`.
2. Apply the normalization function (see `build_dataset.py::normalize_text`).
3. Compute SHA-256 and compare to the stored `source_text_hash`.
4. A mismatch indicates the underlying regulation text has changed and the record requires review.
