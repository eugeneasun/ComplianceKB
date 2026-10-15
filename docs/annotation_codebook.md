# TrusOne-ComplianceKB IRR Annotation Codebook

**Version:** 1.2.0  
**Status:** Approved and frozen on 2026-09-27 for IRR-A  
**Fields:** `risk_level`, `audit_evidence_type`, `workflow_trigger`

## General procedure

For each sampled record, read the requirement text, official source excerpt, citation, and source URL. Assign each field independently. Do not inspect the released database label or another annotator's answer. Use `ann2_notes` for genuine ambiguity; do not use it as a substitute for selecting a label.

## Risk level

Classify the consequence of non-compliance with the stated duty, rather than the general hazard of the regulated process.

| Value | Decision rule |
|---|---|
| `critical` | Non-compliance can directly leave a substantial probability of death or serious physical harm, including failure of a required major hazard-control step. |
| `high` | Significant compliance failure affecting a safety control, written program, training, or readiness, without the direct consequence threshold used for `critical`. |
| `medium` | Administrative, documentation, access, retention, reporting, or procedural duty whose violation does not itself create an immediate severe hazard. |
| `low` | Narrow posting, definitional, applicability, or limited administrative duty with comparatively low direct consequence. |

Tie-breaker: when a record is specifically a documentation duty about a hazardous process, classify the duty expressed in the record. Use `medium` unless the absence of that document itself defeats an immediate safety control.

## Audit evidence type

Choose the principal artifact or observable condition that most directly demonstrates the stated duty.

| Value | Decision rule |
|---|---|
| `written_program` | Formal policy, plan, or program describing what the organization will do. |
| `procedure` | Written operational steps describing how an activity is performed. |
| `training_record` | Record showing training, instruction, attendance, content, or completion. |
| `qualification_record` | Record establishing competence, qualification, or authorization. |
| `performance_evaluation` | Recorded evaluation of performance or effectiveness. |
| `inspection_record` | Completed inspection, examination, or test record. |
| `permit` | Completed authorization for a controlled activity. |
| `physical_condition` | Directly observable equipment, label, posting, access condition, or workplace state. |
| `incident_record` | Injury, illness, release, or incident report or log. |
| `complaint_record` | Complaint, retaliation, or employee-rights case record. |
| `certification` | Signed or otherwise attributable certification of completion or accuracy. |
| `manifest_or_form` | Required regulatory form, submission, log form, or manifest. |
| `safety_data_sheet` | Safety data sheet required or maintained for a chemical. |
| `retention_record` | Evidence that required material was retained for the specified period. |

Tie-breakers:

1. Choose `procedure` for required step-by-step operating procedures and `written_program` for a higher-level plan or program.
2. Choose `training_record` for proof that instruction occurred and `qualification_record` when the duty is to establish competence or qualification.
3. Choose the evidence explicitly required by the source. If the source does not name an artifact, choose the evidence that directly demonstrates the duty and explain a close call in `ann2_notes`.

## Workflow trigger

Choose the principal event or state that activates the duty.

| Value | Decision rule |
|---|---|
| `onboarding_new_employee` | A person joins the organization and must receive initial information or training. |
| `process_assignment` | A person is first assigned to a covered process or work area. |
| `job_reassignment` | A person's job or covered duties change. |
| `training_refresh` | Refresher or repeat training becomes due. |
| `chemical_procurement` | A new chemical or hazard is introduced or acquired. |
| `equipment_change` | Equipment is installed, modified, replaced, or retired. |
| `procedure_change` | An operating, safety, or work procedure changes. |
| `facility_change` | The physical facility changes. |
| `new_process_startup` | A new or materially changed covered process is prepared for startup. |
| `incident_occurrence` | An injury, illness, release, near miss, or other specified incident occurs. |
| `annual_review` | The duty recurs once per calendar year or at year end. |
| `periodic_review` | The duty recurs on a non-annual interval or as often as necessary. |
| `scheduled_inspection` | A required inspection, examination, or test becomes due. |
| `audit_preparation` | A compliance audit or certification review is initiated or due. |
| `permit_renewal` | A permit reaches its renewal or expiry point. |
| `regulatory_update` | The governing regulation changes. |
| `always_on` | The obligation is continuous or has no discrete activating event. |

Multiple-trigger rule: select the trigger stated most directly in the requirement text. If two triggers are equally explicit, select the first trigger in the authoritative provision and list the others in `ann2_notes`.

## Completion rule

Every sampled row must contain all three labels. The annotator must complete all 50 rows before seeing the annotator-1 key or discussing individual answers. Adjudication happens only after the unadjudicated Cohen's kappa and percent agreement are computed and preserved.
