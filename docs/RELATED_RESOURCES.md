# Related resources and bounded positioning

**Targeted public-resource review date: October 14, 2026.**

## What we looked for

The comparison concerns a particular combination, not the existence of OSHA datasets or knowledge graphs in general:

1. A populated dataset of selected requirements spanning PSM, HazCom, Recordkeeping and LOTO.
2. Requirement-level source references plus applicability descriptions, workflow triggers, audit-evidence categories and verification methods.
3. Inspectable documentation of source review and correction, together with independent second-person annotation-agreement analysis.

In a targeted review of the public resources listed below, we did not identify a dataset for which all three conditions could be confirmed together. This is not evidence that no such resource exists. It is not a systematic review, an exhaustive search, or a priority claim.

## Public resources examined

| Resource | What the inspected public material supports | Boundary of this comparison |
|---|---|---|
| [SmartQHSE HSE Q&A Open Corpus v2 2026](https://huggingface.co/datasets/SmartQHSE/hse-qa-corpus-v2-2026) | An openly licensed occupational-safety Q&A corpus; the displayed rows include OSHA topics such as PSM and LOTO. | The inspected page presents Q&A entries and categories. We did not confirm the complete requirement-level operational-field and review/agreement-artifact combination above. This is not a claim that its answers are incorrect or that no further artifacts exist elsewhere. |
| [Wang & El-Gohary (2023), Deep learning-based relation extraction and knowledge graph-based representation of construction safety requirements](https://doi.org/10.1016/j.autcon.2022.104696) | A published method for extracting and representing OSHA fall-protection relations as knowledge-graph queries; evaluated on 20 OSHA sections. | Its reported fall-protection scope differs from the four-framework requirement resource studied here. It establishes relevant prior work; OSHA knowledge representation is not new in itself. |
| [Databricks construction data model: enterprise construction management](https://github.com/databricks-industry-solutions/lakehouse-industry-data-models/blob/main/data-models/construction/v2/ecm/readme.md) | A regulatory-obligation register model includes sources, jurisdiction/scope, ownership, review frequency and required compliance evidence. | Similar compliance fields already exist. The inspected model documentation does not establish the full populated four-framework dataset plus the specific source-review and independent-agreement artifacts above. |
| [HazComFast developer page](https://hazcomfast.com/developers) | Its indexed developer description advertises OSHA reference data in JSON and plain text. The full page could not be retrieved during this review. | A potentially relevant lead, not a verified negative comparison. The full field structure, framework scope and review artifacts could not be checked. It is therefore not used as evidence of absence. |

The publisher's [Wang & El-Gohary abstract and article page](https://www.sciencedirect.com/science/article/pii/S0926580522005660) and the authors' [university publication record](https://experts.illinois.edu/en/publications/deep-learning-based-relation-extraction-and-knowledge-graph-based/) support the paper description. This comparison does not assert that every underlying code/data supplement was inspected.

## Search scope and limits

The targeted queries included:

- `OSHA dataset PSM HazCom Recordkeeping LOTO workflow trigger audit evidence provenance annotation`
- `S0926580522005660 Wang El-Gohary 2023 OSHA fall protection knowledge graph`
- `site.huggingface.co/datasets/SmartQHSE/hse-qa-corpus-v2-2026`

We also inspected the specific publisher, dataset-card and repository pages linked above. This search has no pre-registered systematic-review protocol, exhaustive database coverage, quantitative search recall, or complete supplement audit. A missing feature in the inspected description is recorded as **not confirmed**, not as proof that the feature is absent.

## Reusable wording

> In our targeted review of the public resources documented here, we did not identify a dataset covering selected requirements across PSM, HazCom, Recordkeeping and LOTO that combines source-linked operational fields with documented source review, corrections and independent annotation-agreement artifacts. ComplianceKB explores this combination as a reusable knowledge resource for human-supervised compliance AI.

Do not shorten this to "the first OSHA knowledge base," "the only OSHA dataset," or "complete coverage of four OSHA regulations." New discoveries should update this comparison rather than be excluded to preserve a novelty claim.

## What ComplianceKB makes inspectable

- [Versioned records](../data/releases/): source links, excerpts, descriptive scope, triggers, evidence and verification methods.
- [Source-review projection and correction summary](../research/source_review/): historical record-level review flags, without personal reviewer notes.
- [Independent paired labels and results](../research/annotation/): unchanged labels and the unadjudicated agreement analysis.
- [Saved exploratory evaluation](../research/benchmark/runs/): retrieved IDs, model outputs and recomputable scores.

This combination is the project focus; it is not a claim that each individual field, model component, or review statistic is a new invention. Source review was author-performed with AI assistance, not an independent legal-expert certification. The second annotation tests label consistency and does not independently certify every regulatory interpretation.
