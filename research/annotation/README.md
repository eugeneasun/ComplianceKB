# Independent annotation: frozen, unadjudicated results

`paired_labels.csv` contains the same 50 IDs and the two sets of three labels used in the reported analysis. Annotators are identified only as 1 and 2. Names, correspondence, and free-text review notes are excluded. Source clauses and official URLs remain for inspection.

The source completed CSV's eighth header was accidentally `always_on`; analysis treated the eighth data column as `ann2_workflow_trigger`. No label was changed. The normalized public CSV uses the intended explicit column names. `reported_results.json` preserves original source-file hashes, the repair description, confusion matrices, marginal distributions, and reported confidence intervals.

| Field | Exact agreement | Nominal Cohen's kappa | Bootstrap 95% interval |
|---|---:|---:|---|
| Risk | 23/50 (46%) | .234 | [.048, .418] |
| Evidence | 34/50 (68%) | .642 | [.491, .775] |
| Trigger | 29/50 (58%) | .443 | [.269, .605] |

These results are not adjudicated ground truth. Risk was scored nominally, not with weighted ordinal kappa. The 50 retained IDs originate in the old 89-record sample frame and are not a new random sample of all 108 records. Follow the codebook for the intended original annotation procedure; use the paired file only for retrospective analysis, not for a new blinded exercise.
