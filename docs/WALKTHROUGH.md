# A source-to-audit walkthrough you can check

This page expands the homepage example using **existing saved research artifacts**. It does not introduce a new model run, new human annotation, or a real facility inspection. The successful case was chosen because its short output makes the field mapping easy to inspect; it is not representative evidence that every case succeeds.

## 1. Scenario and regulatory source

The frozen development scenario **DEV-006** says:

> The anniversary of the last review of a machine-specific energy-control procedure is approaching.

Its stated context is employees servicing equipment where unexpected energization or stored energy could cause injury, under federal OSHA. The scenario is AI-drafted and author-confirmed, with no independent test-set status.

The stored source excerpt in **OSHA-LOTO-005** is:

> The employer shall conduct a periodic inspection of the energy control procedure at least annually to ensure that the procedure and the requirements of this standard are being followed.

Source: [§1910.147(c)(6)(i)](https://www.ecfr.gov/current/title-29/part-1910/section-1910.147#p-1910.147(c)(6)(i)). The stored record reports source version **2024-07-01** and normalized-text SHA-256 **6beaa0d404d1d95f102d5cbc8fd86cfd8a533da77072d1a0c1fe0b0f6cf93504**. The URL opens a current page, which must not be assumed identical to a stored historical version.

## 2. What the reviewed record adds

| Field | Exact released value | Role in a proposed audit |
|---|---|---|
| `id` | `OSHA-LOTO-005` | Stable handle for the requirement |
| `workflow_trigger` | `annual_review` | A reusable event label for retrieval/output comparison |
| `audit_evidence_type` | `inspection_record` | The principal evidence category to propose inspecting |
| `verification_method` | `record_review` | How a reviewer would examine that evidence |
| `verification_status` | `implemented_from_human_verification` | Dataset curation status, not facility compliance status |

Applicability descriptors and provenance are retained in the [complete machine-readable example](../examples/end_to_end_loto.json). These are curated interpretations, not literal field names supplied by OSHA. Neither the source quote nor a label establishes that an inspection happened.

## 3. Actual agent execution and output

The RKM condition uses the stored hybrid retrieval rankings for DEV-006, serializes retrieved records with operational fields, and makes one constrained model call. The saved response used **gpt-5.6-terra**, system **rkm_agent**, prompt SHA-256 **30d2dcb8edb4c829422396c73e46a47868475cfc7806d90c50d400426cf413db**.

The following is a field projection of the [unchanged saved answer](../research/benchmark/runs/llm_development_20260927/openai/rkm_agent/DEV-006.json), not a newly generated illustration:

```json
{
  "predicted_requirement_ids": [
    "OSHA-LOTO-005"
  ],
  "predicted_trigger_labels": [
    "annual_review"
  ],
  "predicted_evidence_labels": [
    "inspection_record"
  ],
  "predicted_citations": [
    "§1910.147(c)(6)(i)"
  ],
  "predicted_decision": "answer"
}
```

The saved rationale connects the approaching anniversary to the annual periodic-inspection requirement. The ID, trigger, evidence, citation and decision match this scenario's reference labels. F1 for each of those single-item sets is `2×1/(1+1) = 1`. This is one selected development example; use the full 24-scenario results for the overall comparison.

## 4. What a person would still need to do

**No actual workplace verification or final compliance confirmation was performed here.** The following checklist describes next steps for a reviewer; it is not part of the saved model response:

1. Confirm that the equipment, task and energy-control procedure fall within the applicable regulatory scope and exceptions.
2. Inspect the actual periodic-inspection evidence, its date, coverage and provenance; check the full clause and related requirements.
3. Confirm the inspection was actually performed and any deficiencies addressed; a stored source or model answer cannot establish this.
4. Record any missing information and make or escalate the site-specific judgment. No workplace verification was performed in this synthetic example.


In particular, `predicted_decision = answer` means the model returned a response rather than requesting information or escalating under the benchmark policy. It does not mean "compliant," "inspection passed," or "human approved."

## A contrasting failure: correct evidence type, wrong requirements

In **DEV-002**, a technician is newly assigned to a PSM-covered process. The reference requirements are **OSHA-PSM-016** and **OSHA-PSM-018**. The [saved GPT RKM answer](../research/benchmark/runs/llm_development_20260927/openai/rkm_agent/DEV-002.json) instead returns **OSHA-HAZCOM-007** and **OSHA-HAZCOM-016**. It recovers `training_record` as an evidence category but misses the reference PSM requirement IDs.

The two requirement sets have no overlap, so requirement F1 is `2×0/(2+2) = 0`. This is a reference-label mismatch, not a claim that no HazCom requirement could ever apply. It demonstrates why recovering a useful evidence label or returning `answer` is insufficient to certify the whole output. The original outputs remain unchanged.

## Inspect or reproduce

- [Source-linked walkthrough JSON](../examples/end_to_end_loto.json)
- [Frozen scenario CSV](../research/benchmark/scenarios_HUMAN_CONFIRMED_DEVELOPMENT.csv)
- [Saved hybrid rankings](../research/benchmark/runs/retrieval_provisional/hybrid_predictions.jsonl)
- [Prompt/context construction](../research/benchmark/run_llm_benchmark.py)
- [Scoring functions](../research/benchmark/evaluate_benchmark.py)
- [Dataset card and limitations](DATASET_CARD.md)

```bash
python tools/demo.py --query "annual energy control inspection"
python tests/test_readme_walkthrough.py
python tools/reproduce.py
```

The CLI demo is retrieval-only; it does not replay a paid model call or establish a site-specific result. Offline reproduction checks the saved artifacts against their reported scores.
