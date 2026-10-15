# ComplianceKB

**Source-linked OSHA requirements, operational audit fields, and documented human verification for compliance AI.**

ComplianceKB means **Compliance Knowledge Base**. It implements a Regulatory Knowledge Model (RKM) that connects a regulatory requirement—what an employer must do—to its scope, official source, activating event, expected evidence, and human review history.

**Eugene Sun and Dupeng Liu · Research conducted during a TrusOne internship.**

**Upcoming presentation:** accepted for poster presentation at **AIAS+ 2026 — Chen Institute Symposium for AI Advancing Science and Society**; preparing to present this work at the symposium. **Publication status:** the revised manuscript is under publication-eligibility review for possible inclusion in the **ACM International Conference Proceedings Series (ICPS)**. Proceedings publication is not yet confirmed. ICPS is a conference-proceedings series, not a journal. [Status and sources](docs/PUBLICATION_STATUS.md).


**[Read the full paper](paper/ComplianceKB_Manuscript.pdf)** · [Poster](poster/ComplianceKB_ESS_2026.pdf) · [Example record](examples/training_record.json) · [Reproduce the results](docs/REPRODUCIBILITY.md) · [Dataset card](docs/DATASET_CARD.md) · [Methods and limits](docs/METHODS.md)

## Why this resource

The focus is the **combination of a reusable dataset and an inspectable review process**, rather than a claim that OSHA knowledge bases or regulatory AI are new.

- **Four-framework scope:** selected requirements from PSM, HazCom, Recordkeeping, and LOTO; not complete coverage of all four regulations.
- **From source to proposed check:** each record links a specific regulatory source to applicability descriptions, a workflow trigger, an evidence category, and a verification method.
- **Visible verification artifacts:** author source review and documented corrections, frozen releases, and an independent second annotator's unadjudicated agreement results.

In our targeted review of the public resources documented in [Related resources and positioning](docs/RELATED_RESOURCES.md), we did not identify a dataset covering selected requirements across these four OSHA frameworks that combines all of those operational fields with documented source review, corrections, and annotation-agreement artifacts. ComplianceKB explores this combination as a reusable knowledge resource for human-supervised compliance AI.

This is a bounded search finding, not a claim to be the first or only such resource. Related OSHA datasets, regulatory knowledge graphs, and enterprise compliance models already exist; individual field types are not claimed as unique. [Inspect the source-review record](research/source_review/) and [paired annotation results](research/annotation/).

## Start here

1. Open the [training-record example](examples/training_record.json). Follow `provenance.source_url` to inspect the regulatory source.
2. Compare `requirement_text`, `workflow_trigger`, and `audit_evidence_type`: these connect a source passage to a proposed audit check.
3. Run the offline checks below. No API key, model download, or paid call is required.

```bash
python tools/check_release.py
python tools/demo.py --query "employee training records"
python tools/reproduce.py
```

Run these commands from this repository's root with Python 3.12 or later. The offline checks use only the Python standard library. For formal JSON Schema validation, install the optional development dependency in `requirements-dev.txt`.

## What this contributes

- **Knowledge infrastructure:** reviewed, source-linked records make regulatory interpretations inspectable and reusable across queries.
- **An explicit AI workflow:** retrieval selects records; one constrained model call proposes requirement IDs, operational labels, citations, and an answer / request-for-information / escalation decision.
- **A representation benchmark:** compare excerpt-only contexts with richer RKM records using the same models and, for hybrid versus RKM, the same candidate IDs.
- **Separate verification layers:** structural checks, author source review, independent annotation, and output scoring test different claims instead of treating any one score as legal correctness.

The implemented agent is a bounded proposal-generation workflow, not an autonomous compliance auditor or a multi-step action-taking system.

## Dataset versions: do not mix them

| Release | Records | Role |
|---|---:|---|
| **v1.2.0** | **108** | Frozen dataset used in the reported benchmark and independent-label analysis |
| v1.3.0 | 113 | Later coverage-audit additions |
| v1.4.0 | 131 | Further coverage-audit additions |
| **v1.5.0** | **133** | Latest included extension; not evaluated by the reported model experiment |

The v1.2.0 corpus covers PSM (55 records), HazCom (16), Recordkeeping (26), and LOTO (11). It contains 103 obligations, 3 prohibitions, and 2 permissions. A later, larger dataset does not retroactively enlarge the paper's experiment.

Read the [release notes](docs/RELEASES.md). Each version includes JSON, CSV, JSON-LD and SQL exports and a file-hash manifest. Source data files retain their original bytes.

## Reported exploratory experiment

**24 AI-assisted, author-confirmed development scenarios × 5 input conditions × 2 models = 240 saved responses.**

| Model | Context | Requirement F1 | Trigger F1 | Evidence F1 | Decision accuracy |
|---|---|---:|---:|---:|---:|
| GPT-5.6-terra | Hybrid | .801 | .693 | .681 | .917 |
| GPT-5.6-terra | RKM | .789 | .824 | .838 | .917 |
| Claude Sonnet 5 | Hybrid | .745 | .628 | .544 | .958 |
| Claude Sonnet 5 | RKM | .771 | .858 | .888 | .958 |

RKM improves agreement with reference **trigger and evidence labels** in these paired comparisons. Requirement identification and citation scores do not improve consistently; final decision accuracy is unchanged. This does not establish real-world legal correctness, calibrated safety, or reduced human labor.

The full five-condition results, saved answers, retrieval rankings, and paired-bootstrap outputs are in [`research/benchmark/runs/`](research/benchmark/runs/). BM25, MiniLM dense retrieval, reciprocal-rank hybrid retrieval, and a separate post-hoc E5 sensitivity analysis are included.

**Important:** these are development results, not independent holdout findings. Scenarios share the RKM label taxonomy, and RKM includes additional information and context tokens. Candidate parity does not isolate formatting as the cause of gains.

## Human verification

- All 108 v1.2.0 records received author source review with AI assistance.
- The 24 development scenarios were author-confirmed; they were not independently authored or independently verified test cases.
- A second annotator labeled 50 retained IDs from the original 89-record pool. Unadjudicated nominal Cohen's κ: **risk .234; evidence .642; trigger .443**.

These agreement scores expose ambiguity; they are not certificates of expert correctness. Labels were not revised to improve agreement. [Paired labels and results](research/annotation/) and the [frozen English codebook](docs/annotation_codebook.md) are included without reviewers' correspondence or personal review notes.

## Structure

```text
data/releases/           Frozen datasets and later extensions
docs/                    Methods, dataset card, release notes and reproducibility
examples/                One source-linked record
paper/                   Full submission manuscript PDF
poster/                  ESS poster PDF
research/annotation/     Anonymized paired labels and reported agreement
research/benchmark/      Retrieval, prompt construction, scoring and saved outputs
tests/                   Selected implementation and integrity checks
tools/                   Offline demo, integrity checks and reproduction entry point
```

## Scope and safety

The model's record structure can be applied to other regulatory domains in principle; only OSHA examples were evaluated here. Applicability fields are descriptive, not an executable legal rule engine. Excerpt hashes support integrity checks and change detection; they do not prove that a source is authoritative, current, complete, or correctly interpreted. No temporal regulatory graph or temporal-reasoning evaluation is claimed.

People must verify site facts, regulatory applicability and exceptions, evidence authenticity, and final compliance judgments. This is a research prototype, not legal advice or a deployed safety-critical decision system.

## Presentation and publication status

Prepared for the Berkeley Engineering Undergraduate Research Poster Session, October 15, 2026, and for the accepted AIAS+ 2026 poster presentation at the Chen Institute Symposium for AI Advancing Science and Society. The revised manuscript is awaiting the publication-eligibility review outcome for possible ACM ICPS proceedings inclusion; this is not an ACM journal acceptance or a confirmed proceedings publication. AIAS+ and the Chen Institute symposium refer to the same event, not two independent speaking engagements. See [publication status and sources](docs/PUBLICATION_STATUS.md).

The [full submission manuscript](paper/ComplianceKB_Manuscript.pdf) is shared by the authors for readers who want the complete method and results. It retains its original anonymous submission title page; the project homepage and poster identify the authors. Reviewer correspondence and the response letter are not distributed.

## Licenses and attribution

- **Code:** existing [MIT license](LICENSE-CODE.txt), copyright TrusOne, Inc.
- **Dataset and annotations:** existing [CC BY 4.0 terms](LICENSE-DATA.txt); cite the specific version used. Federal regulatory source text retains its original public-domain status.
- **Poster and third-party visuals:** see [NOTICE](NOTICE.md). The code/data licenses do not grant rights to Berkeley branding or third-party assets.

See [`CITATION.cff`](CITATION.cff). This attributed research release is shared at the repository owner’s request; it is not a publisher version of record.

## Share this project

Project homepage: **https://github.com/eugeneasun/ComplianceKB**

Share the homepage link or scan the [project QR code](sharing/ComplianceKB_QR.png). The homepage offers the full paper, poster, example record, datasets and offline reproduction instructions. GitHub's **Code → Download ZIP** downloads the repository. **[Releases](https://github.com/eugeneasun/ComplianceKB/releases)** provide packaged snapshots; the main branch contains the latest project introduction and documentation.
